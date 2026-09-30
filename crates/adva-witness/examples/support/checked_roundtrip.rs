use adva_lisp::{compile_function, link_modules, parse_module};
use adva_witness::{
    ArtifactKeyV0, BindingOriginV0, BoundaryChargeV0, BoundaryCoordinateV0, BoundaryTermV0,
    CellTemplateV0, ExactExprV0, FormedCellV0, HoleBindingV0, HoleSpecV0, InstanceIdV0, RoleV0,
    TemplateIdV0, TermGlyphV0, WitnessArtifactV0, WitnessProofV0, WitnessStoreV0, WitnessSummaryV0,
};
use num_bigint::BigInt;
use serde::Serialize;
use std::collections::BTreeSet;
use std::fmt;
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::{Duration, Instant};

const PROFILE: &str = "adva.checked-roundtrip-reuse.v0";
const MAX_RECORD: usize = 128 * 1024;
static NEXT_CONTEXT: AtomicU64 = AtomicU64::new(0);
type Result<T> = std::result::Result<T, Failure>;

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
struct Binding {
    profile: String,
    judgment: String,
    interpretation: String,
    premises: Vec<String>,
    evidence_digest: String,
    checker_build_digest: String,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
struct Edge {
    actual: BoundaryChargeV0,
    declared: BoundaryChargeV0,
    before: ExactExprV0,
    after: ExactExprV0,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
struct Evidence {
    forward: Edge,
    reverse: Edge,
    guards: Vec<ExactExprV0>,
}

fn evidence() -> Evidence {
    let p = ExactExprV0::sum(
        ExactExprV0::variable("x"),
        ExactExprV0::product(ExactExprV0::variable("y"), ExactExprV0::variable("z")),
    );
    let q = ExactExprV0::product(ExactExprV0::constant(2), p.clone());
    let boundary = BoundaryChargeV0::from_terms([
        BoundaryTermV0::new(
            BoundaryCoordinateV0::Role {
                role: RoleV0::Construction,
            },
            1,
        ),
        BoundaryTermV0::new(
            BoundaryCoordinateV0::Role {
                role: RoleV0::Space,
            },
            1,
        ),
        BoundaryTermV0::new(BoundaryCoordinateV0::Role { role: RoleV0::Time }, 1),
    ])
    .expect("fixed boundary");
    Evidence {
        forward: Edge {
            actual: boundary.clone(),
            declared: boundary.clone(),
            before: p.clone(),
            after: q.clone(),
        },
        reverse: Edge {
            actual: boundary.clone(),
            declared: boundary,
            before: q.clone(),
            after: p.clone(),
        },
        guards: vec![p.clone(), q.clone(), q, p],
    }
}

#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize)]
struct Work {
    operations: u32,
    bytes: usize,
    encoded_bytes_observed: usize,
    proof_insert_calls: u32,
    template_checks: u32,
    cache_hit_checks: u32,
    compilations: u32,
    instantiations: u32,
    executions: u32,
    requested_uses: u32,
    peak_proof_nodes: usize,
    peak_proof_edges: usize,
    peak_proof_depth: usize,
    peak_evidence_bytes: usize,
}

#[derive(Clone, Debug, Serialize)]
struct Limits {
    operations: u32,
    bytes: usize,
    uses: u32,
    nodes: usize,
    edges: usize,
    depth: usize,
    evidence_bytes: usize,
    cooperative_millis: u64,
}
impl Default for Limits {
    fn default() -> Self {
        Self {
            operations: 256,
            bytes: 8 * 1024 * 1024,
            uses: 2,
            nodes: 16,
            edges: 32,
            depth: 4,
            evidence_bytes: MAX_RECORD,
            cooperative_millis: 30_000,
        }
    }
}

#[derive(Clone, Debug, Serialize)]
pub(super) struct Failure {
    outcome: &'static str,
    reason: String,
    spent: Box<Work>,
    retained_artifacts: Vec<WitnessArtifactV0>,
}
impl fmt::Display for Failure {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.outcome, self.reason)
    }
}
impl std::error::Error for Failure {}

enum NativeCall {
    ProofInsert,
    Template,
    Compile,
    Instantiate,
    Execute,
}

struct Meter {
    limits: Limits,
    spent: Work,
    start: Instant,
    stopped: bool,
}
impl Meter {
    fn new() -> Self {
        Self {
            limits: Limits::default(),
            spent: Work::default(),
            start: Instant::now(),
            stopped: false,
        }
    }
    fn failure(&self, outcome: &'static str, reason: impl Into<String>) -> Failure {
        Failure {
            outcome,
            reason: reason.into(),
            spent: Box::new(self.spent.clone()),
            retained_artifacts: vec![],
        }
    }
    fn require(&self, condition: bool, reason: &str) -> Result<()> {
        if condition {
            Ok(())
        } else {
            Err(self.failure("Rejected", reason))
        }
    }
    fn tick(&mut self, bytes: usize) -> Result<()> {
        if self.stopped
            || self.spent.operations >= self.limits.operations
            || bytes > self.limits.bytes.saturating_sub(self.spent.bytes)
            || self.start.elapsed() >= Duration::from_millis(self.limits.cooperative_millis)
        {
            self.stopped = true;
            return Err(self.failure("Unknown", "cumulative operation, byte or time limit"));
        }
        self.spent.operations += 1;
        self.spent.bytes += bytes;
        Ok(())
    }
    fn native<T, E: fmt::Display>(
        &mut self,
        kind: NativeCall,
        operation: impl FnOnce() -> std::result::Result<T, E>,
    ) -> Result<T> {
        self.tick(0)?;
        match kind {
            NativeCall::ProofInsert => self.spent.proof_insert_calls += 1,
            NativeCall::Template => self.spent.template_checks += 1,
            NativeCall::Compile => self.spent.compilations += 1,
            NativeCall::Instantiate => self.spent.instantiations += 1,
            NativeCall::Execute => self.spent.executions += 1,
        }
        let result = operation();
        if let Err(mut failure) = self.tick(0) {
            if let Err(error) = &result {
                failure
                    .reason
                    .push_str(&format!("; native call also returned: {error}"));
            }
            return Err(failure);
        }
        result.map_err(|error| self.failure("Rejected", error.to_string()))
    }

    fn encode<T: Serialize>(&mut self, value: &T) -> Result<Vec<u8>> {
        self.tick(0)?;
        let bytes = serde_json::to_vec(value)
            .map_err(|error| self.failure("Rejected", error.to_string()))?;
        self.spent.encoded_bytes_observed += bytes.len();
        if bytes.len() > MAX_RECORD {
            self.stopped = true;
            return Err(self.failure("Unknown", "encoded record size limit"));
        }
        self.tick(bytes.len())?;
        Ok(bytes)
    }
    fn request_use(&mut self) -> Result<()> {
        self.tick(0)?;
        if self.spent.requested_uses >= self.limits.uses {
            self.stopped = true;
            return Err(self.failure("Unknown", "two-use lifetime exhausted; no continuation"));
        }
        self.spent.requested_uses += 1;
        Ok(())
    }
    fn storage(&mut self, artifacts: &[WitnessArtifactV0]) -> Result<()> {
        let nodes = artifacts.len();
        let edges: usize = artifacts.iter().map(|a| a.proof.dependencies().len()).sum();
        let mut depths = std::collections::BTreeMap::new();
        for artifact in artifacts {
            let depth = artifact
                .proof
                .dependencies()
                .into_iter()
                .map(|key| depths.get(key).copied().unwrap_or(usize::MAX / 2))
                .max()
                .unwrap_or(0)
                + 1;
            depths.insert(artifact.key.clone(), depth);
        }
        let depth = depths.values().copied().max().unwrap_or(0);
        let bytes = self.encode(&artifacts)?.len();
        self.spent.peak_proof_nodes = self.spent.peak_proof_nodes.max(nodes);
        self.spent.peak_proof_edges = self.spent.peak_proof_edges.max(edges);
        self.spent.peak_proof_depth = self.spent.peak_proof_depth.max(depth);
        self.spent.peak_evidence_bytes = self.spent.peak_evidence_bytes.max(bytes);
        if nodes > self.limits.nodes
            || edges > self.limits.edges
            || depth > self.limits.depth
            || bytes > self.limits.evidence_bytes
        {
            self.stopped = true;
            return Err(self.failure(
                "Unknown",
                "proof node, edge, depth or evidence-storage limit",
            ));
        }
        Ok(())
    }
}

fn digest(bytes: &[u8]) -> String {
    blake3::hash(bytes).to_hex().to_string()
}

fn binding(input: &Evidence, meter: &mut Meter) -> Result<Binding> {
    let mut hash = blake3::Hasher::new();
    macro_rules! source {
        ($path:literal) => {{
            let bytes = include_bytes!($path);
            meter.tick(bytes.len())?;
            hash.update(($path.len() as u64).to_le_bytes().as_slice());
            hash.update($path.as_bytes());
            hash.update((bytes.len() as u64).to_le_bytes().as_slice());
            hash.update(bytes);
        }};
    }
    source!("checked_roundtrip.rs");
    source!("../checked_roundtrip_reuse.rs");
    source!("../../../../docs/kpb/checked-roundtrip-reuse-v0.md");
    source!("../../../../Cargo.lock");
    source!("../../../../Cargo.toml");
    source!("../../Cargo.toml");
    source!("../../src/lib.rs");
    source!("../../src/witness.rs");
    source!("../../src/arithmetic.rs");
    source!("../../src/boundary.rs");
    source!("../../src/seed.rs");
    source!("../../../adva-ir/Cargo.toml");
    source!("../../../adva-ir/src/certificate.rs");
    source!("../../../adva-ir/src/diagram.rs");
    source!("../../../adva-ir/src/graft.rs");
    source!("../../../adva-ir/src/ids.rs");
    source!("../../../adva-ir/src/lib.rs");
    source!("../../../adva-ir/src/numeric_serialization.rs");
    source!("../../../adva-ir/src/process.rs");
    source!("../../../adva-ir/src/term.rs");
    source!("../../../adva-lisp/Cargo.toml");
    source!("../../../adva-lisp/src/compile.rs");
    source!("../../../adva-lisp/src/eval.rs");
    source!("../../../adva-lisp/src/lib.rs");
    source!("../../../adva-lisp/src/module.rs");
    source!("../../../adva-lisp/src/operation.rs");
    source!("../../../adva-lisp/src/parser.rs");
    source!("../../../adva-lisp/src/process.rs");
    source!("../../../adva-lisp/src/validate.rs");
    Ok(Binding {
        profile: PROFILE.into(),
        judgment: "formed p->q->p; M=1; concrete execution requires all retained guards".into(),
        interpretation: "exact research V0 arithmetic; no PSC0 equality or general inverse".into(),
        premises: vec![
            "literal fixed endpoints and three-role boundary".into(),
            "canonical Unit/Construction/Space/Time seeds".into(),
            "same-process Rust compiler, dependencies and platform trusted".into(),
        ],
        evidence_digest: digest(&meter.encode(input)?),
        checker_build_digest: hash.finalize().to_hex().to_string(),
    })
}

// No Clone, Serialize, Deserialize or public constructor: native custody is local.
#[derive(Debug)]
struct Checked {
    binding: Binding,
    evidence: Evidence,
    store: WitnessStoreV0,
    formed: FormedCellV0,
    children: [ArtifactKeyV0; 3],
    artifacts: Vec<WitnessArtifactV0>,
    occurrences: BTreeSet<(
        adva_ir::QualifiedName,
        adva_ir::SourceId,
        adva_ir::OccurrenceId,
    )>,
    namespace: u64,
    next_use: u32,
}

fn insert(
    store: &mut WitnessStoreV0,
    artifacts: &mut Vec<WitnessArtifactV0>,
    proof: WitnessProofV0,
    meter: &mut Meter,
) -> Result<ArtifactKeyV0> {
    let mut inserted = None;
    let result = meter.native(NativeCall::ProofInsert, || {
        let result = store.insert(proof);
        if let Ok(key) = &result {
            inserted = store.artifact(key).cloned();
        }
        result
    });
    if let Some(artifact) = inserted {
        artifacts.push(artifact);
    }
    let key = result?;
    meter.storage(artifacts)?;
    Ok(key)
}

fn first_check(input: &Evidence, expected: &Binding, meter: &mut Meter) -> Result<Checked> {
    let mut artifacts = Vec::new();
    first_check_inner(input, expected, meter, &mut artifacts).map_err(|mut failure| {
        failure.retained_artifacts = artifacts;
        failure
    })
}

fn first_check_inner(
    input: &Evidence,
    expected: &Binding,
    meter: &mut Meter,
    artifacts: &mut Vec<WitnessArtifactV0>,
) -> Result<Checked> {
    meter.tick(0)?;
    meter.require(
        input.forward.after == input.reverse.before && input.forward.before == input.reverse.after,
        "disconnected literal roundtrip endpoints",
    )?;
    meter.require(
        input.forward.actual == input.forward.declared
            && input.reverse.actual == input.reverse.declared,
        "unformed child boundary",
    )?;
    meter.require(
        input == &evidence(),
        "unsupported fixed evidence or missing/changed guards",
    )?;
    let input_digest = digest(&meter.encode(input)?);
    meter.require(
        expected.evidence_digest == input_digest,
        "evidence digest mismatch",
    )?;
    let actual = binding(input, meter)?;
    meter.require(
        expected == &actual,
        "checker/profile/premise/interpretation binding mismatch",
    )?;
    let mut store = WitnessStoreV0::new();
    let mut seeds = Vec::new();
    for term in [
        TermGlyphV0::Unit,
        TermGlyphV0::Construction,
        TermGlyphV0::Space,
        TermGlyphV0::Time,
    ] {
        seeds.push(insert(
            &mut store,
            artifacts,
            WitnessProofV0::Seed { term },
            meter,
        )?);
    }
    let mut transitions = Vec::new();
    for edge in [&input.forward, &input.reverse] {
        transitions.push(insert(
            &mut store,
            artifacts,
            WitnessProofV0::ArithmeticTransition {
                actual_boundary: edge.actual.clone(),
                declared_boundary: edge.declared.clone(),
                before: edge.before.clone(),
                after: edge.after.clone(),
            },
            meter,
        )?);
    }
    let composed = insert(
        &mut store,
        artifacts,
        WitnessProofV0::Compose {
            left: transitions[0].clone(),
            connector: seeds[0].clone(),
            right: transitions[1].clone(),
        },
        meter,
    )?;
    meter.require(
        store
            .artifact(&composed)
            .expect("inserted")
            .summary
            .nonzero_obligations
            == input.guards,
        "native guard ledger differs",
    )?;
    let sealed = insert(
        &mut store,
        artifacts,
        WitnessProofV0::Seal { body: composed },
        meter,
    )?;
    let holes = [
        (RoleV0::Construction, "x"),
        (RoleV0::Space, "y"),
        (RoleV0::Time, "z"),
    ];
    let formed = meter.native(NativeCall::Template, || {
        CellTemplateV0::new(
            TemplateIdV0::new(PROFILE)?,
            std::array::from_fn(|index| HoleSpecV0 {
                index: index as u8,
                role: holes[index].0,
                variable: holes[index].1.into(),
            }),
            input.forward.before.clone(),
            sealed,
        )?
        .form(&store)
    })?;
    let namespace = NEXT_CONTEXT
        .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |id| id.checked_add(1))
        .map_err(|_| meter.failure("Unknown", "process context counter exhausted"))?;
    Ok(Checked {
        binding: actual,
        evidence: input.clone(),
        store,
        formed,
        children: [seeds[1].clone(), seeds[2].clone(), seeds[3].clone()],
        artifacts: artifacts.clone(),
        occurrences: BTreeSet::new(),
        namespace,
        next_use: 0,
    })
}

#[derive(Debug)]
struct Hit<'a> {
    checked: &'a mut Checked,
}
impl Checked {
    fn hit<'a>(&'a mut self, expected: &Binding, meter: &mut Meter) -> Result<Hit<'a>> {
        let result = (|| {
            meter.request_use()?;
            meter.tick(0)?;
            meter.spent.cache_hit_checks += 1;
            meter.require(&self.binding == expected, "cache context mismatch")?;
            let input_digest = digest(&meter.encode(&self.evidence)?);
            meter.require(
                input_digest == expected.evidence_digest,
                "cache evidence mismatch",
            )?;
            Ok(())
        })();
        result.map_err(|mut failure: Failure| {
            failure.retained_artifacts = self.artifacts.clone();
            failure
        })?;
        Ok(Hit { checked: self })
    }
}

#[derive(Clone, Debug, Serialize)]
struct UseRecord {
    outcome: &'static str,
    values: [i32; 3],
    value: String,
    instance: InstanceIdV0,
    artifact: ArtifactKeyV0,
    program: adva_ir::QualifiedName,
    local_cache_context: u64,
    bindings: [HoleBindingV0; 3],
    origin: BindingOriginV0,
    summary: WitnessSummaryV0,
}
impl Hit<'_> {
    fn fresh_use(mut self, values: [i32; 3], meter: &mut Meter) -> Result<UseRecord> {
        self.fresh_use_inner(values, meter).map_err(|mut failure| {
            failure.retained_artifacts = self.checked.artifacts.clone();
            failure
        })
    }
    fn fresh_use_inner(&mut self, values: [i32; 3], meter: &mut Meter) -> Result<UseRecord> {
        meter.tick(0)?;
        meter.require(
            values.iter().all(|v| (-16..=16).contains(v)),
            "input outside [-16,16]",
        )?;
        let checked = &mut self.checked;
        meter.require(checked.next_use < 2, "cache lifetime exhausted")?;
        let module_name = format!("checked_reuse_{}_{}", checked.namespace, checked.next_use);
        checked.next_use += 1;
        let source = format!(
            "(module {module_name} (export pass) (def pass (fn ((x Real) (y Real) (z Real)) (outputs Real Real Real) (frontier (use x) (use y) (use z)))))"
        );
        meter.tick(source.len())?;
        let compilation = meter.native(NativeCall::Compile, || {
            let module = parse_module(&source).map_err(|e| e.to_string())?;
            let linked = link_modules(vec![module]).map_err(|e| e.to_string())?;
            compile_function(&linked, &module_name, "pass").map_err(|e| e.to_string())
        })?;
        let mut instance_artifact = None;
        let instance_result = meter.native(NativeCall::Instantiate, || {
            let result = checked.formed.instantiate_from_graft(
                &mut checked.store,
                &compilation,
                &compilation.graft_trace.result.root,
                checked.children.clone(),
            );
            if let Ok(instance) = &result {
                instance_artifact = checked.store.artifact(&instance.artifact).cloned();
            }
            result
        });
        if let Some(artifact) = instance_artifact {
            if !checked.artifacts.iter().any(|a| a.key == artifact.key) {
                checked.artifacts.push(artifact);
            }
        }
        let instance = instance_result?;
        for binding in &instance.bindings {
            meter.require(
                checked.occurrences.insert((
                    instance.program.clone(),
                    binding.source.clone(),
                    binding.occurrence.clone(),
                )),
                "reused native occurrence",
            )?;
        }
        let artifact = checked
            .store
            .artifact(&instance.artifact)
            .expect("native instance")
            .clone();
        if !checked.artifacts.iter().any(|a| a.key == artifact.key) {
            checked.artifacts.push(artifact.clone());
        }
        meter.storage(&checked.artifacts)?;
        meter.require(
            artifact.summary.nonzero_obligations == checked.evidence.guards,
            "fresh instance lost retained guards",
        )?;
        let executed = meter.native(NativeCall::Execute, || {
            instance.execute(&checked.store, values.map(BigInt::from))
        })?;
        let record = UseRecord {
            outcome: "ScopedExecutionChecked",
            values,
            value: executed.value.to_string(),
            instance: instance.id,
            artifact: instance.artifact,
            program: instance.program,
            local_cache_context: checked.namespace,
            bindings: instance.bindings,
            origin: instance.binding_origin,
            summary: artifact.summary,
        };
        meter.encode(&record)?;
        Ok(record)
    }
}

#[derive(Serialize)]
struct Stage {
    operations_delta: u32,
    bytes_delta: usize,
    phase: &'static str,
    cumulative: Work,
}
fn record_stage(stages: &mut Vec<Stage>, phase: &'static str, spent: &Work) {
    let previous = stages
        .last()
        .map(|s| s.cumulative.clone())
        .unwrap_or_default();
    stages.push(Stage {
        phase,
        operations_delta: spent.operations - previous.operations,
        bytes_delta: spent.bytes - previous.bytes,
        cumulative: spent.clone(),
    });
}
#[derive(Serialize)]
struct Control {
    limits: Limits,
    name: &'static str,
    input: Evidence,
    expected: Binding,
    values: Option<[i32; 3]>,
    failure: Failure,
}
#[derive(Serialize)]
struct Route {
    limits: Limits,
    stages: Vec<Stage>,
    uses: Vec<UseRecord>,
    total: Work,
}
#[derive(Serialize)]
pub(super) struct Report {
    schema: &'static str,
    binding: Binding,
    setup: Work,
    full_replay: Route,
    checked_cache: Route,
    negative_controls: Vec<Control>,
    residuals: Vec<&'static str>,
}
fn route(input: &Evidence, expected: &Binding, cached: bool) -> Result<Route> {
    let mut meter = Meter::new();
    let mut stages = Vec::new();
    let mut uses = Vec::new();
    let mut checked = None;
    for values in [[2, 3, 4], [5, 2, 3]] {
        if checked.is_none() || !cached {
            drop(checked.take());
            checked = Some(first_check(input, expected, &mut meter)?);
            record_stage(&mut stages, "first_check", &meter.spent);
        }
        let checked = checked.as_mut().expect("first checked");
        let hit = if cached {
            checked.hit(expected, &mut meter)?
        } else {
            meter.request_use()?;
            Hit { checked }
        };
        record_stage(
            &mut stages,
            if cached { "cache_hit" } else { "replay_ready" },
            &meter.spent,
        );
        uses.push(hit.fresh_use(values, &mut meter)?);
        record_stage(&mut stages, "fresh_use", &meter.spent);
    }
    Ok(Route {
        limits: meter.limits,
        stages,
        uses,
        total: meter.spent,
    })
}

pub(super) fn compare() -> Result<Report> {
    let input = evidence();
    let mut setup = Meter::new();
    let expected = binding(&input, &mut setup)?;
    let full_replay = route(&input, &expected, false)?;
    let checked_cache = route(&input, &expected, true)?;
    for (replay, cache) in full_replay.uses.iter().zip(&checked_cache.uses) {
        setup.require(
            replay.values == cache.values
                && replay.value == cache.value
                && replay.summary == cache.summary,
            "replay/cache judgment mismatch",
        )?;
        setup.require(
            replay.bindings != cache.bindings,
            "independent routes collapsed occurrences",
        )?;
    }
    Ok(Report {
        schema: PROFILE,
        binding: expected.clone(),
        setup: setup.spent,
        full_replay,
        checked_cache,
        negative_controls: controls(&input, &expected)?,
        residuals: vec![
            "same-process local custody only; no serialized authority or general cut checker",
            "native compiler, dependency artifacts, Rust toolchain and OS remain trusted",
            "API operation and encoded-byte accounts are not CPU or physical memory measurements",
            "no consumer adoption, general equality, endpoint inference, or ancestor skipping",
        ],
    })
}

fn controls(input: &Evidence, expected: &Binding) -> Result<Vec<Control>> {
    let mut results = Vec::new();
    for (name, values) in [
        ("zero_roundtrip", [2, -1, 2]),
        ("zero_leaf_nonzero_result", [0, 2, 3]),
    ] {
        let mut meter = Meter::new();
        let mut checked = first_check(input, expected, &mut meter)?;
        let failure = checked
            .hit(expected, &mut meter)?
            .fresh_use(values, &mut meter)
            .expect_err("fixed negative must fail");
        results.push(Control {
            limits: meter.limits,
            name,
            input: input.clone(),
            expected: expected.clone(),
            values: Some(values),
            failure,
        });
    }
    for (name, change) in [
        ("disconnected_endpoints", 0),
        ("deleted_guard", 1),
        ("changed_checker", 2),
        ("exhausted_account", 3),
        ("mid_proof_depth_exhaustion", 4),
    ] {
        let mut meter = Meter::new();
        let mut candidate = input.clone();
        let mut context = expected.clone();
        match change {
            0 => candidate.reverse.before = ExactExprV0::constant(6),
            1 => {
                candidate.guards.pop();
            }
            2 => context.checker_build_digest.push('0'),
            3 => meter.limits.operations = 1,
            _ => meter.limits.depth = 1,
        }
        let failure =
            first_check(&candidate, &context, &mut meter).expect_err("fixed negative must fail");
        results.push(Control {
            limits: meter.limits,
            name,
            input: candidate,
            expected: context,
            values: None,
            failure,
        });
    }
    Ok(results)
}

pub(super) fn encode_report(report: &Report) -> Result<(Vec<u8>, String)> {
    let mut delivery = Meter::new();
    let bytes = delivery.encode(report)?;
    let account = serde_json::to_string(&delivery.spent)
        .map_err(|e| delivery.failure("Rejected", e.to_string()))?;
    Ok((bytes, account))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn fixture() -> (Evidence, Binding, Meter) {
        let input = evidence();
        let mut meter = Meter::new();
        let expected = binding(&input, &mut meter).unwrap();
        (input, expected, Meter::new())
    }

    #[test]
    fn replay_and_cache_keep_judgment_and_charge_each_phase() {
        let report = compare().unwrap();
        assert_eq!(
            report
                .full_replay
                .uses
                .iter()
                .map(|r| r.value.as_str())
                .collect::<Vec<_>>(),
            ["14", "11"]
        );
        assert_eq!(report.full_replay.total.proof_insert_calls, 16);
        assert_eq!(report.checked_cache.total.proof_insert_calls, 8);
        assert_eq!(report.full_replay.total.template_checks, 2);
        assert_eq!(report.checked_cache.total.template_checks, 1);
        assert_eq!(report.checked_cache.total.cache_hit_checks, 2);
        for route in [&report.full_replay, &report.checked_cache] {
            assert_eq!(route.total.compilations, 2);
            assert_eq!(route.total.instantiations, 2);
            assert_eq!(route.total.executions, 2);
            assert_eq!(route.total.peak_proof_nodes, 9);
            assert_eq!(route.total.peak_proof_edges, 8);
            assert_eq!(route.total.peak_proof_depth, 4);
            assert!(route.total.bytes > 0);
            assert!(
                route
                    .stages
                    .windows(2)
                    .all(|p| p[0].cumulative.operations < p[1].cumulative.operations)
            );
        }
        assert_ne!(
            report.checked_cache.uses[0].instance,
            report.checked_cache.uses[1].instance
        );
        assert_ne!(
            report.checked_cache.uses[0].bindings,
            report.checked_cache.uses[1].bindings
        );
        assert!(
            report
                .checked_cache
                .uses
                .iter()
                .all(|r| r.summary.nonzero_obligations.len() == 4)
        );
    }

    #[test]
    fn cache_rechecks_each_context_dimension() {
        for field in 0..6 {
            let (input, expected, mut meter) = fixture();
            let mut checked = first_check(&input, &expected, &mut meter).unwrap();
            let mut changed = expected.clone();
            match field {
                0 => changed.profile.push_str("-changed"),
                1 => changed.judgment.push_str("-changed"),
                2 => changed.interpretation.push_str("-changed"),
                3 => changed.premises.pop().map(|_| ()).unwrap(),
                4 => changed.evidence_digest.push('0'),
                _ => changed.checker_build_digest.push('0'),
            }
            let failure = checked.hit(&changed, &mut meter).unwrap_err();
            assert_eq!(failure.outcome, "Rejected");
            assert_eq!(failure.spent.requested_uses, 1);
            assert_eq!(failure.spent.executions, 0);
        }
    }

    #[test]
    fn first_check_refuses_changed_checker_and_profile() {
        let (input, mut expected, mut meter) = fixture();
        expected.profile.push_str("-foreign-package");
        assert_eq!(
            first_check(&input, &expected, &mut meter)
                .unwrap_err()
                .outcome,
            "Rejected"
        );
        assert_eq!(meter.spent.proof_insert_calls, 0);
    }

    #[test]
    fn literal_endpoints_reject_disconnected_cancelling_ratios() {
        let (mut input, expected, mut meter) = fixture();
        input.forward.before = ExactExprV0::constant(1);
        input.forward.after = ExactExprV0::constant(2);
        input.reverse.before = ExactExprV0::constant(6);
        input.reverse.after = ExactExprV0::constant(3);
        let a = adva_witness::MultiplicativeResidualV0::from_transition(
            &input.forward.before,
            &input.forward.after,
        )
        .unwrap();
        let b = adva_witness::MultiplicativeResidualV0::from_transition(
            &input.reverse.before,
            &input.reverse.after,
        )
        .unwrap();
        assert!(a.checked_multiply(&b).unwrap().is_one());
        assert!(
            first_check(&input, &expected, &mut meter)
                .unwrap_err()
                .reason
                .contains("endpoints")
        );
        assert_eq!(meter.spent.proof_insert_calls, 0);
    }

    #[test]
    fn opposite_unformed_boundaries_cannot_cancel() {
        let (mut input, expected, mut meter) = fixture();
        input.forward.actual = BoundaryChargeV0::zero();
        input.reverse.declared = BoundaryChargeV0::zero();
        assert!(
            first_check(&input, &expected, &mut meter)
                .unwrap_err()
                .reason
                .contains("unformed")
        );
        assert_eq!(meter.spent.proof_insert_calls, 0);
    }

    #[test]
    fn missing_guards_or_tampered_cached_evidence_are_refused() {
        let (mut input, expected, mut meter) = fixture();
        input.guards.pop();
        assert_eq!(
            first_check(&input, &expected, &mut meter)
                .unwrap_err()
                .outcome,
            "Rejected"
        );
        let input = evidence();
        let mut checked = first_check(&input, &expected, &mut meter).unwrap();
        checked.evidence.guards.pop(); // internal fault injection, no external mutable access
        assert!(
            checked
                .hit(&expected, &mut meter)
                .unwrap_err()
                .reason
                .contains("evidence")
        );
    }

    #[test]
    fn changed_input_zero_and_intermediate_zero_are_rechecked() {
        for values in [[2, -1, 2], [0, 2, 3], [2, 0, 3]] {
            let (input, expected, mut meter) = fixture();
            let mut checked = first_check(&input, &expected, &mut meter).unwrap();
            assert_eq!(
                checked
                    .hit(&expected, &mut meter)
                    .unwrap()
                    .fresh_use([2, 3, 4], &mut meter)
                    .unwrap()
                    .value,
                "14"
            );
            let failure = checked
                .hit(&expected, &mut meter)
                .unwrap()
                .fresh_use(values, &mut meter)
                .unwrap_err();
            assert_eq!(failure.outcome, "Rejected");
            assert!(failure.reason.contains("zero"));
            assert_eq!(failure.spent.executions, 2);
            assert_eq!(
                checked
                    .store
                    .artifact(&checked.formed.template.body)
                    .unwrap()
                    .summary
                    .nonzero_obligations
                    .len(),
                4
            );
            assert_eq!(
                checked.hit(&expected, &mut meter).unwrap_err().outcome,
                "Unknown"
            );
        }
    }

    #[test]
    fn input_range_is_enforced_before_compilation() {
        let (input, expected, mut meter) = fixture();
        let mut checked = first_check(&input, &expected, &mut meter).unwrap();
        assert_eq!(
            checked
                .hit(&expected, &mut meter)
                .unwrap()
                .fresh_use([17, 3, 4], &mut meter)
                .unwrap_err()
                .outcome,
            "Rejected"
        );
        assert_eq!(meter.spent.compilations, 0);
    }

    #[test]
    fn stored_guard_fault_blocks_execution_without_destroying_the_history() {
        let (input, expected, mut meter) = fixture();
        let mut checked = first_check(&input, &expected, &mut meter).unwrap();
        // A cache cannot assert concrete execution from symbolic Seal alone.
        assert!(
            checked
                .store
                .artifact(&checked.formed.template.body)
                .unwrap()
                .summary
                .is_multiplicatively_closed()
        );
        let failure = checked
            .hit(&expected, &mut meter)
            .unwrap()
            .fresh_use([2, -1, 2], &mut meter)
            .unwrap_err();
        assert_eq!(failure.outcome, "Rejected");
        assert_eq!(checked.next_use, 1);
        assert_eq!(checked.occurrences.len(), 3);
        assert_eq!(checked.artifacts.len(), 9);
    }

    #[test]
    fn budget_exhaustion_is_unknown_and_cannot_reset() {
        let (input, expected, _) = fixture();
        for limit in 0..6 {
            let mut meter = Meter::new();
            match limit {
                0 => meter.limits.operations = 2,
                1 => meter.limits.bytes = 1,
                2 => meter.limits.depth = 1,
                3 => meter.limits.nodes = 1,
                4 => meter.limits.edges = 1,
                _ => meter.limits.evidence_bytes = 1,
            }
            let failure = first_check(&input, &expected, &mut meter).unwrap_err();
            assert_eq!(failure.outcome, "Unknown");
            assert!(failure.spent.operations > 0);
            if limit >= 2 {
                assert!(!failure.retained_artifacts.is_empty());
            }
            let spent = meter.spent.clone();
            assert_eq!(meter.tick(0).unwrap_err().outcome, "Unknown");
            assert_eq!(meter.spent, spent);
        }
    }

    #[test]
    fn cooperative_deadline_stops_before_proof_admission() {
        let (input, expected, mut meter) = fixture();
        meter.start = Instant::now() - Duration::from_secs(31);
        let failure = first_check(&input, &expected, &mut meter).unwrap_err();
        assert_eq!(failure.outcome, "Unknown");
        assert_eq!(failure.spent.proof_insert_calls, 0);
    }

    #[test]
    fn checked_handle_needs_no_producer_verdict_after_first_check() {
        let (input, expected, mut meter) = fixture();
        let mut checked = first_check(&input, &expected, &mut meter).unwrap();
        drop(input);
        assert_eq!(
            checked
                .hit(&expected, &mut meter)
                .unwrap()
                .fresh_use([5, 2, 3], &mut meter)
                .unwrap()
                .value,
            "11"
        );
        assert_eq!(meter.spent.proof_insert_calls, 8);
    }
    #[test]
    fn report_retains_failures_and_fits_output_budget() {
        let report = compare().unwrap();
        assert_eq!(report.negative_controls.len(), 7);
        assert_eq!(report.negative_controls[0].failure.outcome, "Rejected");
        assert_eq!(
            report.negative_controls[0].failure.retained_artifacts.len(),
            9
        );
        assert_eq!(report.negative_controls[5].failure.outcome, "Unknown");
        assert_eq!(report.negative_controls[6].failure.outcome, "Unknown");
        assert_eq!(
            report.negative_controls[6].failure.retained_artifacts.len(),
            7
        );
        let (bytes, account) = encode_report(&report).unwrap();
        assert!(bytes.len() < MAX_RECORD);
        assert!(account.contains(&bytes.len().to_string()));
    }

    #[test]
    fn denied_preflight_does_not_claim_a_native_invocation() {
        let mut meter = Meter::new();
        meter.limits.operations = 0;
        assert_eq!(
            meter
                .native(NativeCall::Execute, || Ok::<_, String>(()))
                .unwrap_err()
                .outcome,
            "Unknown"
        );
        assert_eq!(meter.spent.executions, 0);
    }

    #[test]
    fn failed_native_call_still_checks_deadline_and_retains_error() {
        let mut meter = Meter::new();
        meter.limits.cooperative_millis = 100;
        let failure = meter
            .native(NativeCall::Execute, || {
                std::thread::sleep(Duration::from_millis(110));
                Err::<(), _>("retained native failure")
            })
            .unwrap_err();
        assert_eq!(failure.outcome, "Unknown");
        assert!(failure.reason.contains("retained native failure"));
        assert_eq!(failure.spent.executions, 1);
    }
    #[test]
    fn matching_but_unsupported_boundaries_are_not_admitted() {
        let (mut input, expected, mut meter) = fixture();
        input.forward.actual = BoundaryChargeV0::zero();
        input.forward.declared = BoundaryChargeV0::zero();
        input.reverse.actual = BoundaryChargeV0::zero();
        input.reverse.declared = BoundaryChargeV0::zero();
        assert_eq!(
            first_check(&input, &expected, &mut meter)
                .unwrap_err()
                .outcome,
            "Rejected"
        );
        assert_eq!(meter.spent.proof_insert_calls, 0);
    }

    #[test]
    fn replayed_native_context_is_refused_even_after_internal_counter_fault() {
        let (input, expected, mut meter) = fixture();
        let mut checked = first_check(&input, &expected, &mut meter).unwrap();
        checked
            .hit(&expected, &mut meter)
            .unwrap()
            .fresh_use([2, 3, 4], &mut meter)
            .unwrap();
        checked.next_use = 0; // internal fault injection; not exposed to callers
        let failure = checked
            .hit(&expected, &mut meter)
            .unwrap()
            .fresh_use([5, 2, 3], &mut meter)
            .unwrap_err();
        assert!(failure.reason.contains("reused native occurrence"));
        assert_eq!(failure.spent.executions, 1);
        assert_eq!(failure.retained_artifacts.len(), 9);
    }
}
