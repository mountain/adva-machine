"""A bounded documentary structure card, not a mathematical graph importer.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized account proxy; not his review or endorsement.
"""
import difflib
import json
import re

from toolchain.boundary import BoundaryError, digest, strict_json

from .io import read

SCHEMA = "adva.structure-card.v1"
MAX_BYTES = 32768
STATUSES = {"proposed", "reported", "adopted-for-discussion"}


def require(condition, message):
    if not condition:
        raise BoundaryError(message)


def fields(value, expected):
    require(type(value) is dict and set(value) == set(expected.split()),
            f"expected exactly these fields: {expected}")


def text(value):
    require(type(value) is str and 0 < len(value.strip()) <= 2000,
            "expected nonempty text of at most 2000 characters")
    require(all(ord(c) >= 32 or c in "\n\t" for c in value), "control character in text")


def identifier(value):
    require(type(value) is str and re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", value),
            "invalid documentary identifier")


def texts(value, limit=16):
    require(type(value) is list and len(value) <= limit, "text list exceeds its bound")
    for item in value:
        text(item)


def check(raw):
    require(len(raw) <= MAX_BYTES, "structure card exceeds 32 KiB")
    card = strict_json(raw)
    fields(card, "schema id question origin objects relations preserve open_questions request")
    require(card["schema"] == SCHEMA, "unsupported structure card")
    identifier(card["id"])
    for name in ("question", "origin", "request"):
        text(card[name])
    for name in ("preserve", "open_questions"):
        texts(card[name])
    objects = card["objects"]
    relations = card["relations"]
    require(type(objects) is list and 1 <= len(objects) <= 32, "expected 1..32 objects")
    require(type(relations) is list and len(relations) <= 64, "at most 64 relations")
    ids = set()
    for obj in objects:
        fields(obj, "id meaning")
        identifier(obj["id"])
        text(obj["meaning"])
        require(obj["id"] not in ids, "duplicate object identifier")
        ids.add(obj["id"])
    seen = set()
    for relation in relations:
        fields(relation, "from relation to status basis")
        for endpoint in ("from", "to"):
            identifier(relation[endpoint])
            require(relation[endpoint] in ids, "relation refers to an undeclared object")
        for key in ("relation", "basis"):
            text(relation[key])
        require(type(relation["status"]) is str and relation["status"] in STATUSES,
                "relations require proposed, reported or adopted-for-discussion status")
        edge = (relation["from"], relation["relation"], relation["to"])
        require(edge not in seen, "duplicate relation; retain disagreement in a successor card")
        seen.add(edge)
    return card


def load(path):
    raw = read(path, MAX_BYTES)
    return raw, check(raw)


def report(raw, card):
    return {"schema": "adva.structure-card.check.v1", "status": "StructureWellFormed",
            "card_id": card["id"], "card_sha256": digest(raw),
            "objects": len(card["objects"]), "relations": len(card["relations"]),
            "open_questions": len(card["open_questions"]),
            "authority": "documentary-shape-only", "claims_verified": False,
            "publication_admission": "NotChecked", "native_admission": "NotGranted",
            "human_acceptance": "NotInferred"}


def render(card):
    # Preserve every field; do not turn a summary into silent loss of obligations.
    lines = [f"Structure: {card['id']}", f"Question: {card['question']}",
             f"Origin: {card['origin']}", "Objects:"]
    lines.extend(f"- {obj['id']}: {obj['meaning']}" for obj in card["objects"])
    lines.append("Relations:")
    lines.extend(f"- {edge['from']} --{edge['relation']}--> {edge['to']} "
                 f"[{edge['status']}; basis: {edge['basis']}]" for edge in card["relations"])
    for heading, key in (("Preserve", "preserve"), ("Open questions", "open_questions")):
        lines.append(heading + ":")
        lines.extend("- " + item for item in card[key])
        if not card[key]:
            lines.append("- None declared; completeness not established.")
    lines.extend(["Requested reply: " + card["request"],
                  "Reading this card establishes no truth, endorsement or receiving acceptance."])
    return "\n".join(lines)


def compare(left_raw, right_raw):
    left, right = check(left_raw), check(right_raw)
    before = json.dumps(left, ensure_ascii=False, sort_keys=True, indent=2).splitlines()
    after = json.dumps(right, ensure_ascii=False, sort_keys=True, indent=2).splitlines()
    return {"schema": "adva.structure-card.comparison.v1", "status": "DocumentaryComparison",
            "base_sha256": digest(left_raw), "next_sha256": digest(right_raw),
            "changed": left != right,
            "removed_preservation_requirements": [x for x in left["preserve"] if x not in right["preserve"]],
            "removed_open_questions": [x for x in left["open_questions"] if x not in right["open_questions"]],
            "difference": "\n".join(difflib.unified_diff(before, after, fromfile="base", tofile="next", lineterm="")),
            "semantic_equivalence": "NotChecked", "obligations_discharged": False,
            "native_admission": "NotGranted"}
