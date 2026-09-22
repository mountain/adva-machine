//! The checked level of a rename.
//!
//! `TRIADICITY-LEVEL-RULING.md` in the workspace ruled that triadicness belongs
//! to the **index/carrier** structure and not to the action layer, and it split
//! the picture into three levels with a different distinguishing structure at
//! each.  A naming mechanism that never says which level a name lives at is
//! therefore missing a leg, and a level that is a prose string is not part of
//! the mechanism at all.
//!
//! Each level has one distinguishing structure, and that is what makes the
//! level checkable rather than decorative:
//!
//! | level | distinguished by | what a rename must respect |
//! | --- | --- | --- |
//! | carrier | the signature | moved tokens are tokens of the declared signature |
//! | combinator | a derivation: one primitive introduces the others | the primitive/derived partition |
//! | action | one action is the identity | the identity action, unless the declaration says it is changing which action is trivial |
//!
//! The combinator row is the one the murphy evidence makes concrete: the
//! substrate's own comment says `j` is the Iota combinator and `S`, `K` and `I`
//! are the combinators the Iota rule introduces, while the frozen rule
//! histogram puts all four in one flat key space.  Renaming the primitive onto
//! a derived name is the combinator-level analogue of an arity change.

use std::collections::{BTreeMap, BTreeSet};

use crate::kernel::Renaming;

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, serde::Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Level {
    Carrier,
    Combinator,
    Action,
}

impl Level {
    pub fn as_str(self) -> &'static str {
        match self {
            Level::Carrier => "carrier",
            Level::Combinator => "combinator",
            Level::Action => "action",
        }
    }
}

/// What the declaration says about the level it acts at.
#[derive(Clone, Debug, serde::Deserialize)]
pub struct LevelSpec {
    pub acting: Level,
    /// combinator level: the labels the primitive introduces, and the primitive
    #[serde(default)]
    pub primitive: Vec<String>,
    #[serde(default)]
    pub derived: Vec<String>,
    /// action level: the one action that does nothing
    #[serde(default)]
    pub identity_action: Option<String>,
    /// action level: declares that the rename deliberately changes which action
    /// is trivial, which is a meaning change and not a respelling
    #[serde(default)]
    pub changes_which_action_is_trivial: bool,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum LevelViolation {
    /// The declaration acts at a level but names no structure for it.
    NoStructureDeclared { level: String },
    /// A moved token is not known at the declared acting level.
    TokenNotAtThisLevel { token: String, level: String },
    /// A label is declared both primitive and derived.
    PartitionOverlap { token: String },
    /// A moved label is in the declared label set but not in the partition.
    PartitionIncomplete { token: String },
    /// A primitive name was moved onto a derived name, or the reverse.
    PartitionNotPreserved {
        token: String,
        target: String,
        from: String,
        to: String,
    },
    /// The identity action was moved without the declaration saying so.
    IdentityActionMoved { action: String, target: String },
}

/// Check the declared rename against the structure of the level it acts at.
///
/// `signature_tokens` is every token the declared signature knows, which is
/// what the carrier level is relative to.
pub fn check_level(
    spec: &LevelSpec,
    pairs: &BTreeMap<char, char>,
    signature_tokens: &BTreeSet<char>,
) -> Vec<LevelViolation> {
    let mut violations = Vec::new();
    let moved: Vec<(String, String)> = pairs
        .iter()
        .filter(|(from, to)| from != to)
        .map(|(from, to)| (from.to_string(), to.to_string()))
        .collect();

    match spec.acting {
        Level::Carrier => {
            // the signature is the carrier's distinguishing structure, so every
            // moved token has to be one the signature knows
            if signature_tokens.is_empty() {
                violations.push(LevelViolation::NoStructureDeclared {
                    level: "carrier".to_string(),
                });
            }
            for (token, _) in &moved {
                let known = token
                    .chars()
                    .next()
                    .is_some_and(|c| signature_tokens.contains(&c));
                if !known {
                    violations.push(LevelViolation::TokenNotAtThisLevel {
                        token: token.clone(),
                        level: "carrier".to_string(),
                    });
                }
            }
        }
        Level::Combinator => {
            let primitive: BTreeSet<&String> = spec.primitive.iter().collect();
            let derived: BTreeSet<&String> = spec.derived.iter().collect();
            if primitive.is_empty() || derived.is_empty() {
                violations.push(LevelViolation::NoStructureDeclared {
                    level: "combinator".to_string(),
                });
            }
            for token in primitive.intersection(&derived) {
                violations.push(LevelViolation::PartitionOverlap {
                    token: (*token).clone(),
                });
            }
            let known: BTreeSet<&String> = primitive.union(&derived).copied().collect();
            for (token, target) in &moved {
                if !known.contains(token) {
                    violations.push(LevelViolation::PartitionIncomplete {
                        token: token.clone(),
                    });
                    continue;
                }
                if !known.contains(target) {
                    violations.push(LevelViolation::PartitionIncomplete {
                        token: target.clone(),
                    });
                    continue;
                }
                let from_is_primitive = primitive.contains(token);
                let to_is_primitive = primitive.contains(target);
                if from_is_primitive != to_is_primitive {
                    violations.push(LevelViolation::PartitionNotPreserved {
                        token: token.clone(),
                        target: target.clone(),
                        from: if from_is_primitive {
                            "primitive".to_string()
                        } else {
                            "derived".to_string()
                        },
                        to: if to_is_primitive {
                            "primitive".to_string()
                        } else {
                            "derived".to_string()
                        },
                    });
                }
            }
        }
        Level::Action => {
            // the action layer's distinguishing fact is that exactly one action
            // does nothing; moving it is a meaning change, not a respelling
            let Some(identity) = spec.identity_action.as_ref() else {
                violations.push(LevelViolation::NoStructureDeclared {
                    level: "action".to_string(),
                });
                return violations;
            };
            for (token, target) in &moved {
                if token == identity && !spec.changes_which_action_is_trivial {
                    violations.push(LevelViolation::IdentityActionMoved {
                        action: token.clone(),
                        target: target.clone(),
                    });
                }
            }
        }
    }
    violations
}

/// Is this enumerated renaming legal at the declared acting level?
///
/// Only the level-intrinsic structure is enforced here -- the combinator
/// partition and the action identity.  The carrier level's constraint is
/// relative to the declared signature and therefore applies to the *declared*
/// rename only; an enumerated renaming ranges over a relation set's universe,
/// which may legitimately sit at another level.
pub fn structural_legal(spec: &LevelSpec, renaming: &Renaming) -> bool {
    let pairs = renaming.clone();
    let violations = check_level(spec, &pairs, &BTreeSet::new());
    match spec.acting {
        Level::Carrier => true,
        Level::Combinator => !violations.iter().any(|v| {
            matches!(
                v,
                LevelViolation::PartitionNotPreserved { .. }
                    | LevelViolation::PartitionOverlap { .. }
                    | LevelViolation::PartitionIncomplete { .. }
            )
        }),
        Level::Action => !violations
            .iter()
            .any(|v| matches!(v, LevelViolation::IdentityActionMoved { .. })),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn spec_combinator() -> LevelSpec {
        LevelSpec {
            acting: Level::Combinator,
            primitive: vec!["j".to_string()],
            derived: vec!["S".to_string(), "K".to_string(), "I".to_string()],
            identity_action: None,
            changes_which_action_is_trivial: false,
        }
    }

    #[test]
    fn moving_the_primitive_onto_a_derived_name_is_a_level_violation() {
        let pairs = BTreeMap::from([('j', 'S')]);
        let violations = check_level(&spec_combinator(), &pairs, &BTreeSet::new());
        assert!(violations.iter().any(|v| matches!(
            v,
            LevelViolation::PartitionNotPreserved { token, .. } if token == "j"
        )));
    }

    #[test]
    fn permuting_within_the_derived_names_is_legal() {
        let pairs = BTreeMap::from([('S', 'K'), ('K', 'I'), ('I', 'S')]);
        let violations = check_level(&spec_combinator(), &pairs, &BTreeSet::new());
        assert!(violations.is_empty(), "{violations:?}");
    }

    #[test]
    fn moving_the_identity_action_needs_to_be_declared() {
        let mut spec = LevelSpec {
            acting: Level::Action,
            primitive: Vec::new(),
            derived: Vec::new(),
            identity_action: Some("i".to_string()),
            changes_which_action_is_trivial: false,
        };
        let pairs = BTreeMap::from([('i', 'm')]);
        assert!(
            check_level(&spec, &pairs, &BTreeSet::new())
                .iter()
                .any(|v| matches!(v, LevelViolation::IdentityActionMoved { .. }))
        );
        spec.changes_which_action_is_trivial = true;
        assert!(check_level(&spec, &pairs, &BTreeSet::new()).is_empty());
    }

    #[test]
    fn a_level_with_no_declared_structure_is_reported() {
        let spec = LevelSpec {
            acting: Level::Action,
            primitive: Vec::new(),
            derived: Vec::new(),
            identity_action: None,
            changes_which_action_is_trivial: false,
        };
        let violations = check_level(&spec, &BTreeMap::new(), &BTreeSet::new());
        assert!(
            violations
                .iter()
                .any(|v| matches!(v, LevelViolation::NoStructureDeclared { .. }))
        );
    }

    #[test]
    fn the_carrier_level_is_relative_to_the_declared_signature() {
        let spec = LevelSpec {
            acting: Level::Carrier,
            primitive: Vec::new(),
            derived: Vec::new(),
            identity_action: None,
            changes_which_action_is_trivial: false,
        };
        let signature: BTreeSet<char> = ['i', '*'].into_iter().collect();
        let pairs = BTreeMap::from([('i', '\u{3b9}')]);
        assert!(check_level(&spec, &pairs, &signature).is_empty());
        let stray = BTreeMap::from([('z', 'q')]);
        assert!(
            check_level(&spec, &stray, &signature)
                .iter()
                .any(|v| matches!(v, LevelViolation::TokenNotAtThisLevel { .. }))
        );
    }
}
