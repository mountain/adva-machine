//! Versioned bounded PSC0 receiving pilot; no stable operation authority.
//! Codex (OpenAI), through Mingli Yuan's authorized account proxy, Unknown v0.3.
//! The observer law compares exact decorated structure, never Real evaluation.

use adva_ir::{
    CompilationArtifact, CutConsumer, CutWire, GraftFrameKind, HistoryEvent, NodeId, Occurrence,
    OccurrenceId, OccurrencePath, OperationRef, QualifiedName, Rational, SharedProgramDiagram,
    SourceId, ValueType, WireProducer, WireRef,
};
use adva_lisp::{analyze_program_slice_with_graft, validate_diagram};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

#[cfg(test)]
const MODULE: &str = "native-binding";
#[cfg(test)]
const BODY: &str = "(frontier (add (copy (use static))) (add (copy (use dynamic))) (discard 1))";

// The current parser freezes literals at builtin constant@2. The retained
// OperationRef::constant helper names historical constant@1; do not conflate
// either exact operation declaration with numerical value equality.
fn literal_operation(value: Rational) -> OperationRef {
    OperationRef {
        version: 2,
        ..OperationRef::constant(value)
    }
}

// Context qualification is explicit. Local occ:N/node indices are not globally fresh.
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct QualifiedOccurrence {
    pub context: QualifiedName,
    pub source: SourceId,
    pub local_id: OccurrenceId,
    pub path: OccurrencePath,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ResearchCertificate {
    pub source_snapshot: SharedProgramDiagram,
    pub residual_snapshot: SharedProgramDiagram,
    pub static_value: Rational,
    pub bound_source: SourceId,
    pub dynamic_source: (SourceId, SourceId),
    pub event_map: Vec<(NodeId, NodeId)>,
    pub occurrence_map: Vec<(QualifiedOccurrence, Option<QualifiedOccurrence>)>,
    pub forgotten_static_occurrences: Vec<Occurrence>,
    pub forgotten_static_history: Vec<HistoryEvent>,
    pub binding_node: NodeId,
}

// This request is fixed independently of the proposed certificate. IDs alone
// cannot bind the source body, and changing a certificate cannot change the task.
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExpectedRequest {
    pub source_snapshot: SharedProgramDiagram,
    pub residual_context: QualifiedName,
    pub static_value: Rational,
}

#[derive(Debug, Eq, PartialEq)]
enum Outcome {
    #[cfg(test)]
    Certified(Box<ResearchCertificate>),
    Refused(&'static str),
    Unknown(&'static str),
}

struct Budget(usize);

impl Budget {
    fn charge(&mut self, work: usize) -> Result<(), Outcome> {
        if self.0 < work {
            return Err(Outcome::Unknown("structural checker budget exhausted"));
        }
        self.0 -= work;
        Ok(())
    }
}

fn qualified(diagram: &SharedProgramDiagram, occurrence: &Occurrence) -> QualifiedOccurrence {
    QualifiedOccurrence {
        context: diagram.function.clone(),
        source: occurrence.source.clone(),
        local_id: occurrence.id.clone(),
        path: occurrence.path.clone(),
    }
}

#[cfg(test)]
fn fixtures(body: &str, value: Rational) -> (CompilationArtifact, CompilationArtifact) {
    use adva_lisp::{compile_function, link_modules, parse_module};
    let text = format!(
        "(module {MODULE} (export source residual)\n\
         (def source (fn ((static Real) (dynamic Real)) (outputs Real Real) {body}))\n\
         (def residual (fn ((dynamic Real)) (outputs Real Real)\n\
           (call source {}/{} (use dynamic)))))",
        value.numerator, value.denominator
    );
    let linked = link_modules(vec![parse_module(&text).unwrap()]).unwrap();
    (
        compile_function(&linked, MODULE, "source").unwrap(),
        compile_function(&linked, MODULE, "residual").unwrap(),
    )
}

fn input_source(artifact: &CompilationArtifact, index: usize) -> SourceId {
    let root = &artifact.graft_trace.result.frames[0];
    let id = &root.holes[index].entry_wire.lineage[0];
    artifact
        .result
        .occurrences
        .iter()
        .find(|occurrence| &occurrence.id == id)
        .unwrap()
        .source
        .clone()
}

// Proposal construction uses the compiler's call-body region. The receiver
// below separately checks coverage, each wire, lineage, history and slice.
#[cfg(test)]
fn propose(
    source: &CompilationArtifact,
    residual: &CompilationArtifact,
    static_value: Rational,
) -> ResearchCertificate {
    let bound_source = input_source(source, 0);
    let dynamic_source = (input_source(source, 1), input_source(residual, 0));
    let call = &residual.graft_trace.result.frames[1];
    let occurrence_map = source
        .result
        .occurrences
        .iter()
        .map(|occurrence| {
            let target = residual.result.occurrences.iter().find(|target| {
                occurrence.source == dynamic_source.0
                    && target.source == dynamic_source.1
                    && occurrence.path == target.path
            });
            (
                qualified(&source.result, occurrence),
                target.map(|target| qualified(&residual.result, target)),
            )
        })
        .collect();
    let static_ids: BTreeSet<_> = source
        .result
        .occurrences
        .iter()
        .filter(|occurrence| occurrence.source == bound_source)
        .map(|occurrence| occurrence.id.clone())
        .collect();
    ResearchCertificate {
        source_snapshot: source.result.clone(),
        residual_snapshot: residual.result.clone(),
        static_value,
        bound_source,
        dynamic_source,
        event_map: source
            .result
            .nodes
            .iter()
            .map(|node| node.id)
            .zip(call.body_region.iter().copied())
            .collect(),
        occurrence_map,
        forgotten_static_occurrences: source
            .result
            .occurrences
            .iter()
            .filter(|occurrence| static_ids.contains(&occurrence.id))
            .cloned()
            .collect(),
        forgotten_static_history: source
            .result
            .history
            .prefix
            .iter()
            .filter(|event| match event {
                HistoryEvent::Source { occurrence, .. } => static_ids.contains(occurrence),
                HistoryEvent::Copy { parent, .. } => static_ids.contains(parent),
                _ => false,
            })
            .cloned()
            .collect(),
        binding_node: residual.result.nodes[0].id,
    }
}

#[cfg(test)]
fn receive(
    source: &CompilationArtifact,
    residual: &CompilationArtifact,
    certificate: &ResearchCertificate,
    request: &ExpectedRequest,
    work: usize,
) -> Outcome {
    match check(source, residual, certificate, request, &mut Budget(work)) {
        Ok(()) => Outcome::Certified(Box::new(certificate.clone())),
        Err(outcome) => outcome,
    }
}

fn require(condition: bool, reason: &'static str) -> Result<(), Outcome> {
    if condition {
        Ok(())
    } else {
        Err(Outcome::Refused(reason))
    }
}

fn check(
    source: &CompilationArtifact,
    residual: &CompilationArtifact,
    certificate: &ResearchCertificate,
    request: &ExpectedRequest,
    budget: &mut Budget,
) -> Result<(), Outcome> {
    budget.charge(1)?;
    let source_diagram = &source.result;
    let residual_diagram = &residual.result;
    // Finite admission before kernel validation; this test-local profile accepts
    // only two Real inputs, one bound literal, and at most sixteen body events.
    for diagram in [source_diagram, residual_diagram] {
        if diagram.nodes.len() > 17
            || diagram.occurrences.len() > 32
            || diagram.history.prefix.len() > 64
            || diagram.signature.outputs.len() > 2
            || diagram.signature.inputs.len() > 2
            || diagram.nodes.iter().any(|node| node.inputs.len() > 2)
        {
            return Err(Outcome::Unknown(
                "outside the fixed finite structural profile",
            ));
        }
        budget.charge(
            1 + diagram.nodes.len() + diagram.occurrences.len() + diagram.history.prefix.len(),
        )?;
        validate_diagram(diagram.clone())
            .map_err(|_| Outcome::Refused("native diagram validation failed"))?;
    }
    require(
        *source_diagram == request.source_snapshot
            && certificate.source_snapshot == *source_diagram
            && certificate.residual_snapshot == *residual_diagram,
        "source or residual snapshot does not bind the caller's question",
    )?;
    require(
        residual_diagram.function == request.residual_context
            && source_diagram.function != residual_diagram.function,
        "residual must have the independently declared distinct checked context",
    )?;
    require(
        certificate.static_value == request.static_value
            && Rational::new(
                request.static_value.numerator,
                request.static_value.denominator,
            )
            .ok()
                == Some(request.static_value),
        "static rational is changed or noncanonical",
    )?;
    require(
        source_diagram.signature.inputs.len() == 2
            && residual_diagram.signature.inputs.len() == 1
            && source_diagram.signature.inputs[0].value_type == ValueType::Real
            && source_diagram.signature.inputs[1].value_type == ValueType::Real
            && source_diagram.signature.inputs[1] == residual_diagram.signature.inputs[0]
            && source_diagram.signature.outputs == residual_diagram.signature.outputs,
        "input-binding boundary mismatch",
    )?;
    require(
        source.graft_trace.result.frames.len() == 1
            && residual.graft_trace.result.frames.len() == 2,
        "only call-free source and one wrapper call are admitted",
    )?;
    // These calls revalidate the supplied graft data; booleans on supplied
    // compilation/graft certificates are not taken as authorization.
    let source_past: Vec<_> = source_diagram.nodes.iter().map(|node| node.id).collect();
    let residual_past: Vec<_> = residual_diagram.nodes.iter().map(|node| node.id).collect();
    budget.charge(3)?;
    let source_slice = analyze_program_slice_with_graft(
        source_diagram,
        &source.graft_trace.result,
        &[],
        &source_past,
    )
    .map_err(|_| Outcome::Refused("source graft/slice validation failed"))?;
    let residual_full = analyze_program_slice_with_graft(
        residual_diagram,
        &residual.graft_trace.result,
        &[],
        &residual_past,
    )
    .map_err(|_| Outcome::Refused("residual graft/slice validation failed"))?;
    require(
        source_slice.certificate.certified() && residual_full.certificate.certified(),
        "native slice certificate not checked",
    )?;
    let call = &residual.graft_trace.result.frames[1];
    require(
        call.kind == GraftFrameKind::Call
            && call.callee == source_diagram.function
            && call.boundary == source_diagram.signature
            && call.holes.len() == 2
            && call.body_region.len() == source_diagram.nodes.len()
            && residual_diagram.nodes.len() == source_diagram.nodes.len() + 1,
        "graft is not the complete declared source body",
    )?;
    let binding = &residual_diagram.nodes[0];
    require(
        certificate.binding_node == binding.id
            && binding.operation == literal_operation(request.static_value)
            && binding.inputs.is_empty()
            && binding.output_types == vec![ValueType::Real],
        "binding prefix is not the declared exact literal",
    )?;
    require(
        certificate.bound_source == input_source(source, 0)
            && certificate.dynamic_source == (input_source(source, 1), input_source(residual, 0)),
        "source correspondence mismatch",
    )?;
    require(
        certificate.event_map
            == source_diagram
                .nodes
                .iter()
                .map(|node| node.id)
                .zip(call.body_region.iter().copied())
                .collect::<Vec<_>>(),
        "incomplete or reordered body event correspondence",
    )?;
    let events: BTreeMap<_, _> = certificate.event_map.iter().copied().collect();
    let mut occurrences = BTreeMap::new();
    require(
        certificate.occurrence_map.len() == source_diagram.occurrences.len(),
        "occurrence correspondence is incomplete",
    )?;
    let mut seen_residual = BTreeSet::new();
    let mut static_occurrences = Vec::new();
    for (source_occurrence, (declared, target)) in source_diagram
        .occurrences
        .iter()
        .zip(&certificate.occurrence_map)
    {
        budget.charge(1)?;
        require(
            *declared == qualified(source_diagram, source_occurrence),
            "qualified source occurrence mismatch",
        )?;
        if source_occurrence.source == certificate.bound_source {
            require(
                target.is_none(),
                "static lineage was silently retained or identified",
            )?;
            static_occurrences.push(source_occurrence.clone());
            occurrences.insert(source_occurrence.id.clone(), None);
        } else {
            let target = target
                .as_ref()
                .ok_or(Outcome::Refused("dynamic occurrence was forgotten"))?;
            require(
                source_occurrence.source == certificate.dynamic_source.0
                    && target.context == residual_diagram.function
                    && target.source == certificate.dynamic_source.1
                    && target.path == source_occurrence.path,
                "dynamic source, context or copy path changed",
            )?;
            let actual = residual_diagram
                .occurrences
                .iter()
                .find(|occurrence| occurrence.id == target.local_id)
                .ok_or(Outcome::Refused("target occurrence is absent"))?;
            require(
                qualified(residual_diagram, actual) == *target
                    && seen_residual.insert(target.local_id.clone()),
                "target occurrence is altered or reused",
            )?;
            occurrences.insert(source_occurrence.id.clone(), Some(target.local_id.clone()));
        }
    }
    require(
        seen_residual.len() == residual_diagram.occurrences.len()
            && certificate.forgotten_static_occurrences == static_occurrences,
        "static ledger or residual occurrence coverage is incomplete",
    )?;
    let static_ids: BTreeSet<_> = static_occurrences.iter().map(|o| o.id.clone()).collect();
    let forgotten: Vec<_> = source_diagram
        .history
        .prefix
        .iter()
        .filter(|event| match event {
            HistoryEvent::Source { occurrence, .. } => static_ids.contains(occurrence),
            HistoryEvent::Copy { parent, .. } => static_ids.contains(parent),
            _ => false,
        })
        .cloned()
        .collect();
    require(
        certificate.forgotten_static_history == forgotten,
        "static source/copy history ledger is incomplete",
    )?;
    let project_wire = |wire: &WireRef| -> Result<WireRef, Outcome> {
        let mut mapped = wire.clone();
        mapped.producer = match wire.producer {
            WireProducer::Input { index } => match index {
                0 => WireProducer::Node { node: binding.id },
                1 => WireProducer::Input { index: 0 },
                _ => return Err(Outcome::Refused("unsupported source input")),
            },
            WireProducer::Node { node } => WireProducer::Node {
                node: *events
                    .get(&node)
                    .ok_or(Outcome::Refused("unmapped body producer"))?,
            },
        };
        mapped.lineage = wire
            .lineage
            .iter()
            .map(|id| {
                occurrences
                    .get(id)
                    .cloned()
                    .ok_or(Outcome::Refused("unmapped lineage"))
            })
            .collect::<Result<Vec<_>, _>>()?
            .into_iter()
            .flatten()
            .collect();
        Ok(mapped)
    };
    require(
        project_wire(&source.graft_trace.result.frames[0].holes[0].entry_wire)?
            == call.holes[0].entry_wire
            && project_wire(&source.graft_trace.result.frames[0].holes[1].entry_wire)?
                == call.holes[1].entry_wire,
        "ordered graft hole correspondence changed",
    )?;
    for node in &source_diagram.nodes {
        budget.charge(1 + node.inputs.len())?;
        let target = residual_diagram
            .nodes
            .iter()
            .find(|target| target.id == events[&node.id])
            .ok_or(Outcome::Refused("mapped body event absent"))?;
        require(
            node.operation == target.operation
                && node.output_types == target.output_types
                && node
                    .inputs
                    .iter()
                    .map(&project_wire)
                    .collect::<Result<Vec<_>, _>>()?
                    == target.inputs,
            "ordered body operation/wire correspondence changed",
        )?;
    }
    require(
        source_diagram
            .outputs
            .iter()
            .map(&project_wire)
            .collect::<Result<Vec<_>, _>>()?
            == residual_diagram.outputs,
        "ordered output correspondence changed",
    )?;
    let body_slice = analyze_program_slice_with_graft(
        residual_diagram,
        &residual.graft_trace.result,
        &[binding.id],
        &residual_past,
    )
    .map_err(|_| Outcome::Refused("residual body slice validation failed"))?;
    require(
        body_slice.certificate.certified()
            && body_slice.result.internal_events
                == source_slice
                    .result
                    .internal_events
                    .iter()
                    .map(|id| events[id])
                    .collect::<Vec<_>>(),
        "hidden body events were erased",
    )?;
    let project_cut = |cut: &CutWire| -> Result<CutWire, Outcome> {
        Ok(CutWire {
            wire: project_wire(&cut.wire)?,
            sources: cut
                .sources
                .iter()
                .filter(|source| **source != certificate.bound_source)
                .map(|source| {
                    if *source == certificate.dynamic_source.0 {
                        Ok(certificate.dynamic_source.1.clone())
                    } else {
                        Err(Outcome::Refused("unmapped cut source"))
                    }
                })
                .collect::<Result<Vec<_>, _>>()?,
            consumer: match cut.consumer {
                CutConsumer::Node { node, input_index } => CutConsumer::Node {
                    node: events[&node],
                    input_index,
                },
                CutConsumer::Output { index } => CutConsumer::Output { index },
            },
        })
    };
    // Cut vectors use each diagram's canonical producer order. Compare exact
    // incidences without pretending that the two vector orders are identical.
    for (left, right) in [
        (
            &source_slice.result.lower.frontier,
            &body_slice.result.lower.frontier,
        ),
        (
            &source_slice.result.upper.frontier,
            &body_slice.result.upper.frontier,
        ),
        (
            &source_slice.result.through_wires,
            &body_slice.result.through_wires,
        ),
        (
            &source_slice.result.lower_boundary,
            &body_slice.result.lower_boundary,
        ),
        (
            &source_slice.result.upper_boundary,
            &body_slice.result.upper_boundary,
        ),
    ] {
        budget.charge(left.len())?;
        let projected = left
            .iter()
            .map(&project_cut)
            .collect::<Result<Vec<_>, _>>()?;
        require(
            projected.len() == right.len() && projected.iter().all(|wire| right.contains(wire)),
            "decorated cut observation does not commute",
        )?;
    }
    let mut projected_history = Vec::new();
    for event in &source_slice.result.event_history {
        budget.charge(1)?;
        match event {
            HistoryEvent::Copy {
                node,
                parent,
                children,
            } if !static_ids.contains(parent) => {
                projected_history.push(HistoryEvent::Copy {
                    node: events[node],
                    parent: occurrences[parent]
                        .clone()
                        .ok_or(Outcome::Refused("copy parent missing"))?,
                    children: children
                        .iter()
                        .map(|id| {
                            occurrences[id]
                                .clone()
                                .ok_or(Outcome::Refused("copy child missing"))
                        })
                        .collect::<Result<Vec<_>, _>>()?,
                });
            }
            HistoryEvent::Copy { .. } => {}
            HistoryEvent::Operation { node, operation } => {
                projected_history.push(HistoryEvent::Operation {
                    node: events[node],
                    operation: operation.clone(),
                });
            }
            _ => return Err(Outcome::Refused("unsupported body history event")),
        }
    }
    require(
        projected_history == body_slice.result.event_history,
        "body history observation does not commute",
    )?;
    Ok(())
}

#[cfg(test)]
fn request(
    source: &CompilationArtifact,
    residual: &CompilationArtifact,
    value: Rational,
) -> ExpectedRequest {
    ExpectedRequest {
        source_snapshot: source.result.clone(),
        residual_context: residual.result.function.clone(),
        static_value: value,
    }
}

#[cfg(test)]
mod regression {
    use super::*;
    #[test]
    fn certified_binding_preserves_dynamic_copy_and_all_body_events_without_evaluation() {
        for value in [
            Rational::ZERO,
            Rational::new(7, 3).unwrap(),
            Rational::new(-5, 2).unwrap(),
        ] {
            let (source, residual) = fixtures(BODY, value);
            let certificate = propose(&source, &residual, value);
            let expected = request(&source, &residual, value);
            assert_eq!(
                receive(&source, &residual, &certificate, &expected, 512),
                Outcome::Certified(Box::new(certificate.clone()))
            );
            assert_eq!(certificate.event_map.len(), 6);
            assert_eq!(certificate.forgotten_static_occurrences.len(), 3);
            assert_eq!(certificate.forgotten_static_history.len(), 2);
            assert_eq!(
                certificate
                    .occurrence_map
                    .iter()
                    .filter(|(_, target)| target.is_some())
                    .count(),
                3
            );
            assert!(
                source
                    .result
                    .nodes
                    .iter()
                    .any(|node| node.operation.name == "discard")
            );
            assert!(
                residual
                    .result
                    .nodes
                    .iter()
                    .any(|node| node.operation.name == "discard")
            );
            // Both contexts deliberately reuse local occ:0; equality of this local
            // coordinate must not identify source and residual semantic objects.
            assert_eq!(
                source.result.occurrences[0].id,
                residual.result.occurrences[0].id
            );
            assert_ne!(source.result.function, residual.result.function);
        }
    }

    #[test]
    fn forgotten_static_root_is_retained_when_the_bound_input_is_discarded() {
        let (source, residual) = fixtures(
            "(frontier (discard (use static)) (copy (use dynamic)))",
            Rational::ONE,
        );
        let certificate = propose(&source, &residual, Rational::ONE);
        assert_eq!(certificate.forgotten_static_occurrences.len(), 1);
        assert_eq!(certificate.forgotten_static_history.len(), 1);
        assert!(matches!(
            receive(
                &source,
                &residual,
                &certificate,
                &request(&source, &residual, Rational::ONE),
                512
            ),
            Outcome::Certified(_)
        ));
    }

    #[test]
    fn zero_event_source_keeps_ordered_through_wires_under_binding() {
        let (source, residual) = fixtures("(frontier (use static) (use dynamic))", Rational::ONE);
        let certificate = propose(&source, &residual, Rational::ONE);
        assert!(certificate.event_map.is_empty());
        assert!(matches!(
            receive(
                &source,
                &residual,
                &certificate,
                &request(&source, &residual, Rational::ONE),
                512
            ),
            Outcome::Certified(_)
        ));
    }

    #[test]
    fn missing_or_forged_accounting_is_refused() {
        let value = Rational::new(7, 3).unwrap();
        let (source, residual) = fixtures(BODY, value);
        let original = propose(&source, &residual, value);
        let expected = request(&source, &residual, value);
        let mut mutations = Vec::new();
        let mut changed = original.clone();
        changed.event_map.pop();
        mutations.push(changed);
        let mut changed = original.clone();
        changed.event_map.swap(0, 1);
        mutations.push(changed);
        let mut changed = original.clone();
        changed.forgotten_static_occurrences.pop();
        mutations.push(changed);
        let mut changed = original.clone();
        changed.forgotten_static_history.pop();
        mutations.push(changed);
        let mut changed = original.clone();
        changed.occurrence_map.pop();
        mutations.push(changed);
        let mut changed = original.clone();
        changed.static_value = Rational::ONE;
        mutations.push(changed);
        let mut changed = original.clone();
        changed.occurrence_map[1].1 = None;
        mutations.push(changed);
        let mut changed = original.clone();
        changed.occurrence_map[1].1.as_mut().unwrap().context = source.result.function.clone();
        mutations.push(changed);
        let mut changed = original.clone();
        changed.occurrence_map[4].1.as_mut().unwrap().path = OccurrencePath::root();
        mutations.push(changed);
        for changed in mutations {
            assert!(matches!(
                receive(&source, &residual, &changed, &expected, 512),
                Outcome::Refused(_)
            ));
        }
    }

    #[test]
    fn changed_body_with_the_same_local_ids_cannot_repin_the_callers_source() {
        let value = Rational::ONE;
        let (source, residual) = fixtures(BODY, value);
        let expected = request(&source, &residual, value);
        let changed_body = BODY.replace("(add (copy (use dynamic)))", "(mul (copy (use dynamic)))");
        let (changed_source, changed_residual) = fixtures(&changed_body, value);
        assert_eq!(source.result.function, changed_source.result.function);
        assert_eq!(source.result.occurrences, changed_source.result.occurrences);
        let repinned = propose(&changed_source, &changed_residual, value);
        assert!(matches!(
            receive(
                &changed_source,
                &changed_residual,
                &repinned,
                &expected,
                512
            ),
            Outcome::Refused(_)
        ));
        let changed_request_context = request(&source, &residual, value);
        let mut forged = propose(&source, &residual, value);
        forged.residual_snapshot.function = source.result.function.clone();
        assert!(matches!(
            receive(&source, &residual, &forged, &changed_request_context, 512),
            Outcome::Refused(_)
        ));
    }

    #[test]
    fn ordered_outputs_and_graft_maps_are_checked_again() {
        let value = Rational::ONE;
        let (source, residual) = fixtures(BODY, value);
        let expected = request(&source, &residual, value);
        let mut changed = residual.clone();
        changed.result.outputs.swap(0, 1);
        let repinned = propose(&source, &changed, value);
        assert!(matches!(
            receive(&source, &changed, &repinned, &expected, 512),
            Outcome::Refused(_)
        ));
        let mut changed = residual.clone();
        changed.graft_trace.result.frames[1].holes.swap(0, 1);
        assert!(matches!(
            receive(
                &source,
                &changed,
                &propose(&source, &residual, value),
                &expected,
                512
            ),
            Outcome::Refused(_)
        ));
    }

    #[test]
    fn literal_version_and_repinned_static_data_do_not_change_the_question() {
        let value = Rational::new(7, 3).unwrap();
        let (source, residual) = fixtures(BODY, value);
        let expected = request(&source, &residual, value);
        let mut historical_literal = residual.clone();
        let binding_id = historical_literal.result.nodes[0].id;
        historical_literal.result.nodes[0].operation = OperationRef::constant(value);
        for event in &mut historical_literal.result.history.prefix {
            match event {
                HistoryEvent::Operation { node, operation } if *node == binding_id => {
                    *operation = OperationRef::constant(value);
                }
                _ => {}
            }
        }
        assert!(validate_diagram(historical_literal.result.clone()).is_ok());
        let repinned = propose(&source, &historical_literal, value);
        assert!(matches!(
            receive(&source, &historical_literal, &repinned, &expected, 512),
            Outcome::Refused(_)
        ));
        let (_, changed_literal) = fixtures(BODY, Rational::ONE);
        let repinned = propose(&source, &changed_literal, Rational::ONE);
        assert!(matches!(
            receive(&source, &changed_literal, &repinned, &expected, 512),
            Outcome::Refused(_)
        ));
    }

    #[test]
    fn deletion_of_hidden_discard_or_copy_is_not_a_specialization_certificate() {
        let value = Rational::ONE;
        let (source, residual) = fixtures(BODY, value);
        let expected = request(&source, &residual, value);
        for changed_body in [
            BODY.replace(" (discard 1)", ""),
            BODY.replace("(add (copy (use dynamic)))", "(neg (use dynamic))"),
        ] {
            let (_, changed_residual) = fixtures(&changed_body, value);
            let repinned = propose(&source, &changed_residual, value);
            assert!(matches!(
                receive(&source, &changed_residual, &repinned, &expected, 512),
                Outcome::Refused(_)
            ));
        }
    }

    #[test]
    fn a_valid_graph_outside_the_frozen_size_profile_is_unknown() {
        let mut dynamic = "(use dynamic)".to_owned();
        for _ in 0..17 {
            dynamic = format!("(id {dynamic})");
        }
        let body = format!("(frontier (use static) {dynamic})");
        let (source, residual) = fixtures(&body, Rational::ONE);
        assert_eq!(source.result.nodes.len(), 17);
        assert_eq!(residual.result.nodes.len(), 18);
        let certificate = propose(&source, &residual, Rational::ONE);
        assert_eq!(
            receive(
                &source,
                &residual,
                &certificate,
                &request(&source, &residual, Rational::ONE),
                512
            ),
            Outcome::Unknown("outside the fixed finite structural profile")
        );
    }

    #[test]
    fn exhaustion_produces_no_certificate_or_automatic_refuelling() {
        let (source, residual) = fixtures(BODY, Rational::ONE);
        let certificate = propose(&source, &residual, Rational::ONE);
        let expected = request(&source, &residual, Rational::ONE);
        for work in [0, 1, 40] {
            assert!(matches!(
                receive(&source, &residual, &certificate, &expected, work),
                Outcome::Unknown(_)
            ));
        }
    }
}

/// Meaning-versioned experimental profile. Implementation identity is additionally
/// fixed by the consumer's full machine commit, never selected by the proposal.
pub const PROFILE: &str = "adva.psc0-input-binding.receive.v0";
pub const MAX_BYTES: usize = 262_144;
pub const MAX_WORK: usize = 4096;

#[derive(Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RequestV0 {
    pub profile: String,
    pub expected: ExpectedRequest,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProposalV0 {
    pub profile: String,
    pub source: CompilationArtifact,
    pub residual: CompilationArtifact,
    pub certificate: ResearchCertificate,
}

#[derive(Debug, Eq, PartialEq, Serialize)]
pub enum Status {
    BoundedAccepted,
    Rejected,
    Unknown,
}

#[derive(Debug, Serialize)]
pub struct Report {
    pub profile: &'static str,
    pub status: Status,
    pub reason: &'static str,
    pub stable_native_authority: bool,
    pub structural_work_spent: usize,
}

// Native tagged enums deliberately retain their legacy decoding rules. This
// isolated wire profile rejects fields those rules would otherwise discard.
fn fields_preserved(input: &serde_json::Value, decoded: &serde_json::Value) -> bool {
    use serde_json::Value;
    match (input, decoded) {
        (Value::Object(left), Value::Object(right)) => left.iter().all(|(key, value)| {
            right
                .get(key)
                .is_some_and(|other| fields_preserved(value, other))
        }),
        (Value::Array(left), Value::Array(right)) => {
            left.len() == right.len() && left.iter().zip(right).all(|(a, b)| fields_preserved(a, b))
        }
        _ => input == decoded,
    }
}

fn strict_decode<T: serde::de::DeserializeOwned + Serialize>(bytes: &[u8]) -> Option<T> {
    // Decode directly first so duplicate struct fields are not collapsed by Value.
    let decoded: T = serde_json::from_slice(bytes).ok()?;
    let input = serde_json::from_slice(bytes).ok()?;
    let normalized = serde_json::to_value(&decoded).ok()?;
    fields_preserved(&input, &normalized).then_some(decoded)
}

/// Request bytes must come from the consumer, through a channel independent of
/// the producer. There is no network fetch, producer callback or receipt cache.
pub fn receive_json(request: &[u8], proposal: &[u8], work: usize) -> Report {
    let report = |status, reason, spent| Report {
        profile: PROFILE,
        status,
        reason,
        stable_native_authority: false,
        structural_work_spent: spent,
    };
    if request.len() > MAX_BYTES || proposal.len() > MAX_BYTES || work > MAX_WORK || work == 0 {
        return report(Status::Unknown, "outside byte/work admission budget", 0);
    }
    let Some(request) = strict_decode::<RequestV0>(request) else {
        return report(Status::Rejected, "invalid request JSON", 0);
    };
    let Some(proposal) = strict_decode::<ProposalV0>(proposal) else {
        return report(Status::Rejected, "invalid proposal JSON", 0);
    };
    if request.profile != PROFILE || proposal.profile != PROFILE {
        return report(Status::Rejected, "unsupported profile identity", 0);
    }
    let mut budget = Budget(work);
    let result = check(
        &proposal.source,
        &proposal.residual,
        &proposal.certificate,
        &request.expected,
        &mut budget,
    );
    let spent = work - budget.0;
    match result {
        Ok(()) => report(
            Status::BoundedAccepted,
            "exact structural correspondence checked",
            spent,
        ),
        Err(Outcome::Refused(reason)) => report(Status::Rejected, reason, spent),
        Err(Outcome::Unknown(reason)) => report(Status::Unknown, reason, spent),
        #[cfg(test)]
        Err(Outcome::Certified(_)) => unreachable!("check never constructs success outcomes"),
    }
}

#[cfg(test)]
mod boundary_tests {
    use super::*;

    fn payload() -> (Vec<u8>, Vec<u8>) {
        let (source, residual) = fixtures(BODY, Rational::new(7, 3).unwrap());
        let expected = request(&source, &residual, Rational::new(7, 3).unwrap());
        let certificate = propose(&source, &residual, expected.static_value);
        (
            serde_json::to_vec(&RequestV0 {
                profile: PROFILE.into(),
                expected,
            })
            .unwrap(),
            serde_json::to_vec(&ProposalV0 {
                profile: PROFILE.into(),
                source,
                residual,
                certificate,
            })
            .unwrap(),
        )
    }

    #[test]
    fn independent_request_roundtrip_and_no_authority() {
        let (request, proposal) = payload();
        let result = receive_json(&request, &proposal, 512);
        assert_eq!(result.status, Status::BoundedAccepted);
        assert!(!result.stable_native_authority);
        assert!(result.structural_work_spent > 0);
        assert_eq!(receive_json(&request, &proposal, 1).status, Status::Unknown);
    }

    #[test]
    fn version_unknown_fields_and_byte_budget() {
        let (request, proposal) = payload();
        let mut changed: serde_json::Value = serde_json::from_slice(&proposal).unwrap();
        changed["profile"] = "adva.psc0-input-binding.receive.v1".into();
        assert_eq!(
            receive_json(&request, &serde_json::to_vec(&changed).unwrap(), 512).status,
            Status::Rejected
        );
        changed["profile"] = PROFILE.into();
        changed["grants_native_authority"] = true.into();
        assert_eq!(
            receive_json(&request, &serde_json::to_vec(&changed).unwrap(), 512).status,
            Status::Rejected
        );
        assert_eq!(
            receive_json(&request, &vec![b' '; MAX_BYTES + 1], 512).status,
            Status::Unknown
        );
    }

    #[test]
    fn nested_history_cannot_hide_checker_selection_or_authority() {
        let (request, proposal) = payload();
        for field in ["checker_commit", "stable_native_authority"] {
            let mut changed: serde_json::Value = serde_json::from_slice(&proposal).unwrap();
            changed["source"]["result"]["history"]["prefix"][0][field] = true.into();
            let result = receive_json(&request, &serde_json::to_vec(&changed).unwrap(), 512);
            assert_eq!(result.status, Status::Rejected);
            assert!(!result.stable_native_authority);
        }
    }

    #[test]
    fn request_identity_and_noncanonical_rationals_are_rejected() {
        let (request, proposal) = payload();
        for (numerator, denominator) in [(14, 6), (7, 0), (-7, -3)] {
            let mut changed: RequestV0 = serde_json::from_slice(&request).unwrap();
            changed.expected.static_value = Rational {
                numerator,
                denominator,
            };
            assert_eq!(
                receive_json(&serde_json::to_vec(&changed).unwrap(), &proposal, 512).status,
                Status::Rejected
            );
        }
        let mut changed: serde_json::Value = serde_json::from_slice(&request).unwrap();
        changed["expected"]["checker_commit"] = "attacker-selected".into();
        assert_eq!(
            receive_json(&serde_json::to_vec(&changed).unwrap(), &proposal, 512).status,
            Status::Rejected
        );
        changed.as_object_mut().unwrap().remove("expected");
        assert_eq!(
            receive_json(&serde_json::to_vec(&changed).unwrap(), &proposal, 512).status,
            Status::Rejected
        );
    }

    #[test]
    fn malformed_and_budget_outcomes_never_grant_authority() {
        let (request, proposal) = payload();
        for bad in [b"{}".as_slice(), b"null", b"{", b"[]"] {
            let result = receive_json(&request, bad, 512);
            assert_eq!(result.status, Status::Rejected);
            assert!(!result.stable_native_authority);
        }
        for work in [0, 1, MAX_WORK + 1] {
            let result = receive_json(&request, &proposal, work);
            assert_eq!(result.status, Status::Unknown);
            assert!(!result.stable_native_authority);
            assert!(result.structural_work_spent <= work);
        }
        let first = receive_json(&request, &proposal, 512);
        let repeated = receive_json(&request, &proposal, 512);
        assert_eq!(first.status, Status::BoundedAccepted);
        assert_eq!(first.structural_work_spent, repeated.structural_work_spent);
    }

    #[test]
    fn wire_boundary_preserves_independent_source_and_ledgers() {
        let (request, proposal) = payload();
        for mutate in 0..4 {
            let mut changed: ProposalV0 = serde_json::from_slice(&proposal).unwrap();
            match mutate {
                0 => changed.certificate.forgotten_static_history.clear(),
                1 => changed.certificate.forgotten_static_occurrences.clear(),
                2 => changed.certificate.occurrence_map.clear(),
                _ => changed.residual.result.function = changed.source.result.function.clone(),
            }
            assert_eq!(
                receive_json(&request, &serde_json::to_vec(&changed).unwrap(), 512).status,
                Status::Rejected
            );
        }
        let mut changed: RequestV0 = serde_json::from_slice(&request).unwrap();
        changed.expected.static_value = Rational::ZERO;
        assert_eq!(
            receive_json(&serde_json::to_vec(&changed).unwrap(), &proposal, 512).status,
            Status::Rejected
        );
    }
}
