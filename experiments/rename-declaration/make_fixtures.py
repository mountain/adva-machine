"""Generate the rename-declaration fixtures.

Two kinds of source appear here, and the difference is deliberate.

* The **murphy** source is *not* embedded.  The fixture names the received bytes
  by path and pins them with the digest the admitted unit's `renaming.json`
  records (`files[label=P].original_sha256`), so the run reads the received
  bytes and proves it did.  Embedding a copy would assert that provenance
  instead of checking it.
* The **hand-written** short sources are embedded, and their digests are
  computed here.  They pin the fixture bytes against later drift; they are not
  external records and are not claimed to be.

The declared algebra is the full closure of the two coordinate generators, not
just the four named elements, so that its element-order profile is a genuine
group invariant.
"""

import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "fixtures"
OUT.mkdir(exist_ok=True)

MURPHY_RELATIVE = (
    "knowledge/received/murphy-iota-machine-2026-09-20-v1/materials/murphy.iota"
)
# recorded in mountain/adva murphy-iota-v0/renaming.json as original_sha256 for
# the admitted program P.  This is an external record, not a digest computed here.
MURPHY_SHA256 = "da47f5cf6cdfb49a29e20c688dcb7ef569e758782b2722a71a5c354761f0d1bf"


def find_root():
    """The repository root holding the received murphy materials."""
    candidates = [HERE.parent / "adva-machine", HERE.parents[1]]
    if len(sys.argv) > 1:
        candidates.insert(0, pathlib.Path(sys.argv[1]))
    for candidate in candidates:
        if (candidate / MURPHY_RELATIVE).is_file():
            return candidate
    raise SystemExit(
        "cannot locate the received murphy materials; pass the repository root as argv[1]"
    )


ROOT = find_root()
murphy_path = ROOT / MURPHY_RELATIVE
murphy_bytes = murphy_path.read_bytes()
murphy_actual = hashlib.sha256(murphy_bytes).hexdigest()
if murphy_actual != MURPHY_SHA256:
    raise SystemExit(
        f"the received murphy source does not match its recorded digest: "
        f"{murphy_actual} != {MURPHY_SHA256}"
    )
print(f"root: {ROOT}")
print(
    f"murphy source: {len(murphy_bytes)} bytes, sha256 {murphy_actual[:16]}... "
    "(matches the digest the admitted unit records)"
)


def embedded(text, provenance):
    return {
        "text": text,
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "provenance": provenance,
    }


def received(path, sha256, provenance):
    return {"path": path, "sha256": sha256, "provenance": provenance}


MURPHY_SOURCE = received(
    MURPHY_RELATIVE,
    MURPHY_SHA256,
    "mountain/adva murphy-iota-v0/renaming.json records this digest for the "
    "admitted program P; the received copy under knowledge/ is byte-identical",
)


# --- the group the murphy coordinate laws present --------------------------


def compose(a, b):
    """apply b, then a"""
    return tuple(a[b[i]] for i in range(len(a)))


IDENT = (0, 1, 2, 3)
C = (0, 3, 2, 1)
J = (1, 2, 3, 0)
J2 = compose(J, J)
J3 = compose(J2, J)

ELEMENTS = {"I": IDENT, "C": C, "J": J, "N": J2, "J3": J3}
for suffix, base in (("", IDENT), ("J", J), ("J2", J2), ("J3", J3)):
    ELEMENTS["C" + suffix] = compose(C, base)

assert len(set(ELEMENTS.values())) == 8, "the closure must have eight elements"


def order(perm):
    eye = tuple(range(len(perm)))
    k, p = 1, perm
    while p != eye:
        p, k = compose(p, perm), k + 1
    return k


profile = {}
for perm in ELEMENTS.values():
    profile[order(perm)] = profile.get(order(perm), 0) + 1
profile = {str(k): v for k, v in sorted(profile.items())}
assert profile == {"1": 1, "2": 5, "4": 2}, f"expected the D8 profile, got {profile}"
print(f"declared algebra: {len(ELEMENTS)} elements, order profile {profile} (D8)")

D8 = {"degree": 4, "elements": {k: list(v) for k, v in sorted(ELEMENTS.items())}}
LAWS = [["CC", "I"], ["JJ", "N"], ["JJJJ", "I"], ["CJC", "NJ"], ["NN", "I"]]
LAW_NAMES = ["C", "J", "N", "I"]

IOTA = "\u03b9"

DIALECT_PAIR = {"operators": {"*": 2}, "atoms": ["i", IOTA], "ignored": ["\n"]}
CARRIER = {"acting": "carrier"}
COMBINATOR = {"acting": "combinator", "primitive": ["j"], "derived": ["S", "K", "I"]}
ACTION = {"acting": "action", "identity_action": "e"}


def declaration(name, level, signature, pairs, fixed, source, relations):
    return {
        "schema": "adva.rename-declaration.v0",
        "name": name,
        "level": level,
        "signature": signature,
        "rename": {"pairs": pairs, "fixed_operators": fixed},
        "source": source,
        "relation_sets": relations,
    }


def word_equations(ident, reading, universe, bound, level):
    return {
        "kind": "word_equations",
        "id": ident,
        "universe": universe,
        "bound": bound,
        "level": level,
        "reading": reading,
        "algebra": D8,
        "denotation": {n: n for n in LAW_NAMES},
        "equations": LAWS,
    }


def spelling_fixed(ident, universe, bound, level):
    return {
        "kind": "spelling_fixed",
        "id": ident,
        "universe": universe,
        "bound": bound,
        "level": level,
    }


def label_counts(ident, universe, bound, level, counts):
    return {
        "kind": "label_counts_fixed",
        "id": ident,
        "universe": universe,
        "bound": bound,
        "level": level,
        "counts": counts,
    }


HAND = (
    "a short hand-written fixture source; its digest pins these bytes, it is "
    "not an external record"
)
COMB_HAND = (
    "a short hand-written fixture source over the combinator alphabet; its "
    "digest pins these bytes, it is not an external record"
)

fixtures = {}

# 1. the published rename, measured against three readings of the same laws
fixtures["murphy-iota-valid.json"] = declaration(
    "murphy-iota-renaming-2026-09-20",
    CARRIER,
    DIALECT_PAIR,
    {"i": IOTA},
    ["*"],
    MURPHY_SOURCE,
    [
        spelling_fixed("spelling-fixed", ["i", IOTA, "*", "j", "k", "s"], 6, "carrier"),
        word_equations("tietze", "tietze", LAW_NAMES, 4, "combinator"),
        word_equations("words-relabelled", "words_relabelled", LAW_NAMES, 4, "combinator"),
        word_equations("denotation-moved", "denotation_moved", LAW_NAMES, 4, "combinator"),
    ],
)

# 2. the rename a tokenwise substitution accepts silently: the operator moves
fixtures["operator-renamed.json"] = declaration(
    "operator-token-renamed",
    CARRIER,
    {"operators": {"*": 2}, "atoms": ["i", IOTA]},
    {"*": "i"},
    ["*"],
    embedded("*ii", HAND),
    [spelling_fixed("spelling-fixed", ["i", "*"], 4, "carrier")],
)

# 3. an operator the declaration itself claims to fix is moved anyway
fixtures["fixed-operator-moved.json"] = declaration(
    "fixed-operator-moved",
    CARRIER,
    {"operators": {"*": 2, "\u00b7": 2}, "atoms": ["i"]},
    {"*": "\u00b7"},
    ["*"],
    embedded("*ii", HAND),
    [spelling_fixed("spelling-fixed", ["i", "*", "\u00b7"], 4, "carrier")],
)

# 4. the target token already occurs in the source and is not itself moved
fixtures["collision.json"] = declaration(
    "collision-with-an-incumbent-token",
    CARRIER,
    {"operators": {"*": 2}, "atoms": ["i", "j"]},
    {"i": "j"},
    ["*"],
    embedded("*ij", HAND),
    [spelling_fixed("spelling-fixed", ["i", "j", "*"], 4, "carrier")],
)

# 5. a declared no-op: legal, sound, and reports nothing
fixtures["vacuous.json"] = declaration(
    "declared-no-op",
    CARRIER,
    {"operators": {"*": 2}, "atoms": ["i"]},
    {"i": "i"},
    ["*"],
    embedded("*ii", HAND),
    [spelling_fixed("spelling-fixed", ["i", "*"], 4, "carrier")],
)

# 6. a three-cycle over the alphabet: what a single {from, to} cannot express
fixtures["cyclic-rename.json"] = declaration(
    "three-cycle-over-the-atom-alphabet",
    CARRIER,
    {"operators": {"*": 2}, "atoms": ["i", "j", IOTA]},
    {"i": "j", "j": IOTA, IOTA: "i"},
    ["*"],
    embedded(
        "**ij" + IOTA,
        "a short hand-written fixture source; every target is itself in the "
        "domain, so the cycle is well defined only if substitution is simultaneous",
    ),
    [spelling_fixed("spelling-fixed", ["i", "j", IOTA, "*"], 4, "carrier")],
)

# 7. an over-large universe must be Unknown, never a truncated count
fixtures["oversized-universe.json"] = declaration(
    "universe-beyond-the-declared-bound",
    CARRIER,
    DIALECT_PAIR,
    {"i": IOTA},
    ["*"],
    MURPHY_SOURCE,
    [spelling_fixed("spelling-fixed", ["i", IOTA, "*", "j", "k", "s", "l"], 6, "carrier")],
)

# 8. a combinator-level rename within the derived names: the level admits it,
#    and the spelling relation set at that level admits it too
fixtures["combinator-rename-accepted.json"] = declaration(
    "combinator-rename-within-the-derived-names",
    COMBINATOR,
    {"operators": {"*": 2}, "atoms": ["j", "S", "K", "I"]},
    {"S": "K", "K": "I", "I": "S"},
    ["*"],
    embedded("*jS", COMB_HAND),
    [spelling_fixed("spelling-fixed", ["j", "S", "K", "I", "*"], 5, "combinator")],
)

# 9. the same rename, now measured against the frozen rule histogram: the counts
#    separate the derived names, so the rename is visible after all
fixtures["combinator-rename-seen-by-counts.json"] = declaration(
    "combinator-rename-measured-by-the-frozen-counts",
    COMBINATOR,
    {"operators": {"*": 2}, "atoms": ["j", "S", "K", "I"]},
    {"S": "K", "K": "I", "I": "S"},
    ["*"],
    embedded("*jS", COMB_HAND),
    [
        spelling_fixed("spelling-fixed", ["j", "S", "K", "I", "*"], 5, "combinator"),
        label_counts(
            "frozen-rule-counts",
            ["j", "S", "K", "I"],
            4,
            "combinator",
            {"j": 372, "S": 296, "K": 250, "I": 1},
        ),
    ],
)

# 10. the level check itself: the primitive moved onto a name it introduces
fixtures["combinator-level-violation.json"] = declaration(
    "primitive-moved-onto-a-derived-name",
    COMBINATOR,
    {"operators": {"*": 2}, "atoms": ["j", "S", "K", "I"]},
    {"j": "S"},
    ["*"],
    embedded("*jS", COMB_HAND),
    [spelling_fixed("spelling-fixed", ["j", "S", "K", "I", "*"], 5, "combinator")],
)

# 11. the level check at the action layer: the identity action is moved
fixtures["action-level-identity-moved.json"] = declaration(
    "identity-action-moved-without-declaring-it",
    ACTION,
    {"operators": {"*": 2}, "atoms": ["e", "m", "n"]},
    {"e": "n"},
    ["*"],
    embedded(
        "*em",
        "action names are written as single characters because the declared "
        "signature is a character signature; e is the action that does nothing",
    ),
    [spelling_fixed("spelling-fixed", ["e", "m", "n", "*"], 4, "action")],
)

for filename, body in fixtures.items():
    path = OUT / filename
    path.write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {path.relative_to(HERE)}")

MURPHY_NAME = "murphy-iota-renaming-2026-09-20"
INVARIANTS = {
    "kernel_plus_visible_equals_admissible": True,
    "every_rename_that_moves_nothing_is_in_the_kernel": True,
}

contract = {
    "schema": "adva.rename-declaration.contract.v0",
    "profile": "rename-declaration-v0",
    "question": (
        "Can a rename be declared so that its fixed signature and its level are "
        "checked rather than asserted in prose, and so that the renames its "
        "recorded relation set cannot tell apart are published rather than left "
        "implicit?"
    ),
    "level": (
        "Research-local executable contract over declared finite alphabets and "
        "one declared finite algebra. No ValueType, OperationSpec, registry "
        "entry, IR version, Seal or stable semantic type is added; native "
        "admission is NotGranted."
    ),
    "assumptions": [
        "The murphy source is read by path from the received materials under "
        "knowledge/ and its SHA-256 is verified against the digest the admitted "
        "unit's renaming.json records; the fixture does not embed a copy of it.",
        "The declared algebra is the full closure of the two coordinate "
        "generators on four slots, so its element-order profile is a group "
        "invariant and identifies D8. That the seven iota terms realize these "
        "laws was checked elsewhere (run-04-murphy-renamed) and is not re-checked "
        "here.",
        "A signature may know both spellings, because a renamed source cannot be "
        "parsed by a signature that knows only the old one.",
        "Renames are partial bijections of a declared name universe, so the "
        "enumerated set is the symmetric inverse monoid I_X, not Sym(X).",
        "The collision rule is relative to each relation set's own occupied "
        "tokens: re-spelling a source collides with the source, re-spelling an "
        "equation collides with the letters the equation uses, re-spelling a "
        "label collides with the labels. Tietze's generator replacement is legal "
        "only for a fresh symbol, and that freshness is exactly this set.",
        "Each level is distinguished by one structure: the signature at the "
        "carrier level, the primitive/derived partition at the combinator level, "
        "and the single action that does nothing at the action level.",
        "'Apply the declared renames in order' is NOT assumed to be the inverse "
        "monoid product; the two differ, and the difference is asserted in a "
        "unit test rather than papered over.",
    ],
    "limits": {
        "max_universe_size": 6,
        "max_monoid_order_enumerated": 13327,
        "parse_depth": 512,
    },
    "controls": [
        {
            "id": "the-source-is-the-bytes-the-declaration-names",
            "declaration": MURPHY_NAME,
            "expect": {"digest_verified": True},
        },
        {
            "id": "published-rename-is-accepted",
            "declaration": MURPHY_NAME,
            "expect": {"outcome": "Accepted"},
        },
        {
            "id": "the-declared-algebra-is-d8",
            "declaration": MURPHY_NAME,
            "expect": {"algebra_order_profile": {"1": 1, "2": 5, "4": 2}},
        },
        {
            "id": "operator-renaming-is-refused-on-arity",
            "declaration": "operator-token-renamed",
            "expect": {"outcome": "Refused", "violation_contains": "KindChanged"},
        },
        {
            "id": "a-declaration-contradicting-its-own-fixed-set-is-refused",
            "declaration": "fixed-operator-moved",
            "expect": {
                "outcome": "Refused",
                "violation_contains": "FixedOperatorMoved",
            },
        },
        {
            "id": "a-collision-with-an-incumbent-token-is-refused",
            "declaration": "collision-with-an-incumbent-token",
            "expect": {"outcome": "Refused", "collisions_nonempty": True},
        },
        {
            "id": "a-vacuous-rename-is-refused",
            "declaration": "declared-no-op",
            "expect": {"outcome": "Refused"},
        },
        {
            "id": "a-three-cycle-is-expressible-and-accepted",
            "declaration": "three-cycle-over-the-atom-alphabet",
            "expect": {"outcome": "Accepted"},
        },
        {
            "id": "an-over-large-universe-is-unknown-not-truncated",
            "declaration": "universe-beyond-the-declared-bound",
            "expect": {"outcome": "Unknown"},
        },
        {
            # the reading under which "presentation-only" is true by
            # construction: its verdict cannot fail, so its kernel is the whole
            # admissible set and it certifies nothing
            "id": "the-tietze-reading-certifies-nothing",
            "declaration": MURPHY_NAME,
            "relation_set": "tietze",
            "expect": dict(
                INVARIANTS,
                kernel_is_total=True,
                kernel_equals_admissible=True,
                has_non_abelian_witness=True,
            ),
        },
        {
            # keeping the old meaning attached to a new spelling is the
            # corruption reading, and it refuses almost everything
            "id": "re-spelling-without-moving-the-meaning-is-not-vacuous",
            "declaration": MURPHY_NAME,
            "relation_set": "words-relabelled",
            "expect": dict(INVARIANTS, kernel_strictly_inside_admissible=True),
        },
        {
            # moving the role while keeping the spelling is the other direction,
            # and it refuses almost everything too
            "id": "moving-the-role-without-the-spelling-is-not-vacuous",
            "declaration": MURPHY_NAME,
            "relation_set": "denotation-moved",
            "expect": dict(INVARIANTS, kernel_strictly_inside_admissible=True),
        },
        {
            "id": "no-kernel-member-touches-the-source-under-spelling-fixed",
            "declaration": MURPHY_NAME,
            "relation_set": "spelling-fixed",
            "expect": dict(INVARIANTS, kernel_touching_the_source_len=0),
        },
        {
            # the level check admits a rename that respects the derivation
            "id": "a-combinator-rename-within-the-derived-names-is-accepted",
            "declaration": "combinator-rename-within-the-derived-names",
            "expect": {"outcome": "Accepted"},
        },
        {
            # and the measurement can still see it: the frozen counts separate
            # the derived names, so the rename is not presentation-only
            "id": "frozen-counts-see-a-derived-name-rename",
            "declaration": "combinator-rename-measured-by-the-frozen-counts",
            "expect": {"outcome": "Refused"},
        },
        {
            "id": "moving-the-primitive-onto-a-derived-name-is-refused",
            "declaration": "primitive-moved-onto-a-derived-name",
            "expect": {
                "outcome": "Refused",
                "violation_contains": "PartitionNotPreserved",
            },
        },
        {
            "id": "moving-the-identity-action-is-refused",
            "declaration": "identity-action-moved-without-declaring-it",
            "expect": {
                "outcome": "Refused",
                "violation_contains": "IdentityActionMoved",
            },
        },
        {
            # the murphy rename acts on the carrier; its coordinate laws are
            # statements about combinator names, so that measurement is
            # cross-level, and the run has to say so rather than let it pass
            "id": "the-murphy-laws-are-a-cross-level-measurement",
            "declaration": MURPHY_NAME,
            "relation_set": "tietze",
            "expect": {"cross_level_is": True, "measuring_level_is": "combinator"},
        },
        {
            "id": "the-murphy-spelling-relation-measures-at-the-acting-level",
            "declaration": MURPHY_NAME,
            "relation_set": "spelling-fixed",
            "expect": {"cross_level_is": False, "measuring_level_is": "carrier"},
        },
    ],
    "acceptance": (
        "Every declaration must reach its declared outcome, every declared "
        "control must behave as declared, and every source digest must verify "
        "before any relation is evaluated. The kernel witnesses must be present "
        "for every relation set whose universe is within the declared bound, and "
        "a universe beyond the bound must produce Unknown with a stated reason "
        "rather than a truncated count. The invariants kernel + visible = "
        "admissible, and every rename that moves nothing is in the kernel, must "
        "hold for every relation set. A control that does not hold fails the run "
        "and is retained in the result."
    ),
    "residual": (
        "This is a research-local contract, not a native Adva operation: no "
        "ValueType, OperationSpec, registry entry, IR version or Seal is "
        "created, and native admission is NotGranted. It does not re-derive the "
        "murphy counted witnesses, digests or traces; reproducing those needs "
        "the machine substrate and is out of scope, so the relation sets "
        "declared here are the coordinate laws and the source spelling, not the "
        "full frozen evidence. The kernel witnesses are statements about the "
        "declared finite universes and the declared relation sets only, and they "
        "say nothing about any relation set not declared. The algebra is one "
        "declared realization; that the iota terms realize these laws was "
        "checked elsewhere and is not re-checked here. The level check enforces "
        "one distinguishing structure per level and does not derive the level of "
        "an arbitrary name, nor decide whether a cross-level measurement is "
        "legitimate -- it reports that one occurred. These checks are executed "
        "from the crate directory and are not run by the repository CI, which "
        "does not build a separate workspace root. The exact kernel orders are "
        "reported rather than pinned as controls: the controls assert invariants "
        "that hold by construction, so a failing control means the checker is "
        "wrong rather than that a prediction was optimistic. Nothing here shows "
        "that the murphy naming is the intended spelling of any other consumer."
    ),
    "declarations": sorted(fixtures),
}

(OUT / "contract.json").write_text(
    json.dumps(contract, indent=2, ensure_ascii=False) + "\n"
)
print(f"wrote fixtures/contract.json with {len(contract['controls'])} controls")
