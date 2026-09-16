//! Original synthetic fixtures contributed under Unknown v0.3 by ChatGPT (OpenAI).
//! Exercise observable publication, delivery and failure boundaries through the CLI.
use serde_json::{Value, json};
use std::{
    fs,
    path::PathBuf,
    process::Command,
    sync::atomic::{AtomicU64, Ordering},
};

static NEXT: AtomicU64 = AtomicU64::new(0);
const DATA: &[u8] = b"{\"role\":\"Surface\"}\n";
const SHA: &str = "6c38698180feeb744fbb7f095203e434da081b444314bdcc79a11164831aeaa1";
fn hash(b: &[u8]) -> String {
    blake3::hash(b).to_hex().to_string()
}
struct Fixture {
    root: PathBuf,
}
impl Fixture {
    fn new() -> Self {
        let root = std::env::temp_dir().join(format!(
            "adva-communication-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&root).unwrap();
        fs::create_dir_all(root.join("source/names")).unwrap();
        fs::create_dir(root.join("store")).unwrap();
        fs::write(root.join("source/names/role.json"), DATA).unwrap();
        let f = Self { root };
        let entry = json!({"key":"logic-fixture", "home":"logic", "title":"Original fixture", "domains":["logic"],
            "theory":{"name":"documentary fixture", "version":"1"}, "scope":"Documentary reference only",
            "recorded_status":"proposed-document", "checker":null, "geometry_lineage":null, "evidence":[],
            "assumptions":["Synthetic labels"], "reuse_requires":["Keep reference context"], "open_obligations":["No human acceptance"],
            "materials":[{"path":"adva-library/names/role.json", "sha256":SHA}]});
        f.write("source/catalog.json", &json!({"entries":[entry]}));
        f.write("review.json", &json!({"schema":"adva.publication-admission.v1", "status":"admitted", "resource_id":"fixture",
            "eligible_basis":"project-original", "files":[{"path":"knowledge/received/fixture/materials/names/role.json",
                "bytes":DATA.len(), "sha256":SHA, "blake3":hash(DATA)}],
            "provenance":{"source_url":"https://github.com/mountain/adva-library", "source_version":"a".repeat(40),
                "creator_or_rights_holder":"ChatGPT fixture contributor", "publication_basis_evidence_urls":["https://github.com/mountain/adva-library"],
                "rights_holder_authority_evidence":"Synthetic test material contributed under Unknown v0.3",
                "jurisdictions_and_limitations":"Fixture attestation; not a legal judgment", "incorporated_components":[], "transformations":[]},
            "review":{"reviewer":"ChatGPT (OpenAI)", "reviewed_at":"2026-09-16", "decision_reason":"Original test fixture",
                "all_components_reviewed":true, "output_publication_reviewed":true, "unresolved_questions":[]}}));
        f.write("contract.json", &json!({"schema":"adva.communication.contract.v1", "profile":"documentary-library-entry-v1",
            "exchange_id":"fixture", "sender":"library", "receiver":"knowledge", "context":"reference-fixture", "purpose":"documentary-reference",
            "origin":{"repository":"https://github.com/mountain/adva-library", "revision":"a".repeat(40), "catalog_path":"catalog.json",
                "catalog_blake3":hash(&f.bytes("source/catalog.json"))},
            "entry_key":"logic-fixture", "home":"logic", "entry_blake3":hash(&serde_json::to_vec(&entry).unwrap()),
            "publication_record_blake3":hash(&f.bytes("review.json")), "read_budget":8_388_608,
            "dependency_policy":"retain-references-no-execution",
            "checker":{"implementation_blake3":hash(include_bytes!("../src/bin/support/communication_cli.rs")),
                "cargo_lock_blake3":hash(include_bytes!(concat!(env!("CARGO_MANIFEST_DIR"), "/../../Cargo.lock")))},
            "files":[{"source":"names/role.json", "destination":"materials/names/role.json",
                "bytes":DATA.len(), "sha256":SHA, "blake3":hash(DATA)}]}));
        f
    }
    fn bytes(&self, p: &str) -> Vec<u8> {
        fs::read(self.root.join(p)).unwrap()
    }
    fn read(&self, p: &str) -> Value {
        serde_json::from_slice(&self.bytes(p)).unwrap()
    }
    fn write(&self, p: &str, v: &Value) {
        fs::write(self.root.join(p), serde_json::to_vec_pretty(v).unwrap()).unwrap();
    }
    fn edit(&self, p: &str, change: impl FnOnce(&mut Value)) {
        let mut v = self.read(p);
        change(&mut v);
        self.write(p, &v);
    }
    fn repin_review(&self) {
        self.edit("contract.json", |c| {
            c["publication_record_blake3"] = hash(&self.bytes("review.json")).into()
        });
    }
    fn repin_envelope(&self) {
        self.edit("envelope.json", |e| {
            e["contract_blake3"] = hash(&self.bytes("contract.json")).into()
        });
    }
    fn run(&self, action: &str, extra: &[&str]) -> (i32, Value) {
        let o = Command::new(env!("CARGO_BIN_EXE_adva"))
            .current_dir(&self.root)
            .args([
                "communicate",
                action,
                "--contract",
                "contract.json",
                "--expect-contract",
                &hash(&self.bytes("contract.json")),
                "--publication-record",
                "review.json",
            ])
            .args(["--attempt", "test-invocation"])
            .args(extra)
            .output()
            .unwrap();
        let v = serde_json::from_slice(&o.stdout).unwrap_or_else(|_| {
            panic!(
                "stdout={}, stderr={}",
                String::from_utf8_lossy(&o.stdout),
                String::from_utf8_lossy(&o.stderr)
            )
        });
        (o.status.code().unwrap(), v)
    }
    fn send(&self) -> (i32, Value) {
        self.run("send", &["--source", "source", "--output", "envelope.json"])
    }
    fn receive(&self) -> (i32, Value) {
        self.run(
            "receive",
            &[
                "--envelope",
                "envelope.json",
                "--store",
                "store",
                "--receiver",
                "knowledge",
                "--context",
                "reference-fixture",
            ],
        )
    }
    fn ack(&self) -> (i32, Value) {
        self.run(
            "acknowledge",
            &[
                "--envelope",
                "envelope.json",
                "--receipt",
                "store/fixture/receipt.json",
                "--output",
                "ack.json",
            ],
        )
    }
    fn empty(&self) {
        assert_eq!(fs::read_dir(self.root.join("store")).unwrap().count(), 0);
    }
    fn sent(&self) {
        let (code, v) = self.send();
        assert_eq!(code, 0, "{v}");
        assert_eq!(v["receiver_observation"], "Unknown");
        self.empty();
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        fs::remove_dir_all(&self.root).unwrap();
    }
}

#[test]
fn send_receive_repeat_and_ack_keep_obligations_and_source() {
    let f = Fixture::new();
    f.sent();
    let (code, v) = f.receive();
    assert_eq!(code, 0, "{v}");
    assert_eq!(v["acceptance_effects"], 1);
    assert_eq!(f.bytes("source/names/role.json"), DATA);
    assert_eq!(f.bytes("store/fixture/materials/names/role.json"), DATA);
    let receipt = f.bytes("store/fixture/receipt.json");
    let r = f.read("store/fixture/receipt.json");
    assert_eq!(
        r["catalog_entry"],
        f.read("source/catalog.json")["entries"][0]
    );
    assert_eq!(r["native_admission"], "NotGranted");
    assert_eq!(r["semantic_verification"], "NotRun");
    let (code, v) = f.receive();
    assert_eq!(code, 0, "{v}");
    assert_eq!(v["status"], "AlreadyAccepted");
    assert_eq!(v["acceptance_effects"], 0);
    assert_eq!(f.bytes("store/fixture/receipt.json"), receipt);
    let (code, v) = f.ack();
    assert_eq!(code, 0, "{v}");
    assert_eq!(v["receipt_blake3"], hash(&receipt));
}

#[test]
fn missing_reply_is_unknown_and_does_not_acknowledge() {
    let f = Fixture::new();
    f.sent();
    let (code, v) = f.ack();
    assert_eq!(code, 3);
    assert_eq!(v["status"], "Unknown");
    assert!(!f.root.join("ack.json").exists());
    f.empty();
}

#[test]
fn wrong_context_or_interface_has_no_acceptance_effect() {
    for (receiver, context) in [
        ("different", "reference-fixture"),
        ("knowledge", "different"),
    ] {
        let f = Fixture::new();
        f.sent();
        let (code, _) = f.run(
            "receive",
            &[
                "--envelope",
                "envelope.json",
                "--store",
                "store",
                "--receiver",
                receiver,
                "--context",
                context,
            ],
        );
        assert_eq!(code, 2);
        f.empty();
    }
}

#[test]
fn pending_incomplete_and_nonoriginal_publication_records_are_refused() {
    for case in 0..5 {
        let f = Fixture::new();
        f.edit("review.json", |p| match case {
            0 => p["status"] = json!("pending"),
            1 => p["review"]["reviewer"] = json!(""),
            2 => p["eligible_basis"] = json!("MIT"),
            3 => p["review"]["unresolved_questions"] = json!(["source rights"]),
            _ => p["review"]["output_publication_reviewed"] = json!(false),
        });
        f.repin_review();
        let (code, _) = f.send();
        assert_eq!(code, 2);
        assert!(!f.root.join("envelope.json").exists());
        f.empty();
    }
}

#[test]
fn changed_payload_missing_material_and_changed_obligations_are_refused() {
    for case in 0..3 {
        let f = Fixture::new();
        f.sent();
        f.edit("envelope.json", |e| match case {
            0 => e["payloads"][0]["bytes"][0] = json!(0),
            1 => e["payloads"] = json!([]),
            _ => e["entry"]["open_obligations"] = json!([]),
        });
        assert_eq!(f.receive().0, 2);
        f.empty();
    }
}

#[test]
fn changed_source_and_catalog_are_refused_before_send() {
    for case in 0..2 {
        let f = Fixture::new();
        if case == 0 {
            fs::write(f.root.join("source/names/role.json"), b"changed").unwrap();
        } else {
            f.edit("source/catalog.json", |v| {
                v["entries"][0]["home"] = json!("geometry")
            });
        }
        assert_eq!(f.send().0, 2);
        assert!(!f.root.join("envelope.json").exists());
    }
}

#[test]
fn partial_stage_is_retained_with_unknown_and_no_automatic_retry() {
    let f = Fixture::new();
    f.sent();
    fs::create_dir(f.root.join("store/.fixture.pending")).unwrap();
    fs::write(
        f.root.join("store/.fixture.pending/partial"),
        b"retained failure",
    )
    .unwrap();
    let (code, v) = f.receive();
    assert_eq!(code, 3);
    assert_eq!(v["automatic_retry"], false);
    assert_eq!(
        f.bytes("store/.fixture.pending/partial"),
        b"retained failure"
    );
    assert!(!f.root.join("store/fixture").exists());
    assert!(!f.root.join("store/.fixture.lock").exists());
}

#[test]
fn active_or_stale_lock_does_not_start_another_receiver() {
    let f = Fixture::new();
    f.sent();
    fs::write(f.root.join("store/.fixture.lock"), b"other invocation").unwrap();
    assert_eq!(f.receive().0, 3);
    assert!(!f.root.join("store/fixture").exists());
    assert_eq!(f.bytes("store/.fixture.lock"), b"other invocation");
}

#[test]
fn budget_exhaustion_leaves_unknown_without_output() {
    let f = Fixture::new();
    f.edit("contract.json", |c| c["read_budget"] = json!(1));
    let (code, v) = f.send();
    assert_eq!(code, 3);
    assert_eq!(v["status"], "Unknown");
    assert!(!f.root.join("envelope.json").exists());
    f.empty();
}

#[test]
fn unavailable_checker_is_unknown_without_using_the_installed_one() {
    let f = Fixture::new();
    f.edit("contract.json", |c| {
        c["checker"]["implementation_blake3"] = json!("0".repeat(64))
    });
    let (code, v) = f.send();
    assert_eq!(code, 3);
    assert_eq!(v["reason"], "required checker version unavailable");
    assert!(!f.root.join("envelope.json").exists());
    f.empty();
}

#[test]
fn stored_tampering_and_scope_inflation_are_detected() {
    for case in 0..4 {
        let f = Fixture::new();
        f.sent();
        assert_eq!(f.receive().0, 0);
        match case {
            0 => fs::write(
                f.root.join("store/fixture/materials/names/role.json"),
                b"tampered",
            )
            .unwrap(),
            1 => fs::create_dir(f.root.join("store/fixture/unexpected-empty")).unwrap(),
            2 => {
                f.edit("store/fixture/receipt.json", |r| {
                    r["native_admission"] = json!("Granted")
                });
                assert_eq!(f.ack().0, 2);
            }
            _ => {
                f.edit("contract.json", |c| c["sender"] = json!("different-source"));
                f.repin_envelope();
            }
        }
        assert_eq!(f.receive().0, 2);
        assert!(!f.root.join("store/.fixture.pending").exists());
    }
}

#[test]
fn traversal_unsupported_use_and_missing_explicit_null_are_refused() {
    for case in 0..3 {
        let f = Fixture::new();
        match case {
            0 => f.edit("contract.json", |c| {
                c["files"][0]["destination"] = json!("materials/../escape")
            }),
            1 => f.edit("contract.json", |c| c["purpose"] = json!("native-proof")),
            _ => {
                f.edit("source/catalog.json", |v| {
                    v["entries"][0].as_object_mut().unwrap().remove("checker");
                });
                let entry = &f.read("source/catalog.json")["entries"][0];
                f.edit("contract.json", |c| {
                    c["entry_blake3"] = hash(&serde_json::to_vec(entry).unwrap()).into();
                    c["origin"]["catalog_blake3"] = hash(&f.bytes("source/catalog.json")).into();
                });
            }
        }
        assert_eq!(f.send().0, 2);
        f.empty();
    }
}

#[test]
fn duplicate_json_fields_are_rejected_even_with_updated_digest() {
    for duplicate in ["\"status\":\"admitted\",", "\"nested\":{\"a\":1,\"a\":2},"] {
        let f = Fixture::new();
        let original = String::from_utf8(f.bytes("review.json")).unwrap();
        fs::write(
            f.root.join("review.json"),
            format!("{{{duplicate}{}", &original[1..]),
        )
        .unwrap();
        f.repin_review();
        assert_eq!(f.send().0, 2);
        assert!(!f.root.join("envelope.json").exists());
    }
}

#[test]
fn fresh_outputs_never_overwrite_existing_evidence() {
    let f = Fixture::new();
    f.sent();
    let before = f.bytes("envelope.json");
    assert_eq!(f.send().0, 2);
    assert_eq!(f.bytes("envelope.json"), before);
}

#[cfg(unix)]
#[test]
fn source_and_destination_symlinks_are_refused() {
    use std::os::unix::fs::symlink;
    let f = Fixture::new();
    fs::remove_file(f.root.join("source/names/role.json")).unwrap();
    fs::write(f.root.join("outside.json"), DATA).unwrap();
    symlink("../../outside.json", f.root.join("source/names/role.json")).unwrap();
    assert_eq!(f.send().0, 2);
    let f = Fixture::new();
    f.sent();
    assert_eq!(f.receive().0, 0);
    fs::remove_file(f.root.join("store/fixture/materials/names/role.json")).unwrap();
    symlink(
        f.root.join("source/names/role.json"),
        f.root.join("store/fixture/materials/names/role.json"),
    )
    .unwrap();
    assert_eq!(f.receive().0, 2);
}
