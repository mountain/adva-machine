//! A tiny finite algebra over permutation tuples.
//!
//! It exists only to evaluate the declared word-equation relation sets.  No
//! third-party algebra library is used, so the numbers a run reports depend on
//! this file alone.
//!
//! Convention: `p[i]` is the image of `i`, and `a.compose(&b)` applies `b`
//! first, then `a`.  Word evaluation multiplies left to right in that order.

use std::collections::BTreeMap;

/// A permutation of `0..degree`, stored by images.
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub struct Perm(pub Vec<usize>);

impl Perm {
    pub fn identity(degree: usize) -> Self {
        Perm((0..degree).collect())
    }

    pub fn compose(&self, other: &Self) -> Self {
        Perm(other.0.iter().map(|&j| self.0[j]).collect())
    }

    #[cfg(test)]
    pub fn pow(&self, exponent: usize) -> Self {
        let mut out = Perm::identity(self.0.len());
        for _ in 0..exponent {
            out = out.compose(self);
        }
        out
    }

    /// The multiplicative order of this element, for the order profile.
    pub fn order(&self) -> usize {
        let mut k = 1;
        let mut p = self.clone();
        let eye = Perm::identity(self.0.len());
        while p != eye {
            p = p.compose(self);
            k += 1;
        }
        k
    }
}

/// A finite algebra: named elements acting as permutations of one degree.
#[derive(Clone, Debug)]
pub struct Algebra {
    pub degree: usize,
    pub elements: BTreeMap<String, Perm>,
}

impl Algebra {
    pub fn new(degree: usize, elements: BTreeMap<String, Perm>) -> Self {
        Algebra { degree, elements }
    }

    /// Evaluate a word: a left-to-right product of the denotations of its
    /// letters.  `None` if a letter has no denotation or a denotation names no
    /// element.
    pub fn eval(&self, word: &str, denotation: &BTreeMap<char, String>) -> Option<Perm> {
        let mut out = Perm::identity(self.degree);
        for letter in word.chars() {
            let element = denotation.get(&letter)?;
            let perm = self.elements.get(element)?;
            if perm.0.len() != self.degree {
                return None;
            }
            out = out.compose(perm);
        }
        Some(out)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn compose_applies_the_right_operand_first() {
        // swap01 then swap12 is the 3-cycle 0 -> 2 -> 1 -> 0
        let swap01 = Perm(vec![1, 0, 2]);
        let swap12 = Perm(vec![0, 2, 1]);
        assert_eq!(swap12.compose(&swap01), Perm(vec![2, 0, 1]));
        assert_eq!(swap01.compose(&swap12), Perm(vec![1, 2, 0]));
        // and the two orders genuinely differ: composition is not commutative
        assert_ne!(swap12.compose(&swap01), swap01.compose(&swap12));
    }

    #[test]
    fn the_three_cycle_has_order_three() {
        assert_eq!(Perm(vec![1, 2, 0]).order(), 3);
        assert_eq!(Perm(vec![1, 2, 0]).pow(3), Perm::identity(3));
    }
}
