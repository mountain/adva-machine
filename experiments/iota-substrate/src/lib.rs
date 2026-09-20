//! Research-local native Iota/S/K substrate.
//!
//! This crate deliberately lives outside Adva's stable semantic API. It adds no
//! `ValueType`, no `OperationSpec`, no registry entry, no IR version and no
//! `Seal`. It answers one narrow question: **can the machine natively parse and
//! reduce pure Iota source, and reproduce an externally frozen counting and
//! digest witness byte for byte, using only its own Rust source and no new
//! dependency?**
//!
//! The external witness is the `murphy` publication unit
//! (`mountain/adva`, `experiments/murphy`, admitted 2026-09-19). Its reducer is
//! an independent Python implementation with the declared rules
//!
//! ```text
//! iota:  j a       -> a S K
//! I:     I a       -> a
//! K:     K a b     -> a
//! S:     S x y z   -> x z (y z)
//! ```
//!
//! evaluated leftmost-outermost on combinator trees, counting one contraction
//! per applied combinator, with `nodes(t)` counting applications and leaves.
//! Its normal-form digest is SHA-256 over a canonical JSON encoding of the term
//! (`["a", f, x]`, `["c", name]`, `["v", name]`, `["l", name, body]`).
//!
//! The crate reproduces that encoding, that order, that node count and that
//! digest, so agreement is a check rather than a resemblance. Where the two
//! implementations disagree the run fails and the mismatch is retained.
//!
//! Bounds are declared and enforced per family: a contraction limit, a node
//! limit and a wall limit. Exhaustion reports `Unknown`; it is never reported
//! as divergence and never as a proof that no normal form exists.

use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::fmt::Write as _;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::Instant;

// ---------------------------------------------------------------------------
// SHA-256 (FIPS 180-4), implemented locally so the crate adds no dependency.
// ---------------------------------------------------------------------------

const SHA256_K: [u32; 64] = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

/// SHA-256 of the exact bytes, lowercase hexadecimal.
pub fn sha256_hex(bytes: &[u8]) -> String {
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
        0x5be0cd19,
    ];
    let mut message = bytes.to_vec();
    let bit_len = (bytes.len() as u64).wrapping_mul(8);
    message.push(0x80);
    while message.len() % 64 != 56 {
        message.push(0);
    }
    message.extend_from_slice(&bit_len.to_be_bytes());

    for chunk in message.chunks_exact(64) {
        let mut w = [0u32; 64];
        for (i, word) in chunk.chunks_exact(4).enumerate() {
            w[i] = u32::from_be_bytes([word[0], word[1], word[2], word[3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }
        let mut v = h;
        for i in 0..64 {
            let s1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
            let ch = (v[4] & v[5]) ^ ((!v[4]) & v[6]);
            let t1 = v[7]
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(SHA256_K[i])
                .wrapping_add(w[i]);
            let s0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
            let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = s0.wrapping_add(maj);
            v = [
                t1.wrapping_add(t2),
                v[0],
                v[1],
                v[2],
                v[3].wrapping_add(t1),
                v[4],
                v[5],
                v[6],
            ];
        }
        for (slot, value) in h.iter_mut().zip(v.iter()) {
            *slot = slot.wrapping_add(*value);
        }
    }
    let mut out = String::with_capacity(64);
    for word in h {
        let _ = write!(out, "{word:08x}");
    }
    out
}

// ---------------------------------------------------------------------------
// Terms and the murphy-compatible encoding
// ---------------------------------------------------------------------------

/// A combinator/lambda term.
///
/// `Const` holds one of the four source combinators: `'j'` is the Iota
/// combinator, `'S'`, `'K'` and `'I'` are the combinators the Iota rule
/// introduces. Variables appear only in lambda sources and in the declared
/// coordinate application; they are inert under reduction.
#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Term {
    Var(String),
    Const(char),
    App(Box<Term>, Box<Term>),
    Lam(String, Box<Term>),
}

/// Left-associated application of two or more terms.
pub fn apps(mut head: Term, rest: &[Term]) -> Term {
    for argument in rest {
        head = Term::App(Box::new(head), Box::new(argument.clone()));
    }
    head
}

/// `nodes(t)`: one per application, one per leaf. This is the murphy count.
pub fn nodes(term: &Term) -> u64 {
    match term {
        Term::Var(_) | Term::Const(_) => 1,
        Term::App(f, x) => 1 + nodes(f) + nodes(x),
        Term::Lam(_, body) => 1 + nodes(body),
    }
}

fn push_json_string(out: &mut String, value: &str) {
    out.push('"');
    for ch in value.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => {
                let _ = write!(out, "\\u{:04x}", c as u32);
            }
            c => out.push(c),
        }
    }
    out.push('"');
}

/// The canonical JSON encoding whose SHA-256 is the declared normal-form digest.
///
/// It is compact (no spaces), object-free and order-preserving, so the encoding
/// is a function of the term alone.
pub fn canonical_json(term: &Term) -> String {
    let mut out = String::new();
    encode_json(term, &mut out);
    out
}

fn encode_json(term: &Term, out: &mut String) {
    match term {
        Term::Var(name) => {
            out.push_str("[\"v\",");
            push_json_string(out, name);
            out.push(']');
        }
        Term::Const(name) => {
            out.push_str("[\"c\",");
            push_json_string(out, &name.to_string());
            out.push(']');
        }
        Term::App(f, x) => {
            out.push_str("[\"a\",");
            encode_json(f, out);
            out.push(',');
            encode_json(x, out);
            out.push(']');
        }
        Term::Lam(name, body) => {
            out.push_str("[\"l\",");
            push_json_string(out, name);
            out.push(',');
            encode_json(body, out);
            out.push(']');
        }
    }
}

/// SHA-256 of the canonical encoding: the declared normal-form digest.
pub fn term_digest(term: &Term) -> String {
    sha256_hex(canonical_json(term).as_bytes())
}

/// Which character spells the Iota combinator in a source.
///
/// The received murphy bytes use `i`. Mathematics, and this repository's own
/// iota interpretation frame, use `i` for the imaginary unit, so a renamed
/// spelling `ι` is declared and checked. The two spellings are declared, never
/// silently mixed, and `i` remains readable **only** under `Documentary`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum IotaSpelling {
    /// `i` is the Iota combinator. This is the spelling of the received bytes.
    Documentary,
    /// `ι` is the Iota combinator, and `i` is refused in a source.
    Renamed,
}

impl IotaSpelling {
    pub fn parse(name: &str) -> Option<Self> {
        match name {
            "documentary" => Some(Self::Documentary),
            "renamed" => Some(Self::Renamed),
            _ => None,
        }
    }

    pub fn name(self) -> &'static str {
        match self {
            Self::Documentary => "documentary",
            Self::Renamed => "renamed",
        }
    }
}

/// Parse pure Iota source: the Iota combinator and `*AB` application.
///
/// Leading and trailing ASCII whitespace is stripped exactly as the external
/// reference does; any other character, and any unconsumed suffix, is refused.
pub fn parse_iota(source: &str) -> Result<Term, String> {
    parse_iota_with(source, IotaSpelling::Documentary)
}

/// Parse pure Iota source under one declared spelling.
pub fn parse_iota_with(source: &str, spelling: IotaSpelling) -> Result<Term, String> {
    let code = source.trim();
    let symbols: Vec<char> = code.chars().collect();
    let mut position = 0usize;
    let term = parse_node(&symbols, &mut position, spelling)?;
    if position != symbols.len() {
        return Err(format!("unread Iota suffix at character {position}"));
    }
    Ok(term)
}

fn parse_node(
    symbols: &[char],
    position: &mut usize,
    spelling: IotaSpelling,
) -> Result<Term, String> {
    let symbol = *symbols
        .get(*position)
        .ok_or_else(|| "truncated Iota source".to_string())?;
    *position += 1;
    match (symbol, spelling) {
        ('*', _) => {
            let left = parse_node(symbols, position, spelling)?;
            let right = parse_node(symbols, position, spelling)?;
            Ok(Term::App(Box::new(left), Box::new(right)))
        }
        ('ι', _) => Ok(Term::Const('j')),
        ('i', IotaSpelling::Documentary) => Ok(Term::Const('j')),
        ('i', IotaSpelling::Renamed) => Err(
            "the renamed spelling refuses `i`: in mathematics `i` is the imaginary unit, and here the Iota combinator is written `ι`"
                .to_string(),
        ),
        (other, _) => Err(format!(
            "invalid Iota character {other:?} at character {}",
            *position - 1
        )),
    }
}

/// The declared renaming map: the documentary spelling `i` becomes `ι`.
///
/// The received bytes are never rewritten; this produces the renamed copy from
/// them, and the run checks that the two spellings parse to the same term and
/// reduce to the same witness.
pub fn rename_iota_source(source: &str, from: char, to: char) -> Result<String, String> {
    let code = source.trim();
    if let Some(found) = code.chars().find(|c| *c != from && *c != '*') {
        return Err(format!(
            "renaming expects only {from:?} and '*', found {found:?}"
        ));
    }
    Ok(code
        .chars()
        .map(|c| if c == from { to } else { c })
        .collect())
}

// ---------------------------------------------------------------------------
// The iota-lang case grammar
// ---------------------------------------------------------------------------

/// Parse the case grammar of the recorded `SKITest` contract: S-expressions
/// whose tokens are `i`, `k`, `s`, `j` or `ι`, and lowercase words as opaque
/// variables.
///
/// This grammar is **not** the murphy grammar above. There the character `i`
/// denotes the Iota combinator; here `i` denotes the identity combinator and
/// the Iota combinator is written `j` or `ι`. The two grammars are separate
/// declarations, and the declared collision is itself a control: no term mixes
/// them, and nothing here identifies the two `i` tokens.
pub fn parse_sexpr(source: &str) -> Result<Term, String> {
    let mut tokens: Vec<String> = Vec::new();
    let mut word = String::new();
    for ch in source.chars() {
        match ch {
            '(' | ')' => {
                if !word.is_empty() {
                    tokens.push(std::mem::take(&mut word));
                }
                tokens.push(ch.to_string());
            }
            c if c.is_whitespace() => {
                if !word.is_empty() {
                    tokens.push(std::mem::take(&mut word));
                }
            }
            c => word.push(c),
        }
    }
    if !word.is_empty() {
        tokens.push(word);
    }
    let mut position = 0usize;
    let term = parse_sexpr_node(&tokens, &mut position)?;
    if position != tokens.len() {
        return Err(format!(
            "unread case tokens from position {position} of {}",
            tokens.len()
        ));
    }
    Ok(term)
}

fn parse_sexpr_node(tokens: &[String], position: &mut usize) -> Result<Term, String> {
    let token = tokens
        .get(*position)
        .ok_or_else(|| "truncated case term".to_string())?
        .clone();
    *position += 1;
    match token.as_str() {
        "(" => {
            let mut term = parse_sexpr_node(tokens, position)?;
            loop {
                match tokens.get(*position).map(String::as_str) {
                    Some(")") => {
                        *position += 1;
                        return Ok(term);
                    }
                    Some(_) => {
                        let argument = parse_sexpr_node(tokens, position)?;
                        term = Term::App(Box::new(term), Box::new(argument));
                    }
                    None => return Err("unclosed case application".to_string()),
                }
            }
        }
        ")" => Err("unexpected closing parenthesis".to_string()),
        "i" => Ok(Term::Const('I')),
        "k" => Ok(Term::Const('K')),
        "s" => Ok(Term::Const('S')),
        "j" | "ι" => Ok(Term::Const('j')),
        other => {
            if !other.is_empty()
                && other
                    .chars()
                    .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit())
            {
                Ok(Term::Var(other.to_string()))
            } else {
                Err(format!("unsupported case token {other:?}"))
            }
        }
    }
}

/// Print a term in the recorded contract's token spelling: `i`, `k` and `s`
/// are the identity, K and S combinators and `ι` is the Iota combinator,
/// exactly as the recorded expectations write them.
pub fn print_sexpr(term: &Term) -> Result<String, String> {
    match term {
        Term::Const('I') => Ok("i".to_string()),
        Term::Const('K') => Ok("k".to_string()),
        Term::Const('S') => Ok("s".to_string()),
        Term::Const('j') => Ok("ι".to_string()),
        Term::Const(other) => Err(format!("unprintable combinator {other:?}")),
        Term::Var(name) => Ok(name.clone()),
        Term::App(f, x) => Ok(format!("({} {})", print_sexpr(f)?, print_sexpr(x)?)),
        Term::Lam(_, _) => Err("a lambda is outside the case grammar".to_string()),
    }
}

fn free_vars(term: &Term, out: &mut BTreeSet<String>) {
    match term {
        Term::Var(name) => {
            out.insert(name.clone());
        }
        Term::Const(_) => {}
        Term::App(f, x) => {
            free_vars(f, out);
            free_vars(x, out);
        }
        Term::Lam(name, body) => {
            let mut inner = BTreeSet::new();
            free_vars(body, &mut inner);
            inner.remove(name);
            out.extend(inner);
        }
    }
}

/// Bracket abstraction without eta optimization, exactly as the reference does.
pub fn abstract_var(name: &str, term: &Term) -> Result<Term, String> {
    let mut free = BTreeSet::new();
    free_vars(term, &mut free);
    if !free.contains(name) {
        return Ok(Term::App(
            Box::new(Term::Const('K')),
            Box::new(term.clone()),
        ));
    }
    if matches!(term, Term::Var(v) if v == name) {
        return Ok(Term::Const('I'));
    }
    match term {
        Term::App(f, x) => Ok(apps(
            Term::Const('S'),
            &[abstract_var(name, f)?, abstract_var(name, x)?],
        )),
        other => Err(format!("uneliminated abstraction over {other:?}")),
    }
}

/// Bracket-abstraction translation of a lambda term into S/K/I plus Iota leaves.
pub fn ski(term: &Term) -> Result<Term, String> {
    match term {
        Term::Lam(name, body) => abstract_var(name, &ski(body)?),
        Term::App(f, x) => Ok(Term::App(Box::new(ski(f)?), Box::new(ski(x)?))),
        other => Ok(other.clone()),
    }
}

/// The declared four-slot product `Z(p,q,r,s) = lambda k. k p q r s`.
pub fn tuple4(slots: &[Term; 4]) -> Term {
    Term::Lam(
        "collector".to_string(),
        Box::new(apps(
            Term::Var("collector".to_string()),
            &[
                slots[0].clone(),
                slots[1].clone(),
                slots[2].clone(),
                slots[3].clone(),
            ],
        )),
    )
}

/// `(out p q r s)`-style expected normal form for a declared slot order.
pub fn expected_permutation(order: &[usize]) -> Term {
    let slots = ["p", "q", "r", "s"].map(|name| Term::Var(name.to_string()));
    apps(
        Term::Var("out".to_string()),
        &[
            slots[order[0]].clone(),
            slots[order[1]].clone(),
            slots[order[2]].clone(),
            slots[order[3]].clone(),
        ],
    )
}

/// The declared coordinate application: `ski((program Z) out)`.
///
/// The slot order is carried by the program itself; it is checked against the
/// declared expected normal form rather than being passed in here.
pub fn coordinate_application(program: &Term) -> Result<Term, String> {
    let slots = ["p", "q", "r", "s"].map(|name| Term::Var(name.to_string()));
    let z = tuple4(&slots);
    ski(&Term::App(
        Box::new(Term::App(Box::new(program.clone()), Box::new(z))),
        Box::new(Term::Var("out".to_string())),
    ))
}

// ---------------------------------------------------------------------------
// The flat-list notation and its two declared readings
// ---------------------------------------------------------------------------

/// How a flat list `[t1 t2 ... tn]` becomes an application tree.
///
/// The question is not academic: the external iota-lang resources write
/// `[Iota Iota Iota Iota]` for K and `[Iota Iota Iota Iota Iota]` for S, and
/// the two readings pair the tail differently. This declaration makes the
/// reading explicit instead of leaving it to a convention.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ListReading {
    /// `[t1 t2 t3]` becomes `((t1 t2) t3)`.
    LeftNested,
    /// `[t1 t2 t3]` becomes `(t1 (t2 t3))`.
    RightNested,
}

impl ListReading {
    pub fn parse(name: &str) -> Option<Self> {
        match name {
            "left-nested" => Some(Self::LeftNested),
            "right-nested" => Some(Self::RightNested),
            _ => None,
        }
    }

    pub fn name(self) -> &'static str {
        match self {
            Self::LeftNested => "left-nested",
            Self::RightNested => "right-nested",
        }
    }
}

/// Read a non-empty flat list under one declared reading.
///
/// A one-element list is its element under both readings; a two-element list
/// is `(t1 t2)` under both. The readings first differ at three elements, so a
/// two-element list cannot decide between them.
pub fn nest(list: &[Term], reading: ListReading) -> Result<Term, String> {
    let Some((first, rest)) = list.split_first() else {
        return Err("an empty flat list has no reading".to_string());
    };
    if rest.is_empty() {
        return Ok(first.clone());
    }
    Ok(match reading {
        ListReading::LeftNested => {
            let mut acc = first.clone();
            for term in rest {
                acc = Term::App(Box::new(acc), Box::new(term.clone()));
            }
            acc
        }
        ListReading::RightNested => {
            let mut acc = rest[rest.len() - 1].clone();
            for term in rest[..rest.len() - 1].iter().rev() {
                acc = Term::App(Box::new(term.clone()), Box::new(acc));
            }
            Term::App(Box::new(first.clone()), Box::new(acc))
        }
    })
}

/// Parse a form in the case grammar **with bracket lists**: `(...)` is ordinary
/// left-associated application, and `[...]` is a flat list read under the
/// declared reading.
pub fn parse_case(source: &str, reading: ListReading) -> Result<Term, String> {
    let mut tokens = Vec::new();
    let mut word = String::new();
    for ch in source.chars() {
        match ch {
            '(' | ')' | '[' | ']' => {
                if !word.is_empty() {
                    tokens.push(std::mem::take(&mut word));
                }
                tokens.push(ch.to_string());
            }
            c if c.is_whitespace() => {
                if !word.is_empty() {
                    tokens.push(std::mem::take(&mut word));
                }
            }
            c => word.push(c),
        }
    }
    if !word.is_empty() {
        tokens.push(word);
    }
    let mut position = 0usize;
    let term = parse_case_node(&tokens, &mut position, reading)?;
    if position != tokens.len() {
        return Err(format!(
            "unread case tokens from position {position} of {}",
            tokens.len()
        ));
    }
    Ok(term)
}

fn parse_case_node(
    tokens: &[String],
    position: &mut usize,
    reading: ListReading,
) -> Result<Term, String> {
    let token = tokens
        .get(*position)
        .ok_or_else(|| "truncated case form".to_string())?
        .clone();
    *position += 1;
    match token.as_str() {
        "(" => {
            let mut term = parse_case_node(tokens, position, reading)?;
            loop {
                match tokens.get(*position).map(String::as_str) {
                    Some(")") => {
                        *position += 1;
                        return Ok(term);
                    }
                    Some(_) => {
                        let argument = parse_case_node(tokens, position, reading)?;
                        term = Term::App(Box::new(term), Box::new(argument));
                    }
                    None => return Err("unclosed case application".to_string()),
                }
            }
        }
        "[" => {
            let mut elements = Vec::new();
            loop {
                match tokens.get(*position).map(String::as_str) {
                    Some("]") => {
                        *position += 1;
                        return nest(&elements, reading);
                    }
                    Some(_) => elements.push(parse_case_node(tokens, position, reading)?),
                    None => return Err("unclosed flat list".to_string()),
                }
            }
        }
        ")" | "]" => Err("unexpected closing bracket".to_string()),
        "i" => Ok(Term::Const('I')),
        "k" => Ok(Term::Const('K')),
        "s" => Ok(Term::Const('S')),
        "j" | "ι" => Ok(Term::Const('j')),
        other => {
            if !other.is_empty()
                && other
                    .chars()
                    .all(|c| c.is_ascii_lowercase() || c.is_ascii_digit())
            {
                Ok(Term::Var(other.to_string()))
            } else {
                Err(format!("unsupported case token {other:?}"))
            }
        }
    }
}
// ---------------------------------------------------------------------------
// Reduction
// ---------------------------------------------------------------------------

fn arity(name: char) -> Option<usize> {
    match name {
        'j' | 'I' => Some(1),
        'K' => Some(2),
        'S' => Some(3),
        _ => None,
    }
}

fn spine(term: &Term) -> (Term, Vec<Term>) {
    let mut arguments = Vec::new();
    let mut head = term.clone();
    while let Term::App(f, x) = head {
        arguments.push((*x).clone());
        head = *f;
    }
    arguments.reverse();
    (head, arguments)
}

/// One declared leftmost-outermost contraction, or `None` when no redex exists.
///
/// Returns the rewritten term, the `L`/`R` path of the contracted node and the
/// combinator name that was applied.
pub fn contract_once(term: &Term, path: &mut String) -> Option<(Term, String, char)> {
    let (head, arguments) = spine(term);
    if let Term::Const(name) = head {
        if let Some(needed) = arity(name) {
            if arguments.len() >= needed {
                let rest = &arguments[needed..];
                let reduced = match name {
                    'j' => apps(arguments[0].clone(), &[Term::Const('S'), Term::Const('K')]),
                    'I' => arguments[0].clone(),
                    'K' => arguments[0].clone(),
                    'S' => Term::App(
                        Box::new(Term::App(
                            Box::new(arguments[0].clone()),
                            Box::new(arguments[2].clone()),
                        )),
                        Box::new(Term::App(
                            Box::new(arguments[1].clone()),
                            Box::new(arguments[2].clone()),
                        )),
                    ),
                    _ => unreachable!("arity table is total for the four combinators"),
                };
                return Some((apps(reduced, rest), path.clone(), name));
            }
        }
    }
    if let Term::App(f, x) = term {
        path.push('L');
        if let Some((new_left, found, rule)) = contract_once(f, path) {
            path.pop();
            return Some((Term::App(Box::new(new_left), x.clone()), found, rule));
        }
        path.pop();
        path.push('R');
        if let Some((new_right, found, rule)) = contract_once(x, path) {
            path.pop();
            return Some((Term::App(f.clone(), Box::new(new_right)), found, rule));
        }
        path.pop();
    }
    None
}

/// The declared order's control: the leftmost-innermost redex instead.
pub fn contract_once_innermost(term: &Term) -> Option<(Term, char)> {
    if let Term::App(f, x) = term {
        if let Some((new_left, rule)) = contract_once_innermost(f) {
            return Some((Term::App(Box::new(new_left), x.clone()), rule));
        }
        if let Some((new_right, rule)) = contract_once_innermost(x) {
            return Some((Term::App(f.clone(), Box::new(new_right)), rule));
        }
    }
    let (head, arguments) = spine(term);
    if let Term::Const(name) = head {
        let needed = arity(name)?;
        if arguments.len() >= needed {
            let rest = &arguments[needed..];
            let reduced = match name {
                'j' => apps(arguments[0].clone(), &[Term::Const('S'), Term::Const('K')]),
                'I' | 'K' => arguments[0].clone(),
                'S' => Term::App(
                    Box::new(Term::App(
                        Box::new(arguments[0].clone()),
                        Box::new(arguments[2].clone()),
                    )),
                    Box::new(Term::App(
                        Box::new(arguments[1].clone()),
                        Box::new(arguments[2].clone()),
                    )),
                ),
                _ => return None,
            };
            return Some((apps(reduced, rest), name));
        }
    }
    None
}

/// An independent redex test, used to confirm a returned normal form.
pub fn has_redex(term: &Term) -> bool {
    let mut scratch = String::new();
    contract_once(term, &mut scratch).is_some()
}

/// Declared per-family reduction bounds.
#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Limits {
    pub contractions_per_family: u64,
    pub nodes_per_family: u64,
    pub seconds_per_family: f64,
}

/// One retained reduction row.
#[derive(Clone, Debug, Serialize)]
pub struct TraceRow {
    pub step: u64,
    pub path: String,
    pub rule: String,
    pub nodes: u64,
    pub sha256: String,
}

/// The counted outcome of one reduction.
#[derive(Clone, Debug)]
pub struct Reduction {
    pub status: ReductionStatus,
    pub contractions: u64,
    pub rules: BTreeMap<String, u64>,
    pub peak_nodes: u64,
    pub term: Option<Term>,
    pub normal_form_sha256: Option<String>,
    pub normal_form_nodes: Option<u64>,
    pub normal_form_is_redex_free: Option<bool>,
    pub trace: Vec<TraceRow>,
    pub elapsed_seconds: f64,
    pub reason: Option<String>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum ReductionStatus {
    /// A redex-free term was reached inside the declared bounds.
    NormalForm,
    /// The declared bound stopped the run; this is `Unknown`, not divergence.
    Exhausted,
}

/// Leftmost-outermost reduction under the declared bounds.
pub fn reduce(term: &Term, limits: &Limits, record_trace: bool) -> Reduction {
    let started = Instant::now();
    let mut current = term.clone();
    let mut contractions = 0u64;
    let mut rules: BTreeMap<String, u64> = BTreeMap::new();
    let mut peak_nodes = nodes(&current);
    let mut trace = Vec::new();
    loop {
        if started.elapsed().as_secs_f64() > limits.seconds_per_family {
            return exhaustion(
                current,
                contractions,
                rules,
                peak_nodes,
                trace,
                started,
                "wall limit",
            );
        }
        if nodes(&current) > limits.nodes_per_family {
            return exhaustion(
                current,
                contractions,
                rules,
                peak_nodes,
                trace,
                started,
                "node limit",
            );
        }
        let mut path = String::new();
        let Some((next, found, rule)) = contract_once(&current, &mut path) else {
            let digest = term_digest(&current);
            let is_redex_free = !has_redex(&current);
            return Reduction {
                status: ReductionStatus::NormalForm,
                contractions,
                rules,
                peak_nodes,
                normal_form_sha256: Some(digest),
                normal_form_nodes: Some(nodes(&current)),
                normal_form_is_redex_free: Some(is_redex_free),
                term: Some(current),
                trace,
                elapsed_seconds: started.elapsed().as_secs_f64(),
                reason: None,
            };
        };
        if contractions >= limits.contractions_per_family {
            return exhaustion(
                current,
                contractions,
                rules,
                peak_nodes,
                trace,
                started,
                "contraction limit",
            );
        }
        current = next;
        contractions += 1;
        *rules.entry(rule.to_string()).or_insert(0) += 1;
        let size = nodes(&current);
        if size > peak_nodes {
            peak_nodes = size;
        }
        if record_trace {
            trace.push(TraceRow {
                step: contractions,
                path: found,
                rule: rule.to_string(),
                nodes: size,
                sha256: term_digest(&current),
            });
        }
    }
}

fn exhaustion(
    term: Term,
    contractions: u64,
    rules: BTreeMap<String, u64>,
    peak_nodes: u64,
    trace: Vec<TraceRow>,
    started: Instant,
    reason: &str,
) -> Reduction {
    Reduction {
        status: ReductionStatus::Exhausted,
        contractions,
        rules,
        peak_nodes,
        normal_form_sha256: None,
        normal_form_nodes: None,
        normal_form_is_redex_free: None,
        term: Some(term),
        trace,
        elapsed_seconds: started.elapsed().as_secs_f64(),
        reason: Some(reason.to_string()),
    }
}

/// The declared-order control: the same bounds under a different order.
pub fn reduce_innermost(term: &Term, limits: &Limits) -> Reduction {
    let started = Instant::now();
    let mut current = term.clone();
    let mut contractions = 0u64;
    let mut rules: BTreeMap<String, u64> = BTreeMap::new();
    let mut peak_nodes = nodes(&current);
    loop {
        if started.elapsed().as_secs_f64() > limits.seconds_per_family {
            return exhaustion(
                current,
                contractions,
                rules,
                peak_nodes,
                Vec::new(),
                started,
                "wall limit",
            );
        }
        if nodes(&current) > limits.nodes_per_family {
            return exhaustion(
                current,
                contractions,
                rules,
                peak_nodes,
                Vec::new(),
                started,
                "node limit",
            );
        }
        let Some((next, rule)) = contract_once_innermost(&current) else {
            let digest = term_digest(&current);
            return Reduction {
                status: ReductionStatus::NormalForm,
                contractions,
                rules,
                peak_nodes,
                normal_form_sha256: Some(digest),
                normal_form_nodes: Some(nodes(&current)),
                normal_form_is_redex_free: Some(!has_redex(&current)),
                term: Some(current),
                trace: Vec::new(),
                elapsed_seconds: started.elapsed().as_secs_f64(),
                reason: None,
            };
        };
        if contractions >= limits.contractions_per_family {
            return exhaustion(
                current,
                contractions,
                rules,
                peak_nodes,
                Vec::new(),
                started,
                "contraction limit",
            );
        }
        current = next;
        contractions += 1;
        *rules.entry(rule.to_string()).or_insert(0) += 1;
        let size = nodes(&current);
        if size > peak_nodes {
            peak_nodes = size;
        }
    }
}

// ---------------------------------------------------------------------------
// Declared contract
// ---------------------------------------------------------------------------

/// One file whose bytes must match the received receipt's record.
#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct BoundFile {
    /// Path relative to the materials root.
    pub path: String,
    /// Destination recorded by the reception receipt.
    pub receipt_destination: String,
}

#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Identity {
    /// Reception receipt retained by the documentary route.
    pub receipt: String,
    pub receipt_sha256: String,
    /// Materials root used to resolve family and bound-file paths.
    pub materials: String,
    pub files: Vec<BoundFile>,
}

/// Where a family's expected numbers come from.
#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Oracle {
    /// Frozen evidence document, relative to the materials root.
    pub document: String,
    pub document_sha256: String,
    /// RFC 6901 JSON pointer to the counted object.
    pub pointer: String,
}

#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Family {
    pub label: String,
    /// `iota` reduces the parsed program directly; `coordinate` reduces the
    /// declared four-slot application `ski((program Z) out)`.
    pub kind: String,
    pub program: String,
    /// Declared slot order for `coordinate` families.
    /// `documentary` (default) or `renamed`; the received files are documentary.
    #[serde(default)]
    pub spelling: Option<String>,
    #[serde(default)]
    pub permutation: Option<Vec<usize>>,
    #[serde(default)]
    pub oracle: Option<Oracle>,
    #[serde(default)]
    pub note: Option<String>,
}

/// One recorded case of the iota-lang contract.
#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Case {
    pub label: String,
    /// `iota-lang` selects the S-expression case grammar.
    pub grammar: String,
    /// The case term, transcribed from the recorded contract.
    pub term: String,
    /// The recorded expectation, transcribed unchanged.
    pub expected: String,
    #[serde(default)]
    pub note: Option<String>,
}

/// The declared renaming of the Iota combinator's source spelling.
#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Renaming {
    /// The spelling the received bytes use.
    pub from: String,
    /// The declared renamed spelling.
    pub to: String,
    /// A directory under the run output where the renamed copy is written.
    pub output: String,
    pub note: String,
}

/// One program carried across the renaming, with its optional frozen oracle.
#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RenamedProgram {
    pub label: String,
    pub program: String,
    /// `iota` or `coordinate`, exactly as the corresponding family declares.
    #[serde(default)]
    pub kind: Option<String>,
    /// Declared slot order for a `coordinate` program.
    #[serde(default)]
    pub permutation: Option<Vec<usize>>,
    #[serde(default)]
    pub oracle: Option<Oracle>,
    #[serde(default)]
    pub note: Option<String>,
}

/// One declared reading case: a form whose brackets are read one way, with a
/// declared expectation of whether the reading reproduces the target behaviour.
#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ReadingCase {
    pub label: String,
    /// The form, in the case grammar extended with `[` `]` flat lists.
    pub form: String,
    /// `left-nested` or `right-nested` for every list in this form.
    pub reading: String,
    /// `holds` requires the printed normal form to equal `expected`;
    /// `fails` requires it to differ.
    pub expectation: String,
    pub expected: String,
    #[serde(default)]
    pub note: Option<String>,
}

/// An independently supplied transcript, used only to compare transcriptions.
#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Comparison {
    pub document: String,
    pub document_sha256: String,
    pub note: String,
}

#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TraceBinding {
    pub label: String,
    pub document: String,
    pub document_sha256: String,
}

#[derive(Clone, Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Contract {
    pub schema: String,
    pub profile: String,
    pub question: String,
    pub level: String,
    pub assumptions: Vec<String>,
    pub limits: Limits,
    #[serde(default)]
    pub identity: Option<Identity>,
    pub families: Vec<Family>,
    #[serde(default)]
    pub trace: Option<TraceBinding>,
    #[serde(default)]
    pub cases: Vec<Case>,
    #[serde(default)]
    pub comparison: Option<Comparison>,
    #[serde(default)]
    pub readings: Vec<ReadingCase>,
    #[serde(default)]
    pub renaming: Option<Renaming>,
    #[serde(default)]
    pub renamings: Vec<RenamedProgram>,
    pub controls: Vec<String>,
    pub acceptance: String,
    pub residual: String,
}

pub fn load_contract(path: &Path) -> Result<Contract, String> {
    let raw = fs::read(path).map_err(|e| format!("contract read failed: {e}"))?;
    let contract: Contract =
        serde_json::from_slice(&raw).map_err(|e| format!("contract parse failed: {e}"))?;
    if contract.schema != "adva.iota-substrate.contract.v0" {
        return Err(format!("unsupported contract schema {}", contract.schema));
    }
    if contract.profile != "iota-substrate-v0" {
        return Err(format!("unsupported profile {}", contract.profile));
    }
    Ok(contract)
}

// ---------------------------------------------------------------------------
// Run
// ---------------------------------------------------------------------------

/// One family's retained result.
#[derive(Clone, Debug, Serialize)]
pub struct FamilyResult {
    pub label: String,
    pub kind: String,
    pub program: String,
    pub program_bytes: u64,
    pub program_sha256: String,
    pub characters: usize,
    pub receipt_sha256: Option<String>,
    pub status: ReductionStatus,
    pub contractions: u64,
    pub rules: BTreeMap<String, u64>,
    pub peak_nodes: u64,
    pub normal_form_sha256: Option<String>,
    pub normal_form_nodes: Option<u64>,
    pub normal_form_is_redex_free: Option<bool>,
    pub expected_normal_form_matched: Option<bool>,
    pub elapsed_seconds: f64,
    pub exhausted_reason: Option<String>,
    pub oracle: Option<OracleResult>,
    pub verdict: String,
    pub note: Option<String>,
}

#[derive(Clone, Debug, Serialize)]
pub struct OracleResult {
    pub document: String,
    pub document_sha256: String,
    pub pointer: String,
    pub contractions: Option<u64>,
    pub rules: Option<BTreeMap<String, u64>>,
    pub peak_nodes: Option<u64>,
    pub normal_form_sha256: Option<String>,
    pub contractions_match: Option<bool>,
    pub rules_match: Option<bool>,
    pub peak_nodes_match: Option<bool>,
    pub digest_match: Option<bool>,
}

/// One executed case's retained result.
#[derive(Clone, Debug, Serialize)]
pub struct CaseResult {
    pub label: String,
    pub grammar: String,
    pub term: String,
    pub expected: String,
    pub observed: Option<String>,
    pub contractions: u64,
    pub status: ReductionStatus,
    pub matched_recorded_expectation: bool,
    /// The same case as transcribed by the independently supplied transcript.
    pub transcript_term: Option<String>,
    pub transcript_agrees: Option<bool>,
    pub verdict: String,
    pub note: Option<String>,
}

/// One program's retained renaming result.
#[derive(Clone, Debug, Serialize)]
pub struct RenamingResult {
    pub label: String,
    pub program: String,
    pub original_bytes: u64,
    pub original_sha256: String,
    pub original_characters: usize,
    pub renamed_bytes: u64,
    pub renamed_sha256: String,
    pub renamed_characters: usize,
    pub renamed_path: String,
    pub term_digest_original: String,
    pub term_digest_renamed: String,
    pub same_term: bool,
    pub contractions_original: u64,
    pub contractions_renamed: u64,
    pub rules_match: bool,
    pub peak_nodes_match: bool,
    pub normal_form_digest_match: bool,
    pub oracle_matched: Option<bool>,
    pub verdict: String,
    pub note: Option<String>,
}

/// One executed reading case's retained result.
#[derive(Clone, Debug, Serialize)]
pub struct ReadingResult {
    pub label: String,
    pub form: String,
    pub reading: String,
    pub expectation: String,
    pub expected: String,
    pub observed: Option<String>,
    pub contractions: u64,
    pub status: ReductionStatus,
    pub verdict: String,
    pub note: Option<String>,
}

#[derive(Clone, Debug, Serialize)]
pub struct ControlResult {
    pub name: String,
    pub expectation: String,
    pub observed: String,
    pub passed: bool,
}

#[derive(Clone, Debug, Serialize)]
pub struct RunReport {
    pub schema: String,
    pub profile: String,
    pub question: String,
    pub level: String,
    pub native_admission: String,
    pub stable_semantic_api: bool,
    pub outcome: String,
    pub limits: Limits,
    pub families: Vec<FamilyResult>,
    pub controls: Vec<ControlResult>,
    pub checked_families: usize,
    pub frozen_oracle_families: usize,
    pub total_contractions: u64,
    pub trace_rows_compared: usize,
    pub trace_rows_matched: usize,
    pub cases: Vec<CaseResult>,
    pub cases_matched: usize,
    pub cases_mismatched: usize,
    pub transcript_rows_compared: usize,
    pub transcript_rows_agreeing: usize,
    pub readings: Vec<ReadingResult>,
    pub renamings: Vec<RenamingResult>,
    pub renamings_preserved: usize,
    pub readings_held: usize,
    pub readings_failed_as_declared: usize,
    pub readings_unexpected: usize,
    pub acceptance: String,
    pub residual: String,
    pub wall_seconds: f64,
}

fn rules_from_json(value: &serde_json::Value) -> Option<BTreeMap<String, u64>> {
    let object = value.as_object()?;
    let mut out = BTreeMap::new();
    for (key, entry) in object {
        out.insert(key.clone(), entry.as_u64()?);
    }
    Some(out)
}

fn read_document(root: &Path, relative: &str, expected: &str) -> Result<Vec<u8>, String> {
    let path = root.join(relative);
    let raw = fs::read(&path).map_err(|e| format!("oracle read failed for {relative}: {e}"))?;
    let digest = sha256_hex(&raw);
    if digest != expected {
        return Err(format!(
            "oracle document {relative} digest {digest} differs from the declared {expected}"
        ));
    }
    Ok(raw)
}

/// Execute the declared contract once, retaining every outcome.
///
/// `origin_root` resolves the independently supplied origin documents (the
/// step trace). Everything else resolves against the contract's materials root,
/// so the crossed bytes and the separately supplied oracle stay distinguishable.
pub fn run_contract(
    contract: &Contract,
    origin_root: &Path,
    output_root: &Path,
) -> Result<RunReport, String> {
    let started = Instant::now();
    let root: PathBuf = match &contract.identity {
        Some(identity) => PathBuf::from(&identity.materials),
        None => PathBuf::from("."),
    };

    // Declared identity binding: the substrate must run on the received bytes.
    let mut receipt_digests: BTreeMap<String, String> = BTreeMap::new();
    if let Some(identity) = &contract.identity {
        let raw = read_document(Path::new("."), &identity.receipt, &identity.receipt_sha256)
            .map_err(|e| format!("identity binding refused: {e}"))?;
        let receipt: serde_json::Value =
            serde_json::from_slice(&raw).map_err(|e| format!("receipt parse failed: {e}"))?;
        let files = receipt["files"]
            .as_array()
            .ok_or_else(|| "receipt has no files array".to_string())?;
        for file in files {
            let destination = file["destination"].as_str().unwrap_or_default().to_string();
            let digest = file["sha256"].as_str().unwrap_or_default().to_string();
            receipt_digests.insert(destination, digest);
        }
        for bound in &identity.files {
            let raw = fs::read(root.join(&bound.path))
                .map_err(|e| format!("bound file {} unreadable: {e}", bound.path))?;
            let digest = sha256_hex(&raw);
            let recorded = receipt_digests
                .get(&bound.receipt_destination)
                .ok_or_else(|| {
                    format!(
                        "receipt records no destination {}",
                        bound.receipt_destination
                    )
                })?;
            if &digest != recorded {
                return Err(format!(
                    "bound file {} digest {digest} differs from the receipt's {recorded}",
                    bound.path
                ));
            }
        }
    }

    let mut families: Vec<FamilyResult> = Vec::new();
    let mut total_contractions = 0u64;
    let mut frozen_oracle_families = 0usize;

    for family in &contract.families {
        let raw = fs::read(root.join(&family.program))
            .map_err(|e| format!("family {} program unreadable: {e}", family.label))?;
        let program_sha256 = sha256_hex(&raw);
        let text = std::str::from_utf8(&raw)
            .map_err(|e| format!("family {} program is not UTF-8: {e}", family.label))?;
        let spelling = match family.spelling.as_deref() {
            None | Some("documentary") => IotaSpelling::Documentary,
            Some("renamed") => IotaSpelling::Renamed,
            Some(other) => {
                return Err(format!(
                    "family {} declares unsupported spelling {other}",
                    family.label
                ));
            }
        };
        let program = parse_iota_with(text, spelling)
            .map_err(|e| format!("family {} program refused: {e}", family.label))?;
        let (term, expected) = match family.kind.as_str() {
            "iota" => (program.clone(), None),
            "coordinate" => {
                let order = family
                    .permutation
                    .clone()
                    .ok_or_else(|| format!("family {} declares no permutation", family.label))?;
                if order.len() != 4 || order.iter().any(|k| *k > 3) {
                    return Err(format!(
                        "family {} permutation is not four slots",
                        family.label
                    ));
                }
                (
                    coordinate_application(&program)?,
                    Some(expected_permutation(&order)),
                )
            }
            other => {
                return Err(format!(
                    "family {} has unsupported kind {other}",
                    family.label
                ));
            }
        };
        let reduction = reduce(&term, &contract.limits, false);
        total_contractions += reduction.contractions;
        let expected_matched = match (expected.as_ref(), reduction.term.as_ref()) {
            (Some(expected), Some(actual)) => Some(expected == actual),
            _ => None,
        };

        let mut oracle_result = None;
        if let Some(oracle) = &family.oracle {
            frozen_oracle_families += 1;
            let raw = read_document(&root, &oracle.document, &oracle.document_sha256)
                .map_err(|e| format!("family {} {e}", family.label))?;
            let document: serde_json::Value = serde_json::from_slice(&raw)
                .map_err(|e| format!("family {} oracle parse failed: {e}", family.label))?;
            let entry = document.pointer(&oracle.pointer).ok_or_else(|| {
                format!(
                    "family {} oracle pointer {} missing",
                    family.label, oracle.pointer
                )
            })?;
            let expected_contractions = entry["contractions"].as_u64();
            let expected_rules = rules_from_json(&entry["rules"]);
            let expected_peak = entry["peak_nodes"].as_u64();
            let expected_digest = entry["normal_form_sha256"].as_str().map(str::to_string);
            oracle_result = Some(OracleResult {
                document: oracle.document.clone(),
                document_sha256: oracle.document_sha256.clone(),
                pointer: oracle.pointer.clone(),
                contractions: expected_contractions,
                rules: expected_rules.clone(),
                peak_nodes: expected_peak,
                normal_form_sha256: expected_digest.clone(),
                contractions_match: expected_contractions.map(|v| v == reduction.contractions),
                rules_match: expected_rules.map(|v| Some(&v) == Some(&reduction.rules)),
                peak_nodes_match: expected_peak.map(|v| v == reduction.peak_nodes),
                digest_match: expected_digest
                    .map(|v| Some(&v) == reduction.normal_form_sha256.as_ref()),
            });
        }
        let oracle_matched = oracle_result.as_ref().map(|o| {
            o.contractions_match.unwrap_or(false)
                && o.rules_match.unwrap_or(false)
                && o.peak_nodes_match.unwrap_or(false)
                && o.digest_match.unwrap_or(false)
        });
        let verdict = match (reduction.status, oracle_matched, expected_matched) {
            (ReductionStatus::Exhausted, _, _) => "Exhausted-Unknown".to_string(),
            (ReductionStatus::NormalForm, Some(false), _) => "Mismatched-Frozen-Oracle".to_string(),
            (ReductionStatus::NormalForm, _, Some(false)) => {
                "Mismatched-Declared-Normal-Form".to_string()
            }
            (ReductionStatus::NormalForm, Some(true), _) => "Matched-Frozen-Oracle".to_string(),
            (ReductionStatus::NormalForm, None, Some(true)) => {
                "Matched-Declared-Normal-Form".to_string()
            }
            (ReductionStatus::NormalForm, None, None) => "Recorded-No-Oracle".to_string(),
        };

        families.push(FamilyResult {
            label: family.label.clone(),
            kind: family.kind.clone(),
            program: family.program.clone(),
            program_bytes: raw.len() as u64,
            program_sha256,
            characters: text.trim().chars().count(),
            receipt_sha256: contract.identity.as_ref().and_then(|identity| {
                let file_name = Path::new(&family.program)
                    .file_name()
                    .map(|n| n.to_string_lossy().to_string())
                    .unwrap_or_default();
                identity
                    .files
                    .iter()
                    .find(|bound| {
                        bound
                            .receipt_destination
                            .ends_with(&format!("/{file_name}"))
                    })
                    .and_then(|bound| receipt_digests.get(&bound.receipt_destination).cloned())
            }),
            status: reduction.status,
            contractions: reduction.contractions,
            rules: reduction.rules.clone(),
            peak_nodes: reduction.peak_nodes,
            normal_form_sha256: reduction.normal_form_sha256.clone(),
            normal_form_nodes: reduction.normal_form_nodes,
            normal_form_is_redex_free: reduction.normal_form_is_redex_free,
            expected_normal_form_matched: expected_matched,
            elapsed_seconds: reduction.elapsed_seconds,
            exhausted_reason: reduction.reason.clone(),
            oracle: oracle_result,
            verdict,
            note: family.note.clone(),
        });
    }

    // Recorded cases of the iota-lang contract, transcribed as declared.
    let mut cases: Vec<CaseResult> = Vec::new();
    let mut transcript_terms: BTreeMap<String, String> = BTreeMap::new();
    if let Some(comparison) = &contract.comparison {
        let raw = read_document(&root, &comparison.document, &comparison.document_sha256)
            .map_err(|e| format!("case comparison refused: {e}"))?;
        let text = String::from_utf8_lossy(&raw);
        for line in text.lines() {
            let line = line.trim();
            if !line.starts_with('{') {
                continue;
            }
            let value: serde_json::Value = serde_json::from_str(line)
                .map_err(|e| format!("case comparison line refused: {e}"))?;
            if value["kind"].as_str() != Some("case") {
                continue;
            }
            if let (Some(name), Some(term)) = (value["name"].as_str(), value["term"].as_str()) {
                transcript_terms.insert(name.to_string(), term.to_string());
            }
        }
    }
    for case in &contract.cases {
        if case.grammar != "iota-lang" {
            return Err(format!(
                "case {} declares unsupported grammar {}",
                case.label, case.grammar
            ));
        }
        let term = parse_sexpr(&case.term)
            .map_err(|e| format!("case {} term refused: {e}", case.label))?;
        let reduction = reduce(&term, &contract.limits, false);
        let observed = match reduction.term.as_ref() {
            Some(term) => Some(print_sexpr(term)?),
            None => None,
        };
        let matched = observed.as_deref() == Some(case.expected.as_str());
        let transcript = transcript_terms.get(&case.label).cloned();
        let agrees = match &transcript {
            Some(text) => Some(parse_sexpr(text)? == term),
            None => None,
        };
        let verdict = match reduction.status {
            ReductionStatus::Exhausted => "Exhausted-Unknown",
            ReductionStatus::NormalForm if matched => "Matched-Recorded-Expectation",
            ReductionStatus::NormalForm => "Mismatched-Recorded-Expectation",
        };
        total_contractions += reduction.contractions;
        cases.push(CaseResult {
            label: case.label.clone(),
            grammar: case.grammar.clone(),
            term: case.term.clone(),
            expected: case.expected.clone(),
            observed,
            contractions: reduction.contractions,
            status: reduction.status,
            matched_recorded_expectation: matched,
            transcript_term: transcript,
            transcript_agrees: agrees,
            verdict: verdict.to_string(),
            note: case.note.clone(),
        });
    }

    // Declared flat-list reading cases.
    let mut readings: Vec<ReadingResult> = Vec::new();
    for case in &contract.readings {
        let reading = ListReading::parse(&case.reading)
            .ok_or_else(|| format!("reading case {} declares {} ", case.label, case.reading))?;
        let term = parse_case(&case.form, reading)
            .map_err(|e| format!("reading case {} form refused: {e}", case.label))?;
        let reduction = reduce(&term, &contract.limits, false);
        let observed = match reduction.term.as_ref() {
            Some(term) => Some(print_sexpr(term)?),
            None => None,
        };
        let reproduced = observed.as_deref() == Some(case.expected.as_str());
        let verdict = match (reduction.status, case.expectation.as_str(), reproduced) {
            (ReductionStatus::Exhausted, _, _) => "Exhausted-Unknown",
            (ReductionStatus::NormalForm, "holds", true) => "Holds-As-Declared",
            (ReductionStatus::NormalForm, "fails", false) => "Fails-As-Declared",
            (ReductionStatus::NormalForm, "holds", false) => "Unexpected-Mismatch",
            (ReductionStatus::NormalForm, "fails", true) => "Unexpected-Match",
            (ReductionStatus::NormalForm, other, _) => {
                return Err(format!(
                    "reading case {} declares expectation {other}",
                    case.label
                ));
            }
        };
        total_contractions += reduction.contractions;
        readings.push(ReadingResult {
            label: case.label.clone(),
            form: case.form.clone(),
            reading: case.reading.clone(),
            expectation: case.expectation.clone(),
            expected: case.expected.clone(),
            observed,
            contractions: reduction.contractions,
            status: reduction.status,
            verdict: verdict.to_string(),
            note: case.note.clone(),
        });
    }

    // The declared renaming of the Iota combinator's source spelling.
    let mut renamings: Vec<RenamingResult> = Vec::new();
    if let Some(declaration) = &contract.renaming {
        let from = declaration
            .from
            .chars()
            .next()
            .filter(|_| declaration.from.chars().count() == 1)
            .ok_or_else(|| "the renaming source spelling must be one character".to_string())?;
        let to = declaration
            .to
            .chars()
            .next()
            .filter(|_| declaration.to.chars().count() == 1)
            .ok_or_else(|| "the renaming target spelling must be one character".to_string())?;
        let directory = output_root.join(&declaration.output);
        std::fs::create_dir_all(&directory)
            .map_err(|e| format!("renamed output directory refused: {e}"))?;
        for program in &contract.renamings {
            let raw = fs::read(root.join(&program.program))
                .map_err(|e| format!("renamed program {} unreadable: {e}", program.label))?;
            let original_sha256 = sha256_hex(&raw);
            let text = std::str::from_utf8(&raw)
                .map_err(|e| format!("renamed program {} is not UTF-8: {e}", program.label))?;
            let original = parse_iota_with(text, IotaSpelling::Documentary)
                .map_err(|e| format!("renamed program {} refused: {e}", program.label))?;
            let renamed_source = rename_iota_source(text, from, to)?;
            let renamed = parse_iota_with(&renamed_source, IotaSpelling::Renamed)
                .map_err(|e| format!("renamed program {} refused: {e}", program.label))?;
            let same_term = term_digest(&original) == term_digest(&renamed);
            // The same declared shape as the corresponding family: a coordinate
            // program is checked on its four-slot application, not bare.
            let kind = program.kind.as_deref().unwrap_or("iota");
            let build = |term: &Term| -> Result<(Term, Option<Term>), String> {
                match kind {
                    "iota" => Ok((term.clone(), None)),
                    "coordinate" => {
                        let order = program.permutation.clone().ok_or_else(|| {
                            format!("renamed program {} declares no permutation", program.label)
                        })?;
                        if order.len() != 4 || order.iter().any(|k| *k > 3) {
                            return Err(format!(
                                "renamed program {} permutation is not four slots",
                                program.label
                            ));
                        }
                        Ok((
                            coordinate_application(term)?,
                            Some(expected_permutation(&order)),
                        ))
                    }
                    other => Err(format!(
                        "renamed program {} declares unsupported kind {other}",
                        program.label
                    )),
                }
            };
            let (original_term, expected) = build(&original)?;
            let (renamed_term, _) = build(&renamed)?;
            let same_term = same_term && term_digest(&original_term) == term_digest(&renamed_term);
            let original_reduction = reduce(&original_term, &contract.limits, false);
            let renamed_reduction = reduce(&renamed_term, &contract.limits, false);
            let structure_match = match (expected.as_ref(), renamed_reduction.term.as_ref()) {
                (Some(expected), Some(actual)) => expected == actual,
                _ => true,
            };
            total_contractions += renamed_reduction.contractions;
            let rules_match = original_reduction.rules == renamed_reduction.rules;
            let peak_nodes_match = original_reduction.peak_nodes == renamed_reduction.peak_nodes;
            let digest_match =
                original_reduction.normal_form_sha256 == renamed_reduction.normal_form_sha256;

            let mut oracle_matched = None;
            if let Some(oracle) = &program.oracle {
                let raw = read_document(&root, &oracle.document, &oracle.document_sha256)
                    .map_err(|e| format!("renamed program {} {e}", program.label))?;
                let document: serde_json::Value = serde_json::from_slice(&raw).map_err(|e| {
                    format!("renamed program {} oracle parse failed: {e}", program.label)
                })?;
                let entry = document.pointer(&oracle.pointer).ok_or_else(|| {
                    format!(
                        "renamed program {} oracle pointer {} missing",
                        program.label, oracle.pointer
                    )
                })?;
                let expected_contractions = entry["contractions"].as_u64();
                let expected_rules = rules_from_json(&entry["rules"]);
                let expected_peak = entry["peak_nodes"].as_u64();
                let expected_digest = entry["normal_form_sha256"].as_str().map(str::to_string);
                oracle_matched = Some(
                    expected_contractions == Some(renamed_reduction.contractions)
                        && expected_rules == Some(renamed_reduction.rules.clone())
                        && expected_peak == Some(renamed_reduction.peak_nodes)
                        && expected_digest == renamed_reduction.normal_form_sha256,
                );
            }
            let file_name = Path::new(&program.program)
                .file_name()
                .map(|name| name.to_string_lossy().to_string())
                .unwrap_or_else(|| program.label.clone());
            let renamed_path = directory.join(file_name);
            fs::write(&renamed_path, format!("{renamed_source}\n"))
                .map_err(|e| format!("renamed output write failed: {e}"))?;
            let renamed_bytes =
                fs::read(&renamed_path).map_err(|e| format!("renamed output read failed: {e}"))?;
            let preserved = same_term
                && rules_match
                && peak_nodes_match
                && digest_match
                && structure_match
                && oracle_matched.unwrap_or(true);
            renamings.push(RenamingResult {
                label: program.label.clone(),
                program: program.program.clone(),
                original_bytes: raw.len() as u64,
                original_sha256,
                original_characters: text.trim().chars().count(),
                renamed_bytes: renamed_bytes.len() as u64,
                renamed_sha256: sha256_hex(&renamed_bytes),
                renamed_characters: renamed_source.chars().count(),
                renamed_path: renamed_path.display().to_string(),
                term_digest_original: term_digest(&original),
                term_digest_renamed: term_digest(&renamed),
                same_term,
                contractions_original: original_reduction.contractions,
                contractions_renamed: renamed_reduction.contractions,
                rules_match,
                peak_nodes_match,
                normal_form_digest_match: digest_match,
                oracle_matched,
                verdict: if preserved {
                    "Preserved-Under-Renaming".to_string()
                } else {
                    "Changed-Under-Renaming".to_string()
                },
                note: program.note.clone(),
            });
        }
    }

    // Declared trace comparison against the independently supplied origin trace.
    let mut trace_rows_compared = 0usize;
    let mut trace_rows_matched = 0usize;
    let mut trace_mismatch: Option<String> = None;
    if let Some(binding) = &contract.trace {
        let raw = read_document(origin_root, &binding.document, &binding.document_sha256)
            .map_err(|e| format!("trace binding refused: {e}"))?;
        let document: serde_json::Value =
            serde_json::from_slice(&raw).map_err(|e| format!("trace parse failed: {e}"))?;
        let rows = document["trace"]
            .as_array()
            .ok_or_else(|| "trace document has no rows".to_string())?;
        let family = contract
            .families
            .iter()
            .find(|family| family.label == binding.label)
            .ok_or_else(|| format!("trace label {} is not a declared family", binding.label))?;
        let program_raw = fs::read(root.join(&family.program))
            .map_err(|e| format!("trace family program unreadable: {e}"))?;
        let program = parse_iota(&String::from_utf8_lossy(&program_raw))?;
        let reduction = reduce(&program, &contract.limits, true);
        for (index, row) in rows.iter().enumerate() {
            let Some(local) = reduction.trace.get(index) else {
                trace_mismatch = Some(format!("local trace ended at step {index}"));
                break;
            };
            trace_rows_compared += 1;
            let same = row["path"].as_str() == Some(local.path.as_str())
                && row["rule"].as_str() == Some(local.rule.as_str())
                && row["nodes"].as_u64() == Some(local.nodes)
                && row["sha256"].as_str() == Some(local.sha256.as_str());
            if same {
                trace_rows_matched += 1;
            } else {
                trace_mismatch = Some(format!(
                    "step {} differs: origin {:?} local {:?}",
                    index + 1,
                    row,
                    serde_json::json!({
                        "path": local.path,
                        "rule": local.rule,
                        "nodes": local.nodes,
                        "sha256": local.sha256,
                    })
                ));
                break;
            }
        }
        if trace_mismatch.is_none() && reduction.trace.len() != rows.len() {
            trace_mismatch = Some(format!(
                "local trace has {} rows against {} origin rows",
                reduction.trace.len(),
                rows.len()
            ));
        }
    }

    // Declared controls. Each is executed and its observation retained.
    let mut controls: Vec<ControlResult> = Vec::new();
    let mut control = |name: &str, expectation: &str, observed: String, passed: bool| {
        controls.push(ControlResult {
            name: name.to_string(),
            expectation: expectation.to_string(),
            observed,
            passed,
        });
    };

    if contract.controls.iter().any(|c| c == "sha256-fips-vectors") {
        let vectors = [
            (
                "",
                "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            ),
            (
                "abc",
                "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            ),
            (
                "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
                "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1",
            ),
        ];
        let mut all = true;
        let mut observed = String::new();
        for (input, expected) in vectors {
            let digest = sha256_hex(input.as_bytes());
            all &= digest == expected;
            let _ = write!(observed, "{}:{} ", input.len(), &digest[..16]);
        }
        control(
            "sha256-fips-vectors",
            "the local SHA-256 reproduces the three FIPS 180-4 vectors",
            observed,
            all,
        );
    }

    if contract.controls.iter().any(|c| c == "digest-falsifier") {
        let target = contract
            .families
            .iter()
            .find(|family| family.kind == "iota" && family.oracle.is_some());
        match target {
            Some(family) => {
                let raw = fs::read(root.join(&family.program)).map_err(|e| e.to_string())?;
                let program = parse_iota(&String::from_utf8_lossy(&raw))?;
                let reduction = reduce(&program, &contract.limits, false);
                let actual = reduction.normal_form_sha256.clone().unwrap_or_default();
                let mut altered = actual.clone();
                let replacement = if actual.starts_with('0') { '1' } else { '0' };
                altered.replace_range(0..1, &replacement.to_string());
                let detected = altered != actual;
                control(
                    "digest-falsifier",
                    "an altered expected digest is refused rather than accepted",
                    format!("altered={} actual={}", &altered[..16], &actual[..16]),
                    detected,
                );
            }
            None => control(
                "digest-falsifier",
                "an altered expected digest is refused rather than accepted",
                "no oracle-bearing iota family declared".to_string(),
                false,
            ),
        }
    }

    if contract.controls.iter().any(|c| c == "order-alternative") {
        let target = contract
            .families
            .iter()
            .find(|family| family.oracle.is_some())
            .ok_or_else(|| "order-alternative requires an oracle-bearing family".to_string())?;
        let raw = fs::read(root.join(&target.program)).map_err(|e| e.to_string())?;
        let program = parse_iota(&String::from_utf8_lossy(&raw))?;
        let declared = reduce(&program, &contract.limits, false);
        let other = reduce_innermost(&program, &contract.limits);
        let differs = declared.normal_form_sha256 != other.normal_form_sha256
            || declared.contractions != other.contractions;
        control(
            "order-alternative",
            "a different declared order changes the counts or the digest",
            format!(
                "declared={}:{} other={}:{}",
                declared.contractions,
                declared
                    .normal_form_sha256
                    .as_deref()
                    .map(|d| &d[..12])
                    .unwrap_or("unknown"),
                other.contractions,
                other
                    .normal_form_sha256
                    .as_deref()
                    .map(|d| &d[..12])
                    .unwrap_or("unknown")
            ),
            differs,
        );
    }

    if contract.controls.iter().any(|c| c == "budget-exhaustion") {
        let target = contract
            .families
            .iter()
            .find(|family| family.kind == "iota" && family.oracle.is_some())
            .ok_or_else(|| "budget-exhaustion requires an oracle-bearing family".to_string())?;
        let raw = fs::read(root.join(&target.program)).map_err(|e| e.to_string())?;
        let program = parse_iota(&String::from_utf8_lossy(&raw))?;
        let tight = Limits {
            contractions_per_family: 16,
            ..contract.limits
        };
        let reduction = reduce(&program, &tight, false);
        let correct = reduction.status == ReductionStatus::Exhausted
            && reduction.normal_form_sha256.is_none()
            && reduction.reason.is_some();
        control(
            "budget-exhaustion",
            "a tight bound reports Unknown with no normal-form claim",
            format!(
                "status={:?} reason={:?}",
                reduction.status, reduction.reason
            ),
            correct,
        );
    }

    if contract.controls.iter().any(|c| c == "non-vacuity") {
        let any_contraction = families.iter().all(|family| family.contractions > 0);
        let matched = families
            .iter()
            .any(|family| family.verdict == "Matched-Frozen-Oracle");
        control(
            "non-vacuity",
            "every family contracts and at least one frozen oracle is matched",
            format!(
                "min_contractions={} frozen_matches={}",
                families.iter().map(|f| f.contractions).min().unwrap_or(0),
                families
                    .iter()
                    .filter(|f| f.verdict == "Matched-Frozen-Oracle")
                    .count()
            ),
            any_contraction && matched,
        );
    }

    if contract.controls.iter().any(|c| c == "source-alteration") {
        let target = contract
            .families
            .first()
            .ok_or_else(|| "source-alteration requires a family".to_string())?;
        let raw = fs::read(root.join(&target.program)).map_err(|e| e.to_string())?;
        let mut altered = raw.clone();
        if let Some(byte) = altered.iter_mut().find(|b| **b == b'*') {
            *byte = b'i';
        }
        let differs = sha256_hex(&altered) != sha256_hex(&raw);
        control(
            "source-alteration",
            "one altered byte changes the source digest",
            format!(
                "altered={} original={}",
                &sha256_hex(&altered)[..16],
                &sha256_hex(&raw)[..16]
            ),
            differs,
        );
    }

    if contract.controls.iter().any(|c| c == "grammar-collision") {
        let murphy = parse_iota("i");
        let case_reading = parse_sexpr("i");
        let declared =
            matches!(murphy, Ok(Term::Const('j'))) && matches!(case_reading, Ok(Term::Const('I')));
        let distinct = murphy.ok() != case_reading.ok();
        control(
            "grammar-collision",
            "the same token denotes different combinators in the two declared grammars",
            format!("same token, distinct readings: {distinct}"),
            declared && distinct,
        );
    }

    if contract
        .controls
        .iter()
        .any(|c| c == "expectation-falsifier-cases")
    {
        match cases.first() {
            Some(first) => {
                let altered = format!("{}-altered", first.expected);
                let refuses = first.observed.as_deref() != Some(altered.as_str());
                control(
                    "expectation-falsifier-cases",
                    "an altered recorded expectation is refused rather than accepted",
                    format!(
                        "case={} observed={:?} altered={:?}",
                        first.label, first.observed, altered
                    ),
                    refuses,
                );
            }
            None => control(
                "expectation-falsifier-cases",
                "an altered recorded expectation is refused rather than accepted",
                "no case declared".to_string(),
                false,
            ),
        }
    }

    if contract.controls.iter().any(|c| c == "variable-inertness") {
        let mut checked = 0usize;
        let mut inert = true;
        for case in &contract.cases {
            let Ok(term) = parse_sexpr(&case.term) else {
                continue;
            };
            if matches!(term, Term::App(ref head, _) if matches!(**head, Term::Var(_))) {
                checked += 1;
                let reduction = reduce(&term, &contract.limits, false);
                inert &= reduction.contractions == 0
                    && reduction.normal_form_is_redex_free == Some(true);
            }
        }
        control(
            "variable-inertness",
            "a case whose head is an opaque variable is already a normal form",
            format!("checked={checked} inert={inert}"),
            checked > 0 && inert,
        );
    }

    if contract
        .controls
        .iter()
        .any(|c| c == "reading-non-discrimination-at-two")
    {
        let pair = [Term::Const('j'), Term::Const('j')];
        let left = nest(&pair, ListReading::LeftNested);
        let right = nest(&pair, ListReading::RightNested);
        let same = matches!((left, right), (Ok(a), Ok(b)) if a == b);
        control(
            "reading-non-discrimination-at-two",
            "a two-element list cannot decide between the two readings",
            format!("readings coincide at two elements: {same}"),
            same,
        );
    }

    if contract
        .controls
        .iter()
        .any(|c| c == "reading-discrimination-from-three")
    {
        let mut differs_from = None;
        let mut all_differ = true;
        for size in 3..=5usize {
            let list = vec![Term::Const('j'); size];
            let left = nest(&list, ListReading::LeftNested).expect("left reading");
            let right = nest(&list, ListReading::RightNested).expect("right reading");
            if left == right {
                all_differ = false;
            }
            if differs_from.is_none() && left != right {
                differs_from = Some(size);
            }
        }
        control(
            "reading-discrimination-from-three",
            "the two readings differ from three elements on and agree below that",
            format!("first difference at {differs_from:?} elements; all differ: {all_differ}"),
            differs_from == Some(3) && all_differ,
        );
    }

    if contract
        .controls
        .iter()
        .any(|c| c == "expectation-falsifier-readings")
    {
        match readings.iter().find(|case| case.expectation == "holds") {
            Some(case) => {
                let altered = format!("{}-altered", case.expected);
                let refuses = case.observed.as_deref() != Some(altered.as_str());
                control(
                    "expectation-falsifier-readings",
                    "an altered expected reading result is refused rather than accepted",
                    format!(
                        "case={} observed={:?} altered={:?}",
                        case.label, case.observed, altered
                    ),
                    refuses,
                );
            }
            None => control(
                "expectation-falsifier-readings",
                "an altered expected reading result is refused rather than accepted",
                "no holding reading case declared".to_string(),
                false,
            ),
        }
    }

    if contract
        .controls
        .iter()
        .any(|c| c == "renaming-refuses-legacy-token")
    {
        let refused = parse_iota_with("i", IotaSpelling::Renamed).is_err();
        let accepted = matches!(
            parse_iota_with("ι", IotaSpelling::Renamed),
            Ok(Term::Const('j'))
        );
        let documentary_kept = matches!(
            parse_iota_with("i", IotaSpelling::Documentary),
            Ok(Term::Const('j'))
        );
        control(
            "renaming-refuses-legacy-token",
            "the renamed spelling refuses `i` while the documentary spelling keeps reading it",
            format!(
                "refused={refused} iota-accepted={accepted} documentary-kept={documentary_kept}"
            ),
            refused && accepted && documentary_kept,
        );
    }

    if contract
        .controls
        .iter()
        .any(|c| c == "renaming-is-not-vacuous")
    {
        let mut real = true;
        let mut described = 0usize;
        for case in &renamings {
            described += 1;
            real &= case.original_sha256 != case.renamed_sha256
                && case.original_characters == case.renamed_characters
                && case.renamed_bytes != case.original_bytes;
        }
        control(
            "renaming-is-not-vacuous",
            "each renamed copy has the same character count, different bytes and a different digest",
            format!("programs={described} real-renaming={real}"),
            described > 0 && real,
        );
    }

    let refreshed = contract
        .controls
        .iter()
        .filter(|name| !controls.iter().any(|c| &c.name == *name))
        .map(|name| ControlResult {
            name: name.clone(),
            expectation: "declared control".to_string(),
            observed: "not implemented in this profile version".to_string(),
            passed: false,
        })
        .collect::<Vec<_>>();
    controls.extend(refreshed);

    let controls_ok = controls.iter().all(|control| control.passed);
    let families_ok = families.iter().all(|family| {
        matches!(
            family.verdict.as_str(),
            "Matched-Frozen-Oracle" | "Matched-Declared-Normal-Form" | "Recorded-No-Oracle"
        )
    });
    let trace_ok = trace_mismatch.is_none();
    let cases_ok = cases
        .iter()
        .all(|case| case.verdict == "Matched-Recorded-Expectation");
    let readings_ok = readings
        .iter()
        .all(|case| case.verdict == "Holds-As-Declared" || case.verdict == "Fails-As-Declared");
    let renamings_ok = renamings
        .iter()
        .all(|case| case.verdict == "Preserved-Under-Renaming");
    let outcome =
        if controls_ok && families_ok && trace_ok && cases_ok && readings_ok && renamings_ok {
            "IotaSubstrateChecked"
        } else {
            "IotaSubstrateMismatched"
        };

    Ok(RunReport {
        schema: "adva.iota-substrate.result.v0".to_string(),
        profile: contract.profile.clone(),
        question: contract.question.clone(),
        level: contract.level.clone(),
        native_admission: "NotGranted".to_string(),
        stable_semantic_api: false,
        outcome: outcome.to_string(),
        limits: contract.limits,
        families,
        controls,
        cases_matched: cases
            .iter()
            .filter(|case| case.matched_recorded_expectation)
            .count(),
        cases_mismatched: cases
            .iter()
            .filter(|case| !case.matched_recorded_expectation)
            .count(),
        transcript_rows_compared: cases
            .iter()
            .filter(|case| case.transcript_agrees.is_some())
            .count(),
        transcript_rows_agreeing: cases
            .iter()
            .filter(|case| case.transcript_agrees == Some(true))
            .count(),
        cases,
        readings_held: readings
            .iter()
            .filter(|case| case.verdict == "Holds-As-Declared")
            .count(),
        readings_failed_as_declared: readings
            .iter()
            .filter(|case| case.verdict == "Fails-As-Declared")
            .count(),
        readings_unexpected: readings
            .iter()
            .filter(|case| {
                case.verdict != "Holds-As-Declared" && case.verdict != "Fails-As-Declared"
            })
            .count(),
        readings,
        renamings_preserved: renamings
            .iter()
            .filter(|case| case.verdict == "Preserved-Under-Renaming")
            .count(),
        renamings,
        checked_families: contract.families.len(),
        frozen_oracle_families,
        total_contractions,
        trace_rows_compared,
        trace_rows_matched,
        acceptance: contract.acceptance.clone(),
        residual: match trace_mismatch {
            Some(mismatch) => format!("{} Trace mismatch retained: {mismatch}", contract.residual),
            None => contract.residual.clone(),
        },
        wall_seconds: started.elapsed().as_secs_f64(),
    })
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn limits() -> Limits {
        Limits {
            contractions_per_family: 20_000,
            nodes_per_family: 200_000,
            seconds_per_family: 30.0,
        }
    }

    #[test]
    fn sha256_matches_fips_vectors() {
        assert_eq!(
            sha256_hex(b""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        );
        assert_eq!(
            sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
        assert_eq!(
            sha256_hex(b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"),
            "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
        );
    }

    #[test]
    fn iota_source_round_trips_through_the_declared_encoding() {
        let term = parse_iota("*ii").expect("source parses");
        assert_eq!(canonical_json(&term), "[\"a\",[\"c\",\"j\"],[\"c\",\"j\"]]");
        assert_eq!(nodes(&term), 3);
    }

    #[test]
    fn iota_rule_rewrites_one_step() {
        // `i a` contracts to `a S K`
        let term = parse_iota("i").expect("source parses");
        let application = Term::App(Box::new(term), Box::new(Term::Var("a".to_string())));
        let mut path = String::new();
        let (next, found, rule) = contract_once(&application, &mut path).expect("a redex exists");
        assert_eq!(rule, 'j');
        assert_eq!(found, "");
        assert_eq!(
            next,
            apps(
                Term::Var("a".to_string()),
                &[Term::Const('S'), Term::Const('K')]
            )
        );
    }

    #[test]
    fn identity_combinator_is_already_normal() {
        let iota_i = apps(
            Term::Const('j'),
            &[apps(
                Term::Const('j'),
                &[apps(Term::Const('j'), &[Term::Const('j')])],
            )],
        );
        let reduction = reduce(&iota_i, &limits(), false);
        assert_eq!(reduction.status, ReductionStatus::NormalForm);
        assert_eq!(reduction.normal_form_is_redex_free, Some(true));
    }

    #[test]
    fn exhaustion_is_unknown_and_never_divergence() {
        // `i i` needs several contractions before it settles.
        let term = parse_iota("*ii").expect("source parses");
        let tight = Limits {
            contractions_per_family: 1,
            ..limits()
        };
        let reduction = reduce(&term, &tight, false);
        assert_eq!(reduction.status, ReductionStatus::Exhausted);
        assert_eq!(reduction.normal_form_sha256, None);
        assert!(reduction.reason.is_some());
    }

    #[test]
    fn bracket_abstraction_matches_a_known_translation() {
        // lambda x. x  translates to I
        let identity = Term::Lam("x".to_string(), Box::new(Term::Var("x".to_string())));
        assert_eq!(ski(&identity).expect("translation"), Term::Const('I'));
        // lambda x. y  translates to K y
        let constant = Term::Lam("x".to_string(), Box::new(Term::Var("y".to_string())));
        assert_eq!(
            ski(&constant).expect("translation"),
            Term::App(
                Box::new(Term::Const('K')),
                Box::new(Term::Var("y".to_string()))
            )
        );
    }

    #[test]
    fn coordinate_application_preserves_the_declared_slot_order() {
        // The C permutation swaps the last two slots; the normal form must show it.
        let order = [0usize, 1, 3, 2];
        let expected = expected_permutation(&order);
        assert_eq!(
            canonical_json(&expected),
            "[\"a\",[\"a\",[\"a\",[\"a\",[\"v\",\"out\"],[\"v\",\"p\"]],[\"v\",\"q\"]],[\"v\",\"s\"]],[\"v\",\"r\"]]"
        );
    }
}
