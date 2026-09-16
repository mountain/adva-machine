"""Supervise existing Rust judgments; never write a transported material.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized account proxy; not his review or endorsement.
"""
from pathlib import Path
import re
import sys

import blake3

from toolchain.boundary import digest, strict_json, BoundaryError
from toolchain.process import Account, Exhausted

from .io import binary_digest, plain, read
from .structure import check as check_structure, fields, require, text

SCHEMA = "adva.exchange-routine.request.v1"
LIMITS = {"wall": 30, "cpu": 25, "launches": 4, "native_launches": 4,
          "artifacts": 8 * 1024**2}
ATTEMPTS = (("send-1", "send"), ("receive-1", "receive"),
            ("replay-1", "receive"), ("ack-1", "acknowledge"))


def b3(raw):
    return blake3.blake3(raw).hexdigest()


def pin(value):
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value), "invalid digest")


def outside_repository(path):
    path = plain(path)
    require(not any((p / ".git").exists() or (p / ".git").is_symlink()
                    or ((p / "HEAD").is_file() and (p / "objects").is_dir() and (p / "refs").is_dir())
                    for p in (path, *path.parents)),
            "audit output must be outside repository directories")
    return path


def preflight(request_path, expected, account):
    raw = read(request_path, 32768)
    account.save("request-original.json", raw)
    pin(expected)
    require(digest(raw) == expected, "request pin mismatch")
    q = strict_json(raw)
    fields(q, "schema binary contract publication_record source receiver acknowledgment structure_member")
    require(q["schema"] == SCHEMA, "unsupported exchange routine")
    fields(q["binary"], "path sha256")
    fields(q["contract"], "path blake3")
    fields(q["receiver"], "store name context")
    pin(q["binary"]["sha256"])
    pin(q["contract"]["blake3"])
    for key in ("name", "context"):
        text(q["receiver"][key])

    def path(value):
        text(value)
        p = Path(value)
        return plain(p if p.is_absolute() else request_path.parent / p)

    paths = {"binary": path(q["binary"]["path"]), "contract": path(q["contract"]["path"]),
             "publication": path(q["publication_record"]), "source": path(q["source"]),
             "store": path(q["receiver"]["store"])}
    if q["acknowledgment"] is None:
        paths["ack"] = account.root / "sender/acknowledgment.json"
        paths["ack"].parent.mkdir()
    else:
        paths["ack"] = path(q["acknowledgment"])
        require(not paths["ack"].is_relative_to(account.root),
                "explicit acknowledgment cannot collide with supervisor audit files")
    for key in ("source", "store"):
        require(paths[key].is_dir(), f"{key} directory must already exist")
        require(not account.root.is_relative_to(paths[key]) and not paths[key].is_relative_to(account.root),
                "audit output cannot overlap source or receiving store")
    require(not paths["ack"].exists() and paths["ack"].parent.is_dir(),
            "acknowledgment needs a fresh path with an existing parent")
    require(not paths["ack"].is_relative_to(paths["store"]),
            "sender acknowledgment cannot modify the receiver store")
    binary_hash, binary_bytes = binary_digest(paths["binary"])
    require(binary_hash == q["binary"]["sha256"], "selected executable differs from pinned binary")
    contract_raw = read(paths["contract"], 262144)
    require(b3(contract_raw) == q["contract"]["blake3"], "contract pin mismatch")
    c = strict_json(contract_raw)
    require(type(c) is dict and c.get("schema") == "adva.communication.contract.v1"
            and c.get("profile") == "documentary-library-entry-v1", "unsupported receiving contract")
    require(type(c.get("exchange_id")) is str and re.fullmatch(r"[a-zA-Z0-9_-]{1,96}", c["exchange_id"]),
            "invalid native exchange coordinate")
    require(c.get("receiver") == q["receiver"]["name"] and c.get("context") == q["receiver"]["context"],
            "independent receiver/context mismatch")
    require(type(c.get("read_budget")) is int and 0 <= c["read_budget"] <= 8388608,
            "invalid native read budget")
    publication_raw = read(paths["publication"], 262144)
    require(b3(publication_raw) == c.get("publication_record_blake3"), "publication record pin mismatch")
    p = strict_json(publication_raw)
    require(type(p) is dict and p.get("status") == "admitted", "publication review is not admitted")
    # Rust performs the complete existing profile checks, including review coverage.
    account.save("contract.json", contract_raw)
    account.save("publication-record.json", publication_raw)
    if q["structure_member"] is not None:
        text(q["structure_member"])
        require(type(c.get("files")) is list, "missing contract files")
        members = [f for f in c["files"] if type(f) is dict and f.get("source") == q["structure_member"]]
        require(len(members) == 1, "structure card must be an actual bound payload member")
        member = members[0]
        relative = Path(q["structure_member"])
        require(not relative.is_absolute() and ".." not in relative.parts, "invalid structure member path")
        card_raw = read(paths["source"] / relative, 32768)
        require(b3(card_raw) == member.get("blake3") and digest(card_raw) == member.get("sha256")
                and len(card_raw) == member.get("bytes"), "structure member pin mismatch")
        check_structure(card_raw)
    account.remaining()
    repo = Path(__file__).resolve().parents[1]
    producer_files = ["adva-exchange", "toolchain/boundary.py", "toolchain/process.py", *[
        "exchange_routine/" + name for name in ("__init__.py", "cli.py", "io.py", "run.py", "structure.py")]]
    account.save("producer.json", {"schema": "adva.exchange-routine.producer.v1",
                 "python_version": sys.version, "source_sha256": {p: digest(read(repo / p, 262144)) for p in producer_files},
                 "authority": "local producer integrity, not authenticated identity"})
    account.save("plan.json", {"schema": "adva.exchange-routine.plan.v1", "request_sha256": expected,
                 "contract_blake3": q["contract"]["blake3"], "binary_sha256": binary_hash,
                 "binary_bytes_hashed": binary_bytes, "automatic_retries": 0,
                 "attempts": [{"attempt": label, "action": action} for label, action in ATTEMPTS],
                 "maximum_native_read_bytes": 4 * c["read_budget"], "supervisor_limits": LIMITS,
                 "source_retirement": "NotPermitted", "publication_review": "BoundRecordNotRightsOracle"})
    return q, c, paths


def execute(request_path, expected, output):
    request_path = plain(request_path)
    # No input is copied into a public repository when preflight rejects it.
    output = outside_repository(output)
    account = Account(output, **LIMITS)
    report = {"schema": "adva.exchange-routine.result.v1", "status": "Unknown",
              "request_sha256": expected, "observations": [], "receiver_observation": "Unknown",
              "sender_observation": "Unknown", "native_admission": "NotGranted",
              "human_acceptance": "NotInferred", "automatic_retries": 0, "stage": "preflight"}
    code = 3
    try:
        q, c, paths = preflight(request_path, expected, account)
        contract_pin = q["contract"]["blake3"]
        envelope = account.root / "envelope.json"
        receipt = paths["store"] / c["exchange_id"] / "receipt.json"
        common = ["--contract", str(account.root / "contract.json"), "--expect-contract", contract_pin,
                  "--publication-record", str(account.root / "publication-record.json")]
        receive = ["--envelope", str(envelope), "--store", str(paths["store"]),
                   "--receiver", q["receiver"]["name"], "--context", q["receiver"]["context"]]
        arguments = [["--source", str(paths["source"]), "--output", str(envelope)], receive, receive,
                     ["--envelope", str(envelope), "--receipt", str(receipt), "--output", str(paths["ack"])]]
        successes = ({"Sent"}, {"AcceptedDocumentary", "AlreadyAccepted"}, {"AlreadyAccepted"}, {"Acknowledged"})
        for (label, action), extra, permitted in zip(ATTEMPTS, arguments, successes, strict=True):
            report["stage"] = label
            command = [str(paths["binary"]), "communicate", action, *common, "--attempt", label, *extra]
            exit_code, stdout, _ = account.child(label, command, native=True)
            observation = strict_json(stdout)
            require(type(observation) is dict, "malformed native observation")
            require(observation.get("action") == action and observation.get("attempt") == label
                    and observation.get("supplied_contract_blake3") == contract_pin,
                    "native observation context differs")
            report["observations"].append(observation)
            if exit_code != 0:
                require((exit_code, observation.get("status")) in ((2, "Rejected"), (3, "Unknown")),
                        "unexpected native failure status")
                report.update(status=observation["status"], reason=observation.get("reason"))
                code = exit_code
                break
            require(observation.get("status") in permitted, "unexpected native successful disposition")
            if action == "receive":
                report["receiver_observation"] = observation["status"]
                expected_effect = 1 if observation["status"] == "AcceptedDocumentary" else 0
                require(observation.get("acceptance_effects") == expected_effect,
                        "receiving status and acceptance effects disagree")
            if label == "replay-1":
                require(observation.get("acceptance_effects") == 0, "replay repeated acceptance effects")
            account.remaining()
        else:
            report["stage"] = "retained-bindings"
            envelope_hash = b3(read(envelope, 2097152))
            receipt_hash = b3(read(receipt, 262144))
            ack_raw = read(paths["ack"], 262144)
            ack = strict_json(ack_raw)
            require(type(ack) is dict and ack.get("contract_blake3") == contract_pin
                    and ack.get("envelope_blake3") == envelope_hash and ack.get("receipt_blake3") == receipt_hash
                    and ack.get("status") == "Acknowledged" and ack.get("native_admission") == "NotGranted",
                    "retained acknowledgment binding mismatch")
            observations = report["observations"]
            require(observations[0].get("envelope_blake3") == envelope_hash
                    and all(v.get("receipt_blake3") == receipt_hash for v in observations[1:]),
                    "native observations differ from retained bytes")
            require(all(type(v.get("bytes_read")) is int and 0 <= v["bytes_read"] <= c["read_budget"]
                        for v in observations), "native resource account exceeds contract")
            account.remaining()
            report.update(status="CompletedDocumentaryExchange", stage="complete", sender_observation="Acknowledged",
                          envelope_blake3=envelope_hash, receipt_blake3=receipt_hash,
                          acknowledgment_path=str(paths["ack"]), receiver_receipt_path=str(receipt),
                          acknowledgment_blake3=b3(ack_raw), aggregate_native_read_bytes=sum(v["bytes_read"] for v in observations),
                          new_acceptance_effects=observations[1].get("acceptance_effects"), source_retirement="NotPerformed")
            code = 0
    except Exhausted as error:
        report.update(status="Unknown", reason=str(error))
    except (BoundaryError, ValueError, TypeError, KeyError, RecursionError) as error:
        report.update(status="Refused", reason=str(error))
        code = 2
    except OSError as error:
        report.update(status="Unknown", reason=str(error))
    report["cost"] = account.cost()
    try:
        account.save("result.json", report)
    except (Exhausted, OSError) as error:
        # Earlier native acceptance may have happened; preserve that observation.
        report.update(status="Unknown", reason=f"could not retain final report: {error}")
        code = 3
    return report, code
