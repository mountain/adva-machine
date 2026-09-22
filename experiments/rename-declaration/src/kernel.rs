//! The published kernel witness.
//!
//! "This rename is presentation-only" is a claim about **one** map.  What a
//! reader needs in order to judge it is the complementary claim about the
//! **relation set**: which renames does the recorded relation set fail to tell
//! apart at all?  That class is the kernel, and publishing it is the difference
//! between verification and self-congratulation.
//!
//! The renames of a name universe are not a group here.  `i -> iota` is an
//! injective substitution whose target lies outside the source alphabet, so it
//! is a *partial* bijection: the algebraic home is the symmetric inverse monoid
//! `I_X`, not `Sym(X)`, and the kernel of a monoid homomorphism is a
//! congruence rather than a normal subgroup.

use std::collections::{BTreeMap, BTreeSet};

/// A renaming, as a partial bijection of a name universe.
pub type Renaming = BTreeMap<char, char>;

/// `I_n` = sum over k of C(n,k)^2 k!, the order of the symmetric inverse monoid.
pub fn inverse_monoid_order(n: usize) -> usize {
    fn choose(n: usize, k: usize) -> usize {
        let mut out = 1usize;
        for i in 0..k {
            out = out * (n - i) / (i + 1);
        }
        out
    }
    fn factorial(k: usize) -> usize {
        (1..=k).product::<usize>().max(1)
    }
    (0..=n)
        .map(|k| choose(n, k) * choose(n, k) * factorial(k))
        .sum()
}

/// Every partial bijection of `universe`, up to a declared bound.
///
/// Returns `None` when the universe exceeds the bound, so an over-large request
/// is reported as Unknown instead of silently truncated.
pub fn enumerate_partial_bijections(universe: &[char], bound: usize) -> Option<Vec<Renaming>> {
    if universe.len() > bound {
        return None;
    }
    let mut out = Vec::new();
    let mut current = Renaming::new();
    let mut used = BTreeSet::new();
    walk(universe, 0, &mut current, &mut used, &mut out);
    out.sort_by_key(|r| {
        r.iter()
            .map(|(&k, &v)| format!("{k}->{v}"))
            .collect::<Vec<_>>()
    });
    Some(out)
}

fn walk(
    universe: &[char],
    index: usize,
    current: &mut Renaming,
    used: &mut BTreeSet<char>,
    out: &mut Vec<Renaming>,
) {
    if index == universe.len() {
        out.push(current.clone());
        return;
    }
    let token = universe[index];
    // leave this token unmoved and unmapped
    walk(universe, index + 1, current, used, out);
    for &target in universe {
        if used.contains(&target) {
            continue;
        }
        current.insert(token, target);
        used.insert(target);
        walk(universe, index + 1, current, used, out);
        current.remove(&token);
        used.remove(&target);
    }
}

/// Compose partial bijections: apply `inner`, then `outer`.
pub fn compose(outer: &Renaming, inner: &Renaming) -> Renaming {
    let mut out = Renaming::new();
    for (&token, &image) in inner {
        if let Some(&final_image) = outer.get(&image) {
            out.insert(token, final_image);
        }
    }
    out
}

pub fn is_identity(renaming: &Renaming) -> bool {
    renaming.iter().all(|(&k, &v)| k == v)
}

/// Does this renaming move any token in `tokens`?
pub fn moves_any_of(renaming: &Renaming, tokens: &BTreeSet<char>) -> bool {
    renaming
        .iter()
        .any(|(&k, &v)| k != v && (tokens.contains(&k) || tokens.contains(&v)))
}

/// Would this renaming collide with a token already in the source?
///
/// The rule is the one the repository already declares: a moved token may not
/// land on a token that occurs in the source and is not itself moved, because
/// then the newcomers and the incumbents become indistinguishable.  Imposing it
/// on the enumerated set matters: without it the kernel fills with renames that
/// are invisible only because their domain never occurs in the source, while
/// their target is a token that does.
pub fn collision_free(renaming: &Renaming, source_tokens: &BTreeSet<char>) -> bool {
    !renaming
        .iter()
        .any(|(&k, &v)| k != v && source_tokens.contains(&v) && !renaming.contains_key(&v))
}

/// Is the set closed under composition and abelian?  `None` above the bound.
pub fn abelian(renamings: &[Renaming], bound: usize) -> Option<bool> {
    if renamings.len() > bound {
        return None;
    }
    for a in renamings {
        for b in renamings {
            if compose(a, b) != compose(b, a) {
                return Some(false);
            }
        }
    }
    Some(true)
}

/// What a relation set can and cannot see, over one name universe.
#[derive(Clone, Debug)]
pub struct KernelWitness {
    pub relation_set: String,
    /// the level the rename acts at, and the level this relation set measures at
    pub acting_level: String,
    pub measuring_level: String,
    /// true when the two differ, which makes the witness a cross-level statement
    pub cross_level: bool,
    pub universe: Vec<char>,
    pub universe_size: usize,
    pub monoid_order: usize,
    /// renames that are signature-legal and collision-free over this source
    pub admissible: usize,
    /// renames the relation set's verdict separates from the identity
    pub visible: usize,
    /// renames it cannot separate
    pub kernel: usize,
    pub kernel_is_total: bool,
    /// is that kernel abelian?  `None` when it exceeds the declared bound
    pub kernel_is_abelian: Option<bool>,
    /// kernel members that move nothing at all, a sub-kernel every relation
    /// set contains
    pub kernel_moving_nothing: usize,
    /// the kernel restricted to renames whose domain or image meets the source
    pub kernel_touching_the_source: Vec<String>,
    /// a bounded sample of the kernel, retained rather than merely counted
    pub kernel_sample: Vec<String>,
    pub non_abelian_kernel_witness: Option<[String; 2]>,
}

pub fn render(renaming: &Renaming) -> String {
    if renaming.is_empty() {
        return "<empty>".to_string();
    }
    renaming
        .iter()
        .map(|(&k, &v)| format!("{k}->{v}"))
        .collect::<Vec<_>>()
        .join(",")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_inverse_monoid_orders_match_the_closed_form() {
        assert_eq!(inverse_monoid_order(0), 1);
        assert_eq!(inverse_monoid_order(1), 2);
        assert_eq!(inverse_monoid_order(2), 7);
        assert_eq!(inverse_monoid_order(3), 34);
        assert_eq!(inverse_monoid_order(4), 209);
        assert_eq!(inverse_monoid_order(6), 13327);
    }

    #[test]
    fn enumeration_agrees_with_the_closed_form() {
        for n in 0..=4 {
            let universe: Vec<char> = ('a'..='z').take(n).collect();
            let found = enumerate_partial_bijections(&universe, 4).unwrap();
            assert_eq!(found.len(), inverse_monoid_order(n), "n = {n}");
        }
    }

    #[test]
    fn an_over_large_universe_is_unknown_not_truncated() {
        let universe: Vec<char> = ('a'..='z').take(7).collect();
        assert!(enumerate_partial_bijections(&universe, 6).is_none());
    }

    #[test]
    fn the_monoid_of_three_names_is_not_abelian() {
        let universe = ['a', 'b', 'c'];
        let all = enumerate_partial_bijections(&universe, 6).unwrap();
        assert_eq!(all.len(), 34);
        assert_eq!(abelian(&all, 100), Some(false));
    }

    fn substitute(text: &str, renaming: &Renaming) -> String {
        text.chars()
            .map(|c| renaming.get(&c).copied().unwrap_or(c))
            .collect()
    }

    #[test]
    fn the_monoid_product_is_not_sequential_substitution() {
        // One declared pair set {i -> j, j -> iota} can be read three ways, and
        // the three readings disagree.  "Apply the declared renames in order"
        // therefore has no algebraic justification: read sequentially it is not
        // the inverse-monoid product, and read as a product it is not what the
        // declaration says.
        let sigma = Renaming::from([('i', 'j')]);
        let tau = Renaming::from([('j', '\u{3b9}')]);
        let declared: Renaming = sigma
            .iter()
            .chain(tau.iter())
            .map(|(&k, &v)| (k, v))
            .collect();
        let product = compose(&tau, &sigma);
        assert_eq!(product, Renaming::from([('i', '\u{3b9}')]));

        let simultaneous = substitute("ij", &declared);
        let as_a_product = substitute("ij", &product);
        let sequential = substitute(&substitute("ij", &sigma), &tau);

        assert_eq!(simultaneous, "j\u{3b9}");
        assert_eq!(as_a_product, "\u{3b9}j");
        assert_eq!(sequential, "\u{3b9}\u{3b9}");
        let distinct: BTreeSet<&String> = [&simultaneous, &as_a_product, &sequential]
            .into_iter()
            .collect();
        assert_eq!(distinct.len(), 3, "the three readings must differ");
    }
}
