// Reuse retained v0.1 implementation bytes unchanged. Its private handle remains
// private in this successor module; no Serialize/Deserialize or handle exporter.
include!("../../checked_roundtrip_reuse/src/checked_roundtrip.rs");

#[derive(Serialize)]
pub(super) struct NativeReport {
    pub(super) outcome: &'static str,
    native_profile_binding: Option<Binding>,
    setup: Work,
    limits: Limits,
    stages: Vec<Stage>,
    uses: Vec<UseRecord>,
    total: Work,
    retained_artifacts: Vec<WitnessArtifactV0>,
    failure: Option<Failure>,
}

#[derive(Debug)]
pub(super) struct SourceBinding {
    pub(super) digest: Option<String>,
    pub(super) bytes: usize,
    pub(super) operations: u32,
    pub(super) failure: Option<Failure>,
}

pub(super) fn retained_binding(operations: u32, bytes: usize) -> SourceBinding {
    let mut meter = Meter::new();
    meter.limits.operations = meter.limits.operations.min(operations);
    meter.limits.bytes = meter.limits.bytes.min(bytes);
    let result = binding(&evidence(), &mut meter);
    SourceBinding {
        digest: result
            .as_ref()
            .ok()
            .map(|value| value.checker_build_digest.clone()),
        bytes: meter.spent.bytes,
        operations: meter.spent.operations,
        failure: result.err(),
    }
}

pub(super) fn run_received(
    raw: &super::intake::RawEvidence,
    context: &super::intake::ReceiverBinding,
    depth_limit: Option<usize>,
    values: [[i32; 3]; 2],
) -> NativeReport {
    run_received_with_meters(
        raw,
        context,
        depth_limit,
        values,
        Meter::new(),
        Meter::new(),
    )
}

fn run_received_with_meters(
    raw: &super::intake::RawEvidence,
    context: &super::intake::ReceiverBinding,
    depth_limit: Option<usize>,
    values: [[i32; 3]; 2],
    mut setup: Meter,
    mut meter: Meter,
) -> NativeReport {
    // The strict intake has checked the fixed primitive proof graph. Build the
    // exact native expressions from its received literal endpoints, never from
    // a stored native artifact, serialized summary, or producer verdict.
    fn expression(token: &str) -> ExactExprV0 {
        let p = ExactExprV0::sum(
            ExactExprV0::variable("x"),
            ExactExprV0::product(ExactExprV0::variable("y"), ExactExprV0::variable("z")),
        );
        match token {
            "x+y*z" => p,
            "2*(x+y*z)" => ExactExprV0::product(ExactExprV0::constant(2), p),
            _ => unreachable!("strict primitive intake validated the endpoint"),
        }
    }
    fn boundary(raw: &[i32; 3]) -> BoundaryChargeV0 {
        BoundaryChargeV0::from_terms(
            [RoleV0::Construction, RoleV0::Space, RoleV0::Time]
                .into_iter()
                .zip(raw)
                .map(|(role, coefficient)| {
                    BoundaryTermV0::new(BoundaryCoordinateV0::Role { role }, *coefficient)
                }),
        )
        .expect("strict fixed three-role boundary")
    }
    let edges = raw.history.transitions.each_ref().map(|raw| Edge {
        actual: boundary(&raw.actual),
        declared: boundary(&raw.declared),
        before: expression(&raw.before),
        after: expression(&raw.after),
    });
    let input = Evidence {
        forward: edges[0].clone(),
        reverse: edges[1].clone(),
        guards: raw.guards.iter().map(|s| expression(s)).collect(),
    };
    let expected = match binding(&input, &mut setup) {
        Ok(expected) => expected,
        Err(failure) => {
            return NativeReport {
                outcome: failure.outcome,
                native_profile_binding: None,
                setup: setup.spent,
                limits: Limits::default(),
                stages: vec![],
                uses: vec![],
                total: Work::default(),
                retained_artifacts: failure.retained_artifacts.clone(),
                failure: Some(failure),
            };
        }
    };
    if let Some(depth) = depth_limit {
        meter.limits.depth = depth;
    }
    let mut stages = Vec::new();
    let mut uses = Vec::new();
    let mut retained_artifacts = Vec::new();
    let result = (|| {
        let mut checked = first_check(&input, &expected, &mut meter)?;
        retained_artifacts = checked.artifacts.clone();
        record_stage(&mut stages, "first_check", &meter.spent);
        // Receiver custody binds the entire independently supplied receiving
        // context in addition to the unchanged native v0.1 binding on every use.
        let custody = context.clone();
        for values in values {
            meter.tick(0)?;
            meter.require(&custody == context, "receiver cache custody changed")?;
            let hit = checked.hit(&expected, &mut meter)?;
            record_stage(&mut stages, "cache_hit", &meter.spent);
            uses.push(hit.fresh_use(values, &mut meter)?);
            retained_artifacts = checked.artifacts.clone();
            record_stage(&mut stages, "fresh_use", &meter.spent);
        }
        Ok(())
    })();
    let failure = result.err().map(|mut failure: Failure| {
        if failure.retained_artifacts.is_empty() {
            failure.retained_artifacts = retained_artifacts.clone();
        }
        retained_artifacts = failure.retained_artifacts.clone();
        failure
    });
    NativeReport {
        outcome: failure
            .as_ref()
            .map_or("LocalCheckedAndUsed", |f| f.outcome),
        native_profile_binding: Some(expected),
        setup: setup.spent,
        limits: meter.limits,
        stages,
        uses,
        total: meter.spent,
        retained_artifacts,
        failure,
    }
}

impl fmt::Debug for NativeReport {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("NativeReport")
            .field("outcome", &self.outcome)
            .field("total", &self.total)
            .finish_non_exhaustive()
    }
}

#[cfg(test)]
mod intake_failure_tests {
    use super::*;
    fn context() -> super::super::intake::ReceiverBinding {
        serde_json::from_slice(&super::super::intake::emit_binding().unwrap()).unwrap()
    }
    #[test]
    fn exhausted_native_setup_returns_structured_unknown() {
        let mut setup = Meter::new();
        setup.limits.operations = 0;
        let report = run_received_with_meters(
            &super::super::intake::fixture(),
            &context(),
            None,
            [[2, 3, 4]; 2],
            setup,
            Meter::new(),
        );
        assert_eq!(report.outcome, "Unknown");
        assert!(report.native_profile_binding.is_none());
        assert_eq!(report.setup.operations, 0);
        assert!(report.failure.is_some());
    }
    #[test]
    fn exhausted_pre_hit_account_retains_checked_prefix() {
        let raw = super::super::intake::fixture();
        let context = context();
        let reference = run_received(&raw, &context, None, [[2, 3, 4]; 2]);
        let first_check_operations = reference.stages[0].cumulative.operations;
        let mut meter = Meter::new();
        meter.limits.operations = first_check_operations;
        let report =
            run_received_with_meters(&raw, &context, None, [[2, 3, 4]; 2], Meter::new(), meter);
        assert_eq!(report.outcome, "Unknown");
        assert_eq!(report.retained_artifacts.len(), 8);
        assert_eq!(report.failure.unwrap().retained_artifacts.len(), 8);
        assert_eq!(report.total.operations, first_check_operations);
        assert_eq!(report.total.requested_uses, 0);
    }
}
