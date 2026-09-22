//! The declared signature, the prefix-application grammar, and the check that
//! makes a rename a *term homomorphism*.
//!
//! This is the field that replaces the prose `scope`.  The point is narrow and
//! it is the whole point: a rename induced by a tokenwise substitution is a
//! homomorphism of the term algebra only if it maps every operator token to an
//! operator token **of the same arity**.  A rename that moves `*` to an atom
//! token silently changes arity, and then the "renamed" source is not the image
//! of the original under any homomorphism at all.

use std::collections::{BTreeMap, BTreeSet};

/// What a token is in the signature.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Operator(usize),
    Atom,
}

impl Kind {
    fn arity(self) -> usize {
        match self {
            Kind::Operator(n) => n,
            Kind::Atom => 0,
        }
    }

    fn describe(self) -> String {
        match self {
            Kind::Operator(n) => format!("operator/{n}"),
            Kind::Atom => "atom".to_string(),
        }
    }
}

/// The signature a source is parsed by and a rename must respect.
#[derive(Clone, Debug)]
pub struct Signature {
    /// operator token -> arity
    pub operators: BTreeMap<char, usize>,
    /// leaf tokens
    pub atoms: BTreeSet<char>,
    /// tokens carrying no structure, dropped before parsing
    pub ignored: BTreeSet<char>,
}

impl Signature {
    pub fn kind(&self, token: char) -> Option<Kind> {
        if let Some(&arity) = self.operators.get(&token) {
            Some(Kind::Operator(arity))
        } else if self.atoms.contains(&token) {
            Some(Kind::Atom)
        } else {
            None
        }
    }
}

/// A reason a declared rename is not a signature homomorphism.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum SignatureViolation {
    /// A moved token is not in the declared signature.
    SourceTokenUnknown { token: char },
    /// A moved token's image is not in the declared signature.
    TargetTokenUnknown { token: char, target: char },
    /// Operator arity changed, or an operator became an atom or vice versa.
    KindChanged {
        token: char,
        from: String,
        to: String,
    },
    /// An operator the declaration claims to fix is moved anyway.
    FixedOperatorMoved { token: char, target: char },
    /// The declaration claims to fix a token that is not an operator.
    FixedTokenIsNotAnOperator { token: char },
    /// Two moved tokens collide on one target, so the map is not injective.
    TargetCollision {
        target: char,
        first: char,
        second: char,
    },
}

/// Check that `pairs` induces a signature homomorphism.
///
/// `pairs` maps an old token to its new spelling; only the tokens it mentions
/// move.  Returns every violation found, in a deterministic order, so a run
/// reports the whole diagnosis rather than the first symptom.
pub fn check_signature_homomorphism(
    signature: &Signature,
    pairs: &BTreeMap<char, char>,
    fixed_operators: &BTreeSet<char>,
) -> Vec<SignatureViolation> {
    let mut violations = Vec::new();

    for (&token, &target) in pairs {
        match signature.kind(token) {
            None => {
                violations.push(SignatureViolation::SourceTokenUnknown { token });
                continue;
            }
            Some(from) => match signature.kind(target) {
                None => violations.push(SignatureViolation::TargetTokenUnknown { token, target }),
                Some(to) => {
                    if from.arity() != to.arity() || from != to {
                        violations.push(SignatureViolation::KindChanged {
                            token,
                            from: from.describe(),
                            to: to.describe(),
                        });
                    }
                }
            },
        }
    }

    for &token in fixed_operators {
        if !signature.operators.contains_key(&token) {
            violations.push(SignatureViolation::FixedTokenIsNotAnOperator { token });
            continue;
        }
        if let Some(&target) = pairs.get(&token) {
            if target != token {
                violations.push(SignatureViolation::FixedOperatorMoved { token, target });
            }
        }
    }

    // injectivity of the declared map
    let mut seen: BTreeMap<char, char> = BTreeMap::new();
    for (&token, &target) in pairs {
        if let Some(&first) = seen.get(&target) {
            violations.push(SignatureViolation::TargetCollision {
                target,
                first,
                second: token,
            });
        } else {
            seen.insert(target, token);
        }
    }

    violations
}

/// A parsed source, keeping leaf tokens so two spellings can be compared.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Shape {
    Leaf(char),
    App(Box<Shape>, Box<Shape>),
}

impl Shape {
    /// Apply a token map to every leaf.
    pub fn relabel(&self, pairs: &BTreeMap<char, char>) -> Shape {
        match self {
            Shape::Leaf(t) => Shape::Leaf(pairs.get(t).copied().unwrap_or(*t)),
            Shape::App(l, r) => Shape::App(Box::new(l.relabel(pairs)), Box::new(r.relabel(pairs))),
        }
    }

    pub fn leaves(&self) -> usize {
        match self {
            Shape::Leaf(_) => 1,
            Shape::App(l, r) => l.leaves() + r.leaves(),
        }
    }

    pub fn nodes(&self) -> usize {
        match self {
            Shape::Leaf(_) => 1,
            Shape::App(l, r) => 1 + l.nodes() + r.nodes(),
        }
    }

    /// A compact canonical text form, used in evidence rather than in identity.
    pub fn render(&self) -> String {
        match self {
            Shape::Leaf(t) => t.to_string(),
            Shape::App(l, r) => format!("({} {})", l.render(), r.render()),
        }
    }
}

/// Parse a source under a signature.  The grammar is the murphy one:
/// `term ::= atom | operator term...` with the operator's declared arity, which
/// is what makes the arity check above load-bearing rather than decorative.
pub fn parse(source: &str, signature: &Signature) -> Result<Shape, String> {
    let tokens: Vec<char> = source
        .chars()
        .filter(|c| !signature.ignored.contains(c))
        .collect();
    let mut cursor = 0usize;
    let shape = parse_term(&tokens, &mut cursor, signature, 0)?;
    if cursor != tokens.len() {
        return Err(format!(
            "trailing source at token offset {cursor} of {}",
            tokens.len()
        ));
    }
    Ok(shape)
}

fn parse_term(
    tokens: &[char],
    cursor: &mut usize,
    signature: &Signature,
    depth: usize,
) -> Result<Shape, String> {
    if depth > 512 {
        return Err("source nesting exceeds the declared parse depth".to_string());
    }
    let Some(&token) = tokens.get(*cursor) else {
        return Err("end of source inside a term".to_string());
    };
    match signature.kind(token) {
        Some(Kind::Atom) => {
            *cursor += 1;
            Ok(Shape::Leaf(token))
        }
        Some(Kind::Operator(arity)) => {
            *cursor += 1;
            let mut children = Vec::with_capacity(arity);
            for _ in 0..arity {
                children.push(parse_term(tokens, cursor, signature, depth + 1)?);
            }
            let mut shape = children.remove(0);
            for child in children {
                shape = Shape::App(Box::new(shape), Box::new(child));
            }
            Ok(shape)
        }
        None => Err(format!("unsupported token {token:?}")),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn murphy_signature() -> Signature {
        Signature {
            operators: BTreeMap::from([('*', 2)]),
            atoms: BTreeSet::from(['i']),
            ignored: BTreeSet::from(['\n']),
        }
    }

    /// The signature of a *dialect pair*: both spellings are terms of it, and
    /// the rename moves one atom to the other.  A renamed source cannot be
    /// parsed by a signature that only knows the old spelling.
    fn murphy_dialect_pair() -> Signature {
        Signature {
            operators: BTreeMap::from([('*', 2)]),
            atoms: BTreeSet::from(['i', '\u{3b9}']),
            ignored: BTreeSet::from(['\n']),
        }
    }

    #[test]
    fn the_prefix_grammar_parses_and_keeps_leaves() {
        let signature = murphy_signature();
        let shape = parse("*ii", &signature).unwrap();
        assert_eq!(shape.render(), "(i i)");
        assert_eq!(shape.leaves(), 2);
        assert_eq!(shape.nodes(), 3);
    }

    #[test]
    fn renaming_the_atom_keeps_the_shape() {
        let signature = murphy_dialect_pair();
        let pairs = BTreeMap::from([('i', '\u{3b9}')]);
        let original = parse("*ii", &signature).unwrap();
        let renamed = parse("*\u{3b9}\u{3b9}", &signature).unwrap();
        assert_eq!(renamed, original.relabel(&pairs));
    }

    #[test]
    fn a_signature_that_knows_only_the_old_spelling_cannot_read_the_new_one() {
        // this is why the declaration must carry the signature of the pair, not
        // of one spelling: otherwise the "renamed" source does not parse at all
        let only_documentary = murphy_signature();
        assert!(parse("*\u{3b9}\u{3b9}", &only_documentary).is_err());
    }

    #[test]
    fn renaming_the_operator_is_a_kind_change_not_a_respelling() {
        let signature = murphy_signature();
        let pairs = BTreeMap::from([('*', 'i')]);
        let violations = check_signature_homomorphism(&signature, &pairs, &BTreeSet::new());
        assert!(matches!(
            violations.as_slice(),
            [SignatureViolation::KindChanged { token: '*', .. }]
        ));
        // and the substituted source no longer parses as the same shape
        assert!(parse("iii", &signature).is_err());
    }

    #[test]
    fn a_claimed_fixed_operator_that_moves_is_a_violation() {
        let signature = Signature {
            operators: BTreeMap::from([('*', 2), ('\u{22c5}', 2)]),
            atoms: BTreeSet::from(['i']),
            ignored: BTreeSet::new(),
        };
        let pairs = BTreeMap::from([('*', '\u{22c5}')]);
        let fixed = BTreeSet::from(['*']);
        let violations = check_signature_homomorphism(&signature, &pairs, &fixed);
        assert!(
            violations
                .iter()
                .any(|v| matches!(v, SignatureViolation::FixedOperatorMoved { .. }))
        );
    }
}
