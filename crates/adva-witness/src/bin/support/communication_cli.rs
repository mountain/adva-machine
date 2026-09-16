//! Bounded documentary exchange. No execution, proof admission or rights oracle.
//! Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy.
use serde::{
    Deserialize, Serialize,
    de::{self, MapAccess, SeqAccess, Visitor},
};
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    fmt,
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    path::{Component, Path, PathBuf},
    time::Instant,
};

const PROFILE: &str = "documentary-library-entry-v1";
const MAX_META: u64 = 262_144;
const MAX_ENVELOPE: u64 = 2_097_152;
const MAX_READ: u64 = 8_388_608;
const MAX_FILE: u64 = 65_536;

#[derive(Debug)]
struct Failure {
    status: &'static str,
    reason: String,
}
type Result<T> = std::result::Result<T, Failure>;
fn fail(status: &'static str, why: impl ToString) -> Failure {
    Failure {
        status,
        reason: why.to_string(),
    }
}
fn require(ok: bool, why: &str) -> Result<()> {
    if ok {
        Ok(())
    } else {
        Err(fail("Rejected", why))
    }
}
impl From<std::io::Error> for Failure {
    fn from(e: std::io::Error) -> Self {
        fail("Unknown", e)
    }
}
impl From<serde_json::Error> for Failure {
    fn from(e: serde_json::Error) -> Self {
        fail("Rejected", e)
    }
}

// Reject duplicate object fields at every depth, including opaque catalog prose.
struct Strict(Value);
impl<'de> Deserialize<'de> for Strict {
    fn deserialize<D: de::Deserializer<'de>>(d: D) -> std::result::Result<Self, D::Error> {
        struct V;
        impl<'de> Visitor<'de> for V {
            type Value = Strict;
            fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
                f.write_str("unambiguous JSON")
            }
            fn visit_bool<E: de::Error>(self, v: bool) -> std::result::Result<Strict, E> {
                Ok(Strict(v.into()))
            }
            fn visit_i64<E: de::Error>(self, v: i64) -> std::result::Result<Strict, E> {
                Ok(Strict(v.into()))
            }
            fn visit_u64<E: de::Error>(self, v: u64) -> std::result::Result<Strict, E> {
                Ok(Strict(v.into()))
            }
            fn visit_f64<E: de::Error>(self, _: f64) -> std::result::Result<Strict, E> {
                Err(E::custom("floating point is outside this profile"))
            }
            fn visit_str<E: de::Error>(self, v: &str) -> std::result::Result<Strict, E> {
                Ok(Strict(v.into()))
            }
            fn visit_unit<E: de::Error>(self) -> std::result::Result<Strict, E> {
                Ok(Strict(Value::Null))
            }
            fn visit_seq<A: SeqAccess<'de>>(
                self,
                mut a: A,
            ) -> std::result::Result<Strict, A::Error> {
                let mut v = Vec::new();
                while let Some(Strict(x)) = a.next_element()? {
                    v.push(x);
                }
                Ok(Strict(Value::Array(v)))
            }
            fn visit_map<A: MapAccess<'de>>(
                self,
                mut a: A,
            ) -> std::result::Result<Strict, A::Error> {
                let mut v = serde_json::Map::new();
                while let Some((k, Strict(x))) = a.next_entry::<String, Strict>()? {
                    if v.insert(k, x).is_some() {
                        return Err(de::Error::custom("duplicate JSON field"));
                    }
                }
                Ok(Strict(Value::Object(v)))
            }
        }
        d.deserialize_any(V)
    }
}
fn parse(raw: &[u8]) -> Result<Value> {
    Ok(serde_json::from_slice::<Strict>(raw)?.0)
}
fn hash(raw: &[u8]) -> String {
    blake3::hash(raw).to_hex().to_string()
}
fn hex(s: &str, n: usize) -> bool {
    s.len() == n
        && s.bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}
fn identifier(s: &str) -> bool {
    !s.is_empty()
        && s.len() <= 96
        && s.bytes()
            .all(|b| b.is_ascii_alphanumeric() || b"-_".contains(&b))
}
fn relative(s: &str) -> Result<()> {
    require(
        !s.is_empty()
            && s.len() <= 200
            && s.split('/').count() <= 8
            && s.split('/').all(|c| {
                !c.is_empty()
                    && c != "."
                    && c != ".."
                    && c.bytes()
                        .all(|b| b.is_ascii_alphanumeric() || b"._-".contains(&b))
            }),
        "noncanonical relative path",
    )
}
fn plain_path(p: &Path) -> Result<()> {
    let mut current = PathBuf::new();
    for c in p.components() {
        require(
            !matches!(c, Component::ParentDir),
            "parent path component refused",
        )?;
        current.push(c);
        if let Ok(meta) = fs::symlink_metadata(&current) {
            require(!meta.file_type().is_symlink(), "symbolic link refused")?;
        }
    }
    Ok(())
}
struct Account {
    start: Instant,
    bytes: u64,
    limit: u64,
    events: Vec<&'static str>,
}
impl Account {
    fn tick(&self) -> Result<()> {
        if self.bytes > self.limit || self.start.elapsed().as_secs_f64() > 5.0 {
            Err(fail("Unknown", "finite invocation budget exhausted"))
        } else {
            Ok(())
        }
    }
    fn read(&mut self, p: &Path, max: u64) -> Result<Vec<u8>> {
        self.tick()?;
        plain_path(p)?;
        require(fs::symlink_metadata(p)?.is_file(), "regular file required")?;
        let remaining = self.limit.saturating_sub(self.bytes);
        let mut raw = Vec::new();
        File::open(p)?
            .take(max.min(remaining) + 1)
            .read_to_end(&mut raw)?;
        self.bytes += raw.len() as u64;
        self.tick()?;
        require(raw.len() as u64 <= max, "individual file limit exceeded")?;
        Ok(raw)
    }
}
#[derive(Debug, Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
struct Member {
    source: String,
    destination: String,
    bytes: u64,
    blake3: String,
    sha256: String,
}
#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct Origin {
    repository: String,
    revision: String,
    catalog_path: String,
    catalog_blake3: String,
}
#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct Contract {
    schema: String,
    profile: String,
    exchange_id: String,
    sender: String,
    receiver: String,
    context: String,
    purpose: String,
    origin: Origin,
    entry_key: String,
    home: String,
    entry_blake3: String,
    publication_record_blake3: String,
    files: Vec<Member>,
    read_budget: u64,
    dependency_policy: String,
    checker: Checker,
}
#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct Checker {
    implementation_blake3: String,
    cargo_lock_blake3: String,
}
#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct Payload {
    source: String,
    bytes: Vec<u8>,
}
#[derive(Debug, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
struct Envelope {
    schema: String,
    contract_blake3: String,
    entry: Value,
    payloads: Vec<Payload>,
}

fn contract(raw: &[u8], expected: &str) -> Result<Contract> {
    require(
        hex(expected, 64) && hash(raw) == expected,
        "receiver contract pin mismatch",
    )?;
    let c: Contract = serde_json::from_value(parse(raw)?)?;
    require(
        c.schema == "adva.communication.contract.v1" && c.profile == PROFILE,
        "unsupported communication profile",
    )?;
    if c.checker.implementation_blake3 != hash(include_bytes!("communication_cli.rs"))
        || c.checker.cargo_lock_blake3
            != hash(include_bytes!(concat!(
                env!("CARGO_MANIFEST_DIR"),
                "/../../Cargo.lock"
            )))
    {
        return Err(fail("Unknown", "required checker version unavailable"));
    }
    require(
        identifier(&c.exchange_id) && identifier(&c.entry_key),
        "invalid exchange or entry identity",
    )?;
    require(
        !c.sender.is_empty() && !c.receiver.is_empty() && !c.context.is_empty(),
        "missing interface context",
    )?;
    require(
        c.purpose == "documentary-reference" && c.home == "logic",
        "unsupported use or home",
    )?;
    require(
        c.dependency_policy == "retain-references-no-execution",
        "unsupported dependency policy",
    )?;
    require(
        c.origin.repository.starts_with("https://github.com/") && hex(&c.origin.revision, 40),
        "origin coordinates required",
    )?;
    relative(&c.origin.catalog_path)?;
    require(
        [
            &c.origin.catalog_blake3,
            &c.entry_blake3,
            &c.publication_record_blake3,
        ]
        .iter()
        .all(|h| hex(h, 64)),
        "invalid digest",
    )?;
    require(
        !c.files.is_empty() && c.files.len() <= 8 && c.read_budget <= MAX_READ,
        "profile bounds exceeded",
    )?;
    let mut sources = BTreeSet::new();
    let mut dests = BTreeSet::new();
    let mut total = 0;
    for f in &c.files {
        relative(&f.source)?;
        relative(&f.destination)?;
        require(
            f.destination.starts_with("materials/")
                && sources.insert(&f.source)
                && dests.insert(&f.destination),
            "duplicate or reserved destination",
        )?;
        require(
            f.bytes <= MAX_FILE && hex(&f.blake3, 64) && hex(&f.sha256, 64),
            "invalid member pin",
        )?;
        total += f.bytes;
    }
    require(total <= 262_144, "payload byte bound exceeded")?;
    for a in &dests {
        for b in &dests {
            require(
                a == b || !b.starts_with(&format!("{a}/")),
                "overlapping destinations",
            )?;
        }
    }
    Ok(c)
}
fn publication(raw: &[u8], c: &Contract) -> Result<()> {
    require(
        hash(raw) == c.publication_record_blake3,
        "publication record pin mismatch",
    )?;
    let p = parse(raw)?;
    require(
        p["schema"] == "adva.publication-admission.v1" && p["status"] == "admitted",
        "publication review not admitted",
    )?;
    require(
        p["eligible_basis"] == "project-original",
        "this profile only supports reviewed project-original material",
    )?;
    for pointer in [
        "/resource_id",
        "/provenance/source_url",
        "/provenance/source_version",
        "/provenance/creator_or_rights_holder",
        "/provenance/rights_holder_authority_evidence",
        "/provenance/jurisdictions_and_limitations",
        "/review/reviewer",
        "/review/reviewed_at",
        "/review/decision_reason",
    ] {
        require(
            p.pointer(pointer)
                .and_then(Value::as_str)
                .is_some_and(|s| !s.trim().is_empty()),
            "incomplete publication record",
        )?;
    }
    require(
        p["review"]["all_components_reviewed"] == true
            && p["review"]["output_publication_reviewed"] == true
            && p["review"]["unresolved_questions"] == json!([]),
        "unresolved publication review",
    )?;
    require(
        p["provenance"]["source_version"] == c.origin.revision
            && p["provenance"]["publication_basis_evidence_urls"]
                .as_array()
                .is_some_and(|a| {
                    !a.is_empty()
                        && a.iter()
                            .all(|v| v.as_str().is_some_and(|s| !s.trim().is_empty()))
                })
            && p["provenance"]["incorporated_components"].is_array()
            && p["provenance"]["transformations"].is_array(),
        "incomplete provenance",
    )?;
    let files = p["files"]
        .as_array()
        .ok_or_else(|| fail("Rejected", "missing reviewed files"))?;
    require(
        files.len() == c.files.len(),
        "publication file coverage mismatch",
    )?;
    for (p, f) in files.iter().zip(&c.files) {
        require(
            p["path"] == format!("knowledge/received/{}/{}", c.exchange_id, f.destination)
                && p["bytes"] == f.bytes
                && p["sha256"] == f.sha256
                && p["blake3"] == f.blake3,
            "publication payload binding mismatch",
        )?;
    }
    Ok(())
}
fn catalog_entry(v: &Value, c: &Contract) -> Result<()> {
    require(
        hash(&serde_json::to_vec(v)?) == c.entry_blake3,
        "catalog entry pin mismatch",
    )?;
    for field in ["title", "scope"] {
        require(
            v[field].as_str().is_some_and(|s| !s.trim().is_empty()),
            "incomplete catalog prose",
        )?;
    }
    require(
        v.get("checker").is_some()
            && v.get("geometry_lineage").is_some()
            && v["theory"].is_object()
            && v["domains"]
                .as_array()
                .is_some_and(|a| a.contains(&json!(c.home))),
        "incomplete catalog structure",
    )?;
    require(
        v["key"] == c.entry_key
            && v["home"] == c.home
            && v["recorded_status"] == "proposed-document"
            && v["checker"].is_null()
            && v["geometry_lineage"].is_null()
            && v["evidence"] == json!([]),
        "unsupported catalog judgment",
    )?;
    require(
        v["assumptions"].is_array()
            && v["open_obligations"].is_array()
            && v["reuse_requires"].is_array(),
        "missing retained obligations",
    )?;
    let materials = v["materials"]
        .as_array()
        .ok_or_else(|| fail("Rejected", "missing materials"))?;
    require(
        materials.len() == c.files.len(),
        "catalog material coverage mismatch",
    )?;
    for (m, f) in materials.iter().zip(&c.files) {
        require(
            m["path"] == format!("adva-library/{}", f.source) && m["sha256"] == f.sha256,
            "catalog source mismatch",
        )?;
    }
    Ok(())
}
fn payload(raw: &[u8], f: &Member) -> Result<()> {
    require(
        raw.len() as u64 == f.bytes && hash(raw) == f.blake3,
        "payload bytes differ from reviewed contract",
    )?;
    require(
        std::str::from_utf8(raw).is_ok(),
        "only UTF-8 documentary materials are supported",
    )
}
fn envelope(raw: &[u8], pin: &str, c: &Contract) -> Result<Envelope> {
    let e: Envelope = serde_json::from_value(parse(raw)?)?;
    require(
        e.schema == "adva.communication.envelope.v1" && e.contract_blake3 == pin,
        "envelope contract mismatch",
    )?;
    catalog_entry(&e.entry, c)?;
    require(
        e.payloads.len() == c.files.len(),
        "envelope file coverage mismatch",
    )?;
    for (p, f) in e.payloads.iter().zip(&c.files) {
        require(p.source == f.source, "envelope source order mismatch")?;
        payload(&p.bytes, f)?;
    }
    Ok(e)
}
fn sync_dir(p: &Path) -> Result<()> {
    File::open(p)?.sync_all()?;
    Ok(())
}
fn fresh(p: &Path, raw: &[u8]) -> Result<()> {
    plain_path(p)?;
    require(!p.try_exists()?, "output already exists")?;
    let mut f = OpenOptions::new().write(true).create_new(true).open(p)?;
    f.write_all(raw)?;
    f.sync_all()?;
    sync_dir(
        p.parent()
            .filter(|p| !p.as_os_str().is_empty())
            .unwrap_or(Path::new(".")),
    )
}
fn receipt(c: &Contract, pin: &str, e: &Envelope, raw: &[u8]) -> Value {
    json!({"schema":"adva.communication.receipt.v1","profile":PROFILE,"status":"AcceptedDocumentary",
        "contract_blake3":pin,"envelope_blake3":hash(raw),"exchange_id":c.exchange_id,
        "sender":c.sender,"receiver":c.receiver,"context":c.context,"accepted_use":c.purpose,
        "origin":c.origin,"publication_record_blake3":c.publication_record_blake3,
        "checker":c.checker,"resource_contract":{"read_bytes_per_invocation":c.read_budget,"cooperative_seconds":5,"automatic_retries":0},
        "publication":"BoundReviewedRecord","rights_determined_by_machine":false,
        "catalog_entry":e.entry,"files":c.files,"semantic_verification":"NotRun","native_admission":"NotGranted",
        "events":["receive","check-integrity-and-contract","accept-documentary-reference"],
        "residual":"Origin claims are pinned, not authenticated; referenced proofs and human acceptance are not checked. No source retirement or new catalog home."})
}
fn inspect_tree(p: &Path, prefix: &str, found: &mut BTreeSet<String>, a: &Account) -> Result<()> {
    plain_path(p)?;
    for child in fs::read_dir(p)? {
        a.tick()?;
        require(found.len() < 64, "destination inventory bound exceeded")?;
        let child = child?;
        let name = child
            .file_name()
            .into_string()
            .map_err(|_| fail("Rejected", "invalid filename"))?;
        let name = format!("{prefix}{name}");
        relative(&name)?;
        require(
            !child.file_type()?.is_symlink(),
            "destination symlink refused",
        )?;
        if child.file_type()?.is_dir() {
            let prefix = format!("{name}/");
            found.insert(prefix.clone());
            inspect_tree(&child.path(), &prefix, found, a)?;
        } else {
            require(child.file_type()?.is_file(), "nonregular destination")?;
            found.insert(name);
        }
    }
    Ok(())
}
fn verify_stored(dir: &Path, expected: &Value, c: &Contract, a: &mut Account) -> Result<()> {
    let r = a.read(&dir.join("receipt.json"), MAX_META)?;
    require(
        r == serde_json::to_vec_pretty(expected)?,
        "existing exchange identity has a different receipt",
    )?;
    let mut inventory = BTreeSet::new();
    inspect_tree(dir, "", &mut inventory, a)?;
    let mut want: BTreeSet<String> = c
        .files
        .iter()
        .map(|f| f.destination.clone())
        .chain(["receipt.json".into()])
        .collect();
    for f in &c.files {
        let mut parent = Path::new(&f.destination).parent();
        while let Some(p) = parent.filter(|p| !p.as_os_str().is_empty()) {
            want.insert(format!("{}/", p.display()));
            parent = p.parent();
        }
    }
    require(inventory == want, "destination inventory differs")?;
    for f in &c.files {
        payload(&a.read(&dir.join(&f.destination), MAX_FILE)?, f)?;
    }
    sync_dir(dir)?;
    Ok(())
}
fn receive(
    store: &Path,
    expected: &Value,
    e: &Envelope,
    c: &Contract,
    a: &mut Account,
) -> Result<Value> {
    plain_path(store)?;
    require(store.is_dir(), "receiver store must already exist")?;
    let lock = store.join(format!(".{}.lock", c.exchange_id));
    let _guard = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&lock)?;
    let outcome = (|| {
        let dest = store.join(&c.exchange_id);
        if dest.try_exists()? {
            verify_stored(&dest, expected, c, a)?;
            a.events.push("prior-acceptance-rechecked");
            return Ok(
                json!({"status":"AlreadyAccepted","acceptance_effects":0,"receipt_blake3":hash(&serde_json::to_vec_pretty(expected)?)}),
            );
        }
        a.tick()?;
        let stage = store.join(format!(".{}.pending", c.exchange_id));
        fs::create_dir(&stage)?; // Retain any partial stage; never reset it automatically.
        a.events.push("record-staging-started");
        for (p, f) in e.payloads.iter().zip(&c.files) {
            a.tick()?;
            let target = stage.join(&f.destination);
            let parent = target.parent().unwrap();
            fs::create_dir_all(parent)?;
            fresh(&target, &p.bytes)?;
            let mut path = parent.to_path_buf();
            while path != stage {
                sync_dir(&path)?;
                path.pop();
            }
        }
        fresh(
            &stage.join("receipt.json"),
            &serde_json::to_vec_pretty(expected)?,
        )?;
        verify_stored(&stage, expected, c, a)?;
        a.tick()?;
        fs::rename(&stage, &dest)?;
        sync_dir(store)?;
        a.events.push("accept-documentary-reference");
        Ok(
            json!({"status":"AcceptedDocumentary","acceptance_effects":1,"receipt_blake3":hash(&serde_json::to_vec_pretty(expected)?)}),
        )
    })();
    fs::remove_file(lock)?;
    sync_dir(store)?;
    outcome
}

fn invoke(args: impl Iterator<Item = String>, a: &mut Account) -> Result<Value> {
    let mut args = args;
    let action = args
        .next()
        .ok_or_else(|| fail("Rejected", "missing communicate action"))?;
    let allowed = match action.as_str() {
        "send" => vec!["--source", "--publication-record", "--output"],
        "receive" => vec![
            "--envelope",
            "--publication-record",
            "--store",
            "--receiver",
            "--context",
        ],
        "acknowledge" => vec![
            "--envelope",
            "--publication-record",
            "--receipt",
            "--output",
        ],
        _ => {
            return Err(fail(
                "Rejected",
                "action must be send, receive or acknowledge",
            ));
        }
    };
    let mut opts = BTreeMap::new();
    while let Some(k) = args.next() {
        require(
            k == "--contract"
                || k == "--expect-contract"
                || k == "--attempt"
                || allowed.contains(&k.as_str()),
            "unknown communicate option",
        )?;
        let v = args
            .next()
            .ok_or_else(|| fail("Rejected", "missing option value"))?;
        require(opts.insert(k, v).is_none(), "duplicate communicate option")?;
    }
    let get = |k: &str| {
        opts.get(k)
            .map(String::as_str)
            .ok_or_else(|| fail("Rejected", format!("missing {k}")))
    };
    for k in &allowed {
        get(k)?;
    }
    require(identifier(get("--attempt")?), "invalid attempt coordinate")?;
    let pin = get("--expect-contract")?;
    let c = contract(&a.read(Path::new(get("--contract")?), MAX_META)?, pin)?;
    a.events.push("contract-bound");
    a.limit = c.read_budget;
    a.tick()?;
    publication(
        &a.read(Path::new(get("--publication-record")?), MAX_META)?,
        &c,
    )?;
    a.events.push("publication-record-bound");
    if action == "send" {
        let root = Path::new(get("--source")?);
        let catalog = a.read(&root.join(&c.origin.catalog_path), MAX_META)?;
        require(
            hash(&catalog) == c.origin.catalog_blake3,
            "source catalog pin mismatch",
        )?;
        let catalog = parse(&catalog)?;
        let entries = catalog["entries"]
            .as_array()
            .ok_or_else(|| fail("Rejected", "missing source entries"))?;
        let matches: Vec<_> = entries.iter().filter(|v| v["key"] == c.entry_key).collect();
        require(matches.len() == 1, "source key must be unique")?;
        catalog_entry(matches[0], &c)?;
        let mut payloads = Vec::new();
        for f in &c.files {
            let bytes = a.read(&root.join(&f.source), MAX_FILE)?;
            payload(&bytes, f)?;
            payloads.push(Payload {
                source: f.source.clone(),
                bytes,
            });
        }
        let e = Envelope {
            schema: "adva.communication.envelope.v1".into(),
            contract_blake3: pin.into(),
            entry: matches[0].clone(),
            payloads,
        };
        let raw = serde_json::to_vec(&e)?;
        require(raw.len() as u64 <= MAX_ENVELOPE, "envelope limit exceeded")?;
        a.tick()?;
        fresh(Path::new(get("--output")?), &raw)?;
        a.events.push("send");
        return Ok(
            json!({"status":"Sent","exchange_id":c.exchange_id,"contract_blake3":pin,"envelope_blake3":hash(&raw),"receiver_observation":"Unknown"}),
        );
    }
    if action == "receive" {
        require(
            get("--receiver")? == c.receiver && get("--context")? == c.context,
            "receiver interface/context mismatch",
        )?;
    }
    let raw = a.read(Path::new(get("--envelope")?), MAX_ENVELOPE)?;
    a.events.push(if action == "receive" {
        "receive"
    } else {
        "sent-presentation-read"
    });
    let e = envelope(&raw, pin, &c)?;
    a.events.push("check-integrity-and-contract");
    let expected = receipt(&c, pin, &e, &raw);
    if action == "receive" {
        return receive(Path::new(get("--store")?), &expected, &e, &c, a);
    }
    let observed = a.read(Path::new(get("--receipt")?), MAX_META)?;
    a.events.push("reply-observed");
    require(
        observed == serde_json::to_vec_pretty(&expected)?,
        "reply does not match this exchange",
    )?;
    let ack = json!({"schema":"adva.communication.acknowledgment.v1","status":"Acknowledged",
        "exchange_id":c.exchange_id,"contract_blake3":pin,"envelope_blake3":hash(&raw),
        "receipt_blake3":hash(&serde_json::to_vec_pretty(&expected)?),"observed_receiver_status":expected["status"],
        "semantic_verification":"NotRun","native_admission":"NotGranted","new_acceptance_effects":0});
    a.tick()?;
    fresh(
        Path::new(get("--output")?),
        &serde_json::to_vec_pretty(&ack)?,
    )?;
    a.events.push("acknowledge");
    Ok(ack)
}
pub(super) fn entry(args: impl Iterator<Item = String>) -> ! {
    let args: Vec<_> = args.collect();
    let action = args.first().cloned();
    let attempt = args
        .windows(2)
        .find(|a| a[0] == "--attempt")
        .map(|a| a[1].clone());
    let contract_pin = args
        .windows(2)
        .find(|a| a[0] == "--expect-contract")
        .map(|a| a[1].clone());
    let mut a = Account {
        start: Instant::now(),
        bytes: 0,
        limit: MAX_READ,
        events: Vec::new(),
    };
    let (mut result, exit) = match invoke(args.into_iter(), &mut a) {
        Ok(v) => (v, 0),
        Err(e) => {
            let exit = if e.status == "Unknown" { 3 } else { 2 };
            (
                json!({"status":e.status,"reason":e.reason,"acceptance_effects":"NotAsserted","automatic_retry":false}),
                exit,
            )
        }
    };
    result["action"] = json!(action);
    result["attempt"] = json!(attempt);
    result["supplied_contract_blake3"] = json!(contract_pin);
    result["observed_events"] = json!(a.events);
    result["profile"] = json!(PROFILE);
    result["bytes_read"] = json!(a.bytes);
    result["wall_seconds"] = json!(a.start.elapsed().as_secs_f64());
    println!(
        "{}",
        serde_json::to_string(&result).expect("serializable communication report")
    );
    std::process::exit(exit)
}
