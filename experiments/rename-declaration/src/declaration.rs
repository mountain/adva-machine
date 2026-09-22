//! Loading a rename declaration and checking it.
//!
//! Two things happen here that the current `declared_map` cannot do:
//!
//! 1. `scope`, today a prose string, is replaced by a declared **signature**
//!    plus a **fixed operator set**, and the checker verifies that the declared
//!    map is a signature homomorphism.  That is what makes the induced map on
//!    terms well defined, and hence what makes the kernel a congruence rather
//!    than an accident.
//! 2. Every relation set is required to carry its own **name universe**, so the
//!    kernel witness is a statement about a definite finite set of renames
//!    instead of an unquantified claim.

use crate::algebra::Algebra;
use crate::grammar::{Shape, Signature, check_signature_homomorphism, parse};
use crate::kernel::{
    KernelWitness, Renaming, abelian, collision_free, compose, enumerate_partial_bijections,
    inverse_monoid_order, is_identity, moves_any_of, render,
};
use crate::level::{Level, LevelSpec, check_level, structural_legal};
use serde::Deserialize;
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Debug, Deserialize)]
pub struct SignatureSpec {
    pub operators: BTreeMap<String, usize>,
    #[serde(default)]
    pub atoms: Vec<String>,
    #[serde(default)]
    pub ignored: Vec<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct RenameSpec {
    pub pairs: BTreeMap<String, String>,
    #[serde(default)]
    pub fixed_operators: Vec<String>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct SourceSpec {
    /// A short hand-written fixture source, embedded.  Mutually exclusive with
    /// `path`.
    #[serde(default)]
    pub text: Option<String>,
    /// A path to bytes that live elsewhere in the repository, resolved against
    /// `--root`.  The murphy unit is declared this way so that the run reads the
    /// received bytes instead of a copy of them.
    #[serde(default)]
    pub path: Option<String>,
    /// the digest for those bytes.  Verified in both cases, so "these are the
    /// bytes the declaration is about" is a check rather than a claim: for a
    /// path it is the digest recorded for the unit, and for an embedded source
    /// it pins the fixture bytes against later drift.
    pub sha256: String,
    /// where that digest comes from
    pub provenance: String,
}

/// Does the declared digest match what was read?
pub fn verify_digest(declared: &str, actual: &str) -> bool {
    declared.trim().eq_ignore_ascii_case(actual.trim())
}

/// How a rename is read against a word-equation relation set.  The three
/// readings are not variants of one idea; they differ in whether the rename is
/// read as a respelling or as a change of meaning, and they give different
/// answers to the same question.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Reading {
    /// Relabel the equation words *and* move the denotation coherently, so that
    /// the new symbol denotes what the old one denoted.  This is the Tietze
    /// reading, and every rename of the generators preserves the presented
    /// structure under it -- so its verdict can never fail, and the kernel it
    /// publishes is the whole admissible set.  It is the reading under which
    /// "this rename is presentation-only" is true by construction and therefore
    /// certifies nothing.
    Tietze,
    /// Relabel the words and hold the denotation fixed.  A symbol keeps its old
    /// meaning while its spelling changes, which is a corruption rather than a
    /// respelling; most renames fail it.
    WordsRelabelled,
    /// Hold the words fixed and move what each name denotes.  A name is bound to
    /// a role and the rename moves the role; most renames fail it.
    DenotationMoved,
}

#[derive(Clone, Debug, Deserialize)]
pub struct AlgebraSpec {
    pub degree: usize,
    pub elements: BTreeMap<String, Vec<usize>>,
}

#[derive(Clone, Debug, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum RelationSetSpec {
    /// The relation is: the source spelling is unchanged.
    SpellingFixed {
        id: String,
        universe: Vec<String>,
        bound: usize,
        #[serde(default)]
        level: Option<Level>,
    },
    /// The relation is: every declared word equation holds.
    WordEquations {
        id: String,
        universe: Vec<String>,
        bound: usize,
        #[serde(default)]
        level: Option<Level>,
        reading: Reading,
        algebra: AlgebraSpec,
        denotation: BTreeMap<String, String>,
        equations: Vec<(String, String)>,
    },
    /// The relation is: every declared label keeps its declared count.  This is
    /// the combinator level's typical measurement, and the counts a declaration
    /// uses should come from frozen evidence rather than from a recomputation.
    LabelCountsFixed {
        id: String,
        universe: Vec<String>,
        bound: usize,
        #[serde(default)]
        level: Option<Level>,
        counts: BTreeMap<String, usize>,
    },
}

impl RelationSetSpec {
    fn id(&self) -> &str {
        match self {
            RelationSetSpec::SpellingFixed { id, .. } => id,
            RelationSetSpec::WordEquations { id, .. } => id,
            RelationSetSpec::LabelCountsFixed { id, .. } => id,
        }
    }

    fn universe(&self) -> &[String] {
        match self {
            RelationSetSpec::SpellingFixed { universe, .. } => universe,
            RelationSetSpec::WordEquations { universe, .. } => universe,
            RelationSetSpec::LabelCountsFixed { universe, .. } => universe,
        }
    }

    fn bound(&self) -> usize {
        match self {
            RelationSetSpec::SpellingFixed { bound, .. } => *bound,
            RelationSetSpec::WordEquations { bound, .. } => *bound,
            RelationSetSpec::LabelCountsFixed { bound, .. } => *bound,
        }
    }

    /// The level this relation set measures at.  A relation set that declares
    /// none measures at the level the rename acts at; one that declares another
    /// is a cross-level measurement, which the run reports rather than hides.
    fn level(&self, acting: Level) -> Level {
        match self {
            RelationSetSpec::SpellingFixed { level, .. } => level.unwrap_or(acting),
            RelationSetSpec::WordEquations { level, .. } => level.unwrap_or(acting),
            RelationSetSpec::LabelCountsFixed { level, .. } => level.unwrap_or(acting),
        }
    }

    /// The tokens a rename may not land on without also moving them.
    ///
    /// This is the occupied set the collision rule is relative to, and it is
    /// per relation set: re-spelling a source collides with the source, while
    /// re-spelling an equation collides with the letters the equation uses.
    /// Tietze's generator replacement is legal only for a *fresh* symbol, and
    /// that freshness is exactly this set.
    fn occupied_tokens(&self, source: &str) -> BTreeSet<char> {
        match self {
            RelationSetSpec::SpellingFixed { .. } => source.chars().collect(),
            RelationSetSpec::WordEquations { equations, .. } => equations
                .iter()
                .flat_map(|(l, r)| l.chars().chain(r.chars()))
                .collect(),
            RelationSetSpec::LabelCountsFixed { counts, .. } => {
                counts.keys().flat_map(|label| label.chars()).collect()
            }
        }
    }
}

#[derive(Clone, Debug, Deserialize)]
pub struct Declaration {
    pub schema: String,
    pub name: String,
    /// the level the rename acts at, with that level's distinguishing structure
    pub level: LevelSpec,
    pub signature: SignatureSpec,
    pub rename: RenameSpec,
    pub source: SourceSpec,
    pub relation_sets: Vec<RelationSetSpec>,
}

fn single_char_list(items: &[String], what: &str) -> Result<Vec<char>, String> {
    items
        .iter()
        .map(|s| {
            let mut chars = s.chars();
            match (chars.next(), chars.next()) {
                (Some(c), None) => Ok(c),
                _ => Err(format!("{what} entry {s:?} is not a single character")),
            }
        })
        .collect()
}

fn single_char_map(
    items: &BTreeMap<String, String>,
    what: &str,
) -> Result<BTreeMap<char, char>, String> {
    let mut out = BTreeMap::new();
    for (k, v) in items {
        let mut kc = k.chars();
        let mut vc = v.chars();
        match (kc.next(), kc.next(), vc.next(), vc.next()) {
            (Some(a), None, Some(b), None) => {
                out.insert(a, b);
            }
            _ => {
                return Err(format!(
                    "{what} entry {k:?} -> {v:?} is not single characters"
                ));
            }
        }
    }
    Ok(out)
}

/// A renaming is legal if every token it moves *that the signature knows* moves
/// legally.  Tokens outside the signature are not terms of this algebra, so a
/// relation set over a different alphabet is not constrained by it.
fn signature_legal(signature: &Signature, fixed: &BTreeSet<char>, renaming: &Renaming) -> bool {
    let relevant: BTreeMap<char, char> = renaming
        .iter()
        .filter(|(k, _)| signature.kind(**k).is_some())
        .map(|(&k, &v)| (k, v))
        .collect();
    relevant.is_empty() || check_signature_homomorphism(signature, &relevant, fixed).is_empty()
}

fn relabel_word(word: &str, renaming: &Renaming) -> String {
    word.chars()
        .map(|c| renaming.get(&c).copied().unwrap_or(c))
        .collect()
}

fn relabel_text(text: &str, renaming: &Renaming) -> String {
    text.chars()
        .map(|c| renaming.get(&c).copied().unwrap_or(c))
        .collect()
}

/// The declared relation set's verdict for one renaming.
fn verdict(
    spec: &RelationSetSpec,
    renaming: &Renaming,
    source: &str,
    algebra: Option<&Algebra>,
    denotation: Option<&BTreeMap<char, String>>,
) -> Result<bool, String> {
    match spec {
        RelationSetSpec::SpellingFixed { .. } => Ok(relabel_text(source, renaming) == source),
        RelationSetSpec::LabelCountsFixed { counts, .. } => {
            // each label keeps its declared count, under the relabelled spelling
            let mut relabelled: BTreeMap<String, usize> = BTreeMap::new();
            for (label, count) in counts {
                let mapped: String = label
                    .chars()
                    .map(|c| renaming.get(&c).copied().unwrap_or(c))
                    .collect();
                relabelled.insert(mapped, *count);
            }
            Ok(&relabelled == counts)
        }
        RelationSetSpec::WordEquations {
            reading, equations, ..
        } => {
            let algebra = algebra.ok_or("missing algebra")?;
            let denotation = denotation.ok_or("missing denotation")?;
            match reading {
                Reading::Tietze => {
                    // the new symbol denotes what the old one denoted, so the
                    // relabelled word evaluates to exactly what the original did
                    let coherent: BTreeMap<char, String> = denotation
                        .iter()
                        .map(|(&name, element)| match renaming.get(&name) {
                            Some(&t) => (
                                t,
                                denotation
                                    .get(&name)
                                    .cloned()
                                    .unwrap_or_else(|| element.clone()),
                            ),
                            None => (name, element.clone()),
                        })
                        .collect();
                    for (left, right) in equations {
                        let l = relabel_word(left, renaming);
                        let r = relabel_word(right, renaming);
                        if algebra.eval(&l, &coherent) != algebra.eval(&r, &coherent) {
                            return Ok(false);
                        }
                    }
                    Ok(true)
                }
                Reading::WordsRelabelled => {
                    for (left, right) in equations {
                        let l = relabel_word(left, renaming);
                        let r = relabel_word(right, renaming);
                        if algebra.eval(&l, denotation) != algebra.eval(&r, denotation) {
                            return Ok(false);
                        }
                    }
                    Ok(true)
                }
                Reading::DenotationMoved => {
                    // the symbol Y now carries the role of the old symbol that
                    // was moved onto it, so this is the inverse direction of the
                    // map.  Writing it this way makes the reading identical to
                    // the check in naming-probe-01/probe.py, so the two agree by
                    // construction rather than by coincidence.
                    let mut inverse: BTreeMap<char, char> = BTreeMap::new();
                    for (&from, &to) in renaming {
                        inverse.insert(to, from);
                    }
                    let moved: BTreeMap<char, String> = denotation
                        .iter()
                        .map(|(&name, element)| match inverse.get(&name) {
                            Some(&old) => (
                                name,
                                denotation
                                    .get(&old)
                                    .cloned()
                                    .unwrap_or_else(|| element.clone()),
                            ),
                            None => (name, element.clone()),
                        })
                        .collect();
                    for (left, right) in equations {
                        if algebra.eval(left, &moved) != algebra.eval(right, &moved) {
                            return Ok(false);
                        }
                    }
                    Ok(true)
                }
            }
        }
    }
}

/// Check one declaration and return its outcome as JSON.
pub fn check(declaration: &Declaration, root: &std::path::Path) -> Result<Value, String> {
    let (source_text, source_origin) = match (&declaration.source.text, &declaration.source.path) {
        (Some(text), None) => (text.clone(), "embedded".to_string()),
        (None, Some(relative)) => {
            let path = root.join(relative);
            let text = std::fs::read_to_string(&path)
                .map_err(|e| format!("reading {} as text: {e}", path.display()))?;
            (text, path.display().to_string())
        }
        _ => {
            return Err("a source declares exactly one of `text` or `path`".to_string());
        }
    };
    let actual_digest = crate::sha256::sha256_hex(source_text.as_bytes());
    let digest_verified = verify_digest(&declaration.source.sha256, &actual_digest);

    if declaration.schema != "adva.rename-declaration.v0" {
        return Err(format!(
            "unexpected declaration schema {:?}",
            declaration.schema
        ));
    }

    let ignored: BTreeSet<char> = single_char_list(&declaration.signature.ignored, "ignored")?
        .into_iter()
        .collect();
    let atoms: BTreeSet<char> = single_char_list(&declaration.signature.atoms, "atoms")?
        .into_iter()
        .collect();
    let mut operators = BTreeMap::new();
    for (token, arity) in &declaration.signature.operators {
        let chars = single_char_list(std::slice::from_ref(token), "operators")?;
        operators.insert(chars[0], *arity);
    }
    let signature = Signature {
        operators,
        atoms,
        ignored,
    };

    let pairs = single_char_map(&declaration.rename.pairs, "pairs")?;
    let fixed: BTreeSet<char> =
        single_char_list(&declaration.rename.fixed_operators, "fixed_operators")?
            .into_iter()
            .collect();

    // --- the signature check: this is the field that replaces prose `scope` ---
    let violations = check_signature_homomorphism(&signature, &pairs, &fixed);

    // --- the level check: this is the field that replaces prose `level` ---
    let signature_tokens: BTreeSet<char> = signature
        .operators
        .keys()
        .chain(signature.atoms.iter())
        .copied()
        .collect();
    let level_violations = check_level(&declaration.level, &pairs, &signature_tokens);
    let acting_level = declaration.level.acting;

    // --- source-level checks ---
    let original_shape: Option<Shape> = parse(&source_text, &signature).ok();
    let renamed_text = relabel_text(&source_text, &pairs);
    let renamed_shape: Option<Shape> = parse(&renamed_text, &signature).ok();
    let expected_shape = original_shape.as_ref().map(|s| s.relabel(&pairs));
    let image_holds = match (&renamed_shape, &expected_shape) {
        (Some(a), Some(b)) => a == b,
        _ => false,
    };

    // a target that already occurs in the source, and is not itself moved, is a
    // collision: the newcomers and the incumbents become indistinguishable
    let source_tokens: BTreeSet<char> = source_text.chars().collect();
    let collisions: Vec<Value> = pairs
        .iter()
        .filter(|(from, to)| from != to && source_tokens.contains(to) && !pairs.contains_key(to))
        .map(|(from, to)| json!({ "from": from.to_string(), "to": to.to_string() }))
        .collect();

    let source_changed = renamed_text != source_text;

    // --- kernel witnesses, one per declared relation set ---
    let mut witnesses: Vec<KernelWitness> = Vec::new();
    let mut unknown_reasons: Vec<String> = Vec::new();
    let mut algebra_profile: Option<Value> = None;

    for spec in &declaration.relation_sets {
        let universe_chars = single_char_list(spec.universe(), "universe")?;
        let Some(all) = enumerate_partial_bijections(&universe_chars, spec.bound()) else {
            unknown_reasons.push(format!(
                "relation set {:?}: universe of {} names exceeds the declared bound {}",
                spec.id(),
                universe_chars.len(),
                spec.bound()
            ));
            continue;
        };

        let algebra = match spec {
            RelationSetSpec::WordEquations { algebra, .. } => {
                let mut elements = BTreeMap::new();
                for (name, images) in &algebra.elements {
                    if images.len() != algebra.degree {
                        return Err(format!(
                            "algebra element {name:?} has {} images but declared degree {}",
                            images.len(),
                            algebra.degree
                        ));
                    }
                    elements.insert(name.clone(), crate::algebra::Perm(images.clone()));
                }
                // the element-order profile is a complete invariant for the
                // groups of order 8, so publishing it says which structure the
                // relation set was actually evaluated in
                if algebra_profile.is_none() {
                    let mut profile: BTreeMap<usize, usize> = BTreeMap::new();
                    for perm in elements.values() {
                        *profile.entry(perm.order()).or_insert(0) += 1;
                    }
                    algebra_profile = Some(json!({
                        "relation_set": spec.id(),
                        "degree": algebra.degree,
                        "element_order_profile": profile
                            .iter()
                            .map(|(k, v)| (k.to_string(), *v))
                            .collect::<BTreeMap<String, usize>>(),
                    }));
                }
                Some(Algebra::new(algebra.degree, elements))
            }
            RelationSetSpec::SpellingFixed { .. } | RelationSetSpec::LabelCountsFixed { .. } => {
                None
            }
        };
        let denotation = match spec {
            RelationSetSpec::WordEquations { denotation, .. } => Some(
                denotation
                    .iter()
                    .map(|(k, v)| {
                        let c = k
                            .chars()
                            .next()
                            .ok_or_else(|| format!("empty denotation key {k:?}"))?;
                        Ok((c, v.clone()))
                    })
                    .collect::<Result<BTreeMap<char, String>, String>>()?,
            ),
            RelationSetSpec::SpellingFixed { .. } | RelationSetSpec::LabelCountsFixed { .. } => {
                None
            }
        };

        let mut visible = 0usize;
        let mut kernel: Vec<Renaming> = Vec::new();
        let mut admissible = 0usize;
        let occupied = spec.occupied_tokens(&source_text);
        let measuring_level = spec.level(acting_level);
        for renaming in &all {
            if !signature_legal(&signature, &fixed, renaming) {
                continue;
            }
            if !structural_legal(&declaration.level, renaming) {
                continue;
            }
            if !collision_free(renaming, &occupied) {
                continue;
            }
            admissible += 1;
            let holds = verdict(
                spec,
                renaming,
                &source_text,
                algebra.as_ref(),
                denotation.as_ref(),
            )?;
            if holds {
                kernel.push(renaming.clone());
            } else {
                visible += 1;
            }
        }

        let touching: Vec<String> = kernel
            .iter()
            .filter(|r| moves_any_of(r, &source_tokens))
            .map(render)
            .collect();
        let sample: Vec<String> = kernel.iter().take(24).map(render).collect();
        let non_abelian = {
            let mut witness = None;
            'outer: for a in &kernel {
                for b in &kernel {
                    if compose(a, b) != compose(b, a) {
                        witness = Some([render(a), render(b)]);
                        break 'outer;
                    }
                }
            }
            witness
        };

        witnesses.push(KernelWitness {
            relation_set: spec.id().to_string(),
            acting_level: acting_level.as_str().to_string(),
            measuring_level: measuring_level.as_str().to_string(),
            cross_level: measuring_level != acting_level,
            universe: universe_chars.clone(),
            universe_size: universe_chars.len(),
            monoid_order: inverse_monoid_order(universe_chars.len()),
            admissible,
            visible,
            kernel: kernel.len(),
            kernel_is_total: visible == 0,
            kernel_is_abelian: abelian(&kernel, 512),
            kernel_moving_nothing: kernel.iter().filter(|r| is_identity(r)).count(),
            kernel_touching_the_source: touching,
            kernel_sample: sample,
            non_abelian_kernel_witness: non_abelian,
        });
    }

    // --- verdict ---
    let declared_renaming_is_legal = violations.is_empty();
    let declared_renaming_preserves_relations = {
        let mut ok = true;
        for spec in &declaration.relation_sets {
            let algebra = match spec {
                RelationSetSpec::WordEquations { algebra, .. } => {
                    let mut elements = BTreeMap::new();
                    for (name, images) in &algebra.elements {
                        elements.insert(name.clone(), crate::algebra::Perm(images.clone()));
                    }
                    Some(Algebra::new(algebra.degree, elements))
                }
                RelationSetSpec::SpellingFixed { .. }
                | RelationSetSpec::LabelCountsFixed { .. } => None,
            };
            let denotation = match spec {
                RelationSetSpec::WordEquations { denotation, .. } => Some(
                    denotation
                        .iter()
                        .map(|(k, v)| {
                            let c = k.chars().next().unwrap_or('?');
                            (c, v.clone())
                        })
                        .collect::<BTreeMap<char, String>>(),
                ),
                RelationSetSpec::SpellingFixed { .. }
                | RelationSetSpec::LabelCountsFixed { .. } => None,
            };
            // the declared rename must not be judged by a relation set it is
            // supposed to move: `spelling_fixed` asks whether the spelling is
            // unchanged, which a rename is precisely meant to change
            if matches!(spec, RelationSetSpec::SpellingFixed { .. }) {
                continue;
            }
            if !verdict(
                spec,
                &pairs,
                &source_text,
                algebra.as_ref(),
                denotation.as_ref(),
            )? {
                ok = false;
            }
        }
        ok
    };

    let declared_renaming = render(&pairs);
    let outcome = if !digest_verified {
        // the declaration is about bytes the run did not read, so nothing it
        // says about them can be checked
        "Refused"
    } else if !declared_renaming_is_legal
        || !level_violations.is_empty()
        || !image_holds
        || !collisions.is_empty()
    {
        "Refused"
    } else if !unknown_reasons.is_empty() {
        "Unknown"
    } else if !source_changed || !declared_renaming_preserves_relations {
        // a rename that moves nothing reports nothing, and a rename the
        // recorded relations can see is not presentation-only
        "Refused"
    } else {
        "Accepted"
    };

    let witness_json: Vec<Value> = witnesses
        .iter()
        .map(|w| {
            json!({
                "relation_set": w.relation_set,
                "acting_level": w.acting_level,
                "measuring_level": w.measuring_level,
                "cross_level": w.cross_level,
                "universe": w.universe.iter().map(|c| c.to_string()).collect::<Vec<_>>(),
                "universe_size": w.universe_size,
                "inverse_monoid_order": w.monoid_order,
                "admissible_renames": w.admissible,
                "visible_renames": w.visible,
                "kernel_order": w.kernel,
                "kernel_is_total": w.kernel_is_total,
                "kernel_is_abelian": w.kernel_is_abelian,
                "kernel_moving_nothing": w.kernel_moving_nothing,
                "kernel_fraction_of_admissible": if w.visible + w.kernel == 0 {
                    Value::Null
                } else {
                    json!(format!(
                        "{}/{}",
                        w.kernel,
                        w.visible + w.kernel
                    ))
                },
                "kernel_restricted_to_renames_touching_the_source":
                    w.kernel_touching_the_source,
                "kernel_sample": w.kernel_sample,
                "non_abelian_kernel_witness": w.non_abelian_kernel_witness,
            })
        })
        .collect();

    Ok(json!({
        "name": declaration.name,
        "level": {
            "acting": acting_level.as_str(),
            "declared_structure": {
                "primitive": &declaration.level.primitive,
                "derived": &declaration.level.derived,
                "identity_action": &declaration.level.identity_action,
                "changes_which_action_is_trivial":
                    declaration.level.changes_which_action_is_trivial,
            },
            "level_legal": level_violations.is_empty(),
            "level_violations": level_violations
                .iter()
                .map(|v| format!("{v:?}"))
                .collect::<Vec<_>>(),
        },
        "outcome": outcome,
        "source": {
            "origin": source_origin,
            "path": declaration.source.path,
            "provenance": declaration.source.provenance,
            "digest_declared": declaration.source.sha256,
            "digest_actual": actual_digest,
            "digest_verified": digest_verified,
            "tokens": source_text.chars().count(),
            "parses": original_shape.is_some(),
            "shape": original_shape.as_ref().map(Shape::render),
            "leaves": original_shape.as_ref().map(Shape::leaves),
            "nodes": original_shape.as_ref().map(Shape::nodes),
        },
        "declared_rename": {
            "pairs": declaration.rename.pairs,
            "fixed_operators": declaration.rename.fixed_operators,
            "rendered": declared_renaming,
            "signature_legal": declared_renaming_is_legal,
            "signature_violations": violations.iter().map(|v| format!("{v:?}")).collect::<Vec<_>>(),
            "image_of_the_source_holds": image_holds,
            "renamed_shape": renamed_shape.as_ref().map(Shape::render),
            "collisions": collisions,
            "spelling_changed": source_changed,
            "renamed_token_count": renamed_text.chars().count(),
        },
        "kernel_witnesses": witness_json,
        "algebra_profile": algebra_profile,
        "unknown_reasons": unknown_reasons,
    }))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn relabelling_a_word_replaces_mapped_letters_and_leaves_the_rest() {
        let pairs = BTreeMap::from([('C', 'J')]);
        // C maps to J; J is not in the map, so it is left alone
        assert_eq!(relabel_word("CJC", &pairs), "JJJ");
    }

    #[test]
    fn the_d8_algebra_evaluates_the_declared_laws() {
        let algebra = Algebra::new(
            4,
            BTreeMap::from([
                ("I".to_string(), crate::algebra::Perm(vec![0, 1, 2, 3])),
                ("C".to_string(), crate::algebra::Perm(vec![0, 3, 2, 1])),
                ("J".to_string(), crate::algebra::Perm(vec![1, 2, 3, 0])),
                ("N".to_string(), crate::algebra::Perm(vec![2, 3, 0, 1])),
            ]),
        );
        let denotation: BTreeMap<char, String> = ["C", "J", "N", "I"]
            .iter()
            .map(|s| (s.chars().next().unwrap(), s.to_string()))
            .collect();
        for (left, right) in [
            ("CC", "I"),
            ("JJ", "N"),
            ("JJJJ", "I"),
            ("CJC", "NJ"),
            ("NN", "I"),
        ] {
            assert_eq!(
                algebra.eval(left, &denotation),
                algebra.eval(right, &denotation),
                "{left} = {right}"
            );
        }
        // the retained negative witness: J squared is not the identity
        assert_ne!(
            algebra.eval("JJ", &denotation),
            algebra.eval("I", &denotation)
        );
    }

    #[test]
    fn even_the_two_name_inverse_monoid_is_not_abelian() {
        // {C->J} then {J->C} is {J->J}; the other order is {C->C}.  Partial
        // bijections with different domains fail to commute even when the
        // underlying permutations would commute, so non-commutativity arrives
        // at two names, not three.
        let universe = ['C', 'J'];
        let all = enumerate_partial_bijections(&universe, 4).unwrap();
        assert_eq!(all.len(), 7);
        assert!(all.iter().any(is_identity));
        assert_eq!(abelian(&all, 100), Some(false));

        let forward = Renaming::from([('C', 'J')]);
        let backward = Renaming::from([('J', 'C')]);
        assert_eq!(compose(&forward, &backward), Renaming::from([('J', 'J')]));
        assert_eq!(compose(&backward, &forward), Renaming::from([('C', 'C')]));
    }
}
