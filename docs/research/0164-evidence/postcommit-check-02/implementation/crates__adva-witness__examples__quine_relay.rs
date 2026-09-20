//! Research byte-output adapter. The existing Rust kernel owns every judgment.
use adva_ir::{ProgramTerm, ValueType};
use adva_lisp::{compile_function, evaluate, link_modules, parse_module};
use adva_witness::{ExactExprV0, LibraryBudgetV0, load_library_v0, reuse_library_word_v0};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::error::Error;
use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::path::Path;

const MAX_SOURCE: usize = 1_048_576;
const MAX_BYTES: usize = 16_384;
const MAX_REPORT: usize = 67_108_864;

fn fresh(path: &str, bytes: &[u8]) -> Result<(), Box<dyn Error>> {
    if bytes.len() > MAX_REPORT {
        return Err("report byte cap".into());
    }
    let mut file = OpenOptions::new().write(true).create_new(true).open(path)?;
    file.write_all(bytes)?;
    file.sync_all()?;
    Ok(())
}

fn inspect_term(term: &ProgramTerm, depth: usize, count: &mut usize) -> Result<(), Box<dyn Error>> {
    *count += 1;
    if depth > 16 || *count > 100_000 {
        return Err("research AST admission cap".into());
    }
    match term {
        ProgramTerm::Constant { .. } => Ok(()),
        ProgramTerm::Frontier { terms } => {
            for child in terms {
                inspect_term(child, depth + 1, count)?;
            }
            Ok(())
        }
        ProgramTerm::Apply {
            operation,
            arguments,
        } if ["add", "copy", "scale"].contains(&operation.name.as_str()) => {
            for child in arguments {
                inspect_term(child, depth + 1, count)?;
            }
            Ok(())
        }
        _ => Err("outside the closed research emission profile".into()),
    }
}

fn emit(source: &str, output: &str) -> Result<Value, Box<dyn Error>> {
    let mut raw = Vec::new();
    File::open(source)?
        .take((MAX_SOURCE + 1) as u64)
        .read_to_end(&mut raw)?;
    if raw.len() > MAX_SOURCE || !raw.is_ascii() {
        return Err("ASCII source byte cap".into());
    }
    // This is an output convention, not another Lisp evaluator or parser.
    let parsed = parse_module(std::str::from_utf8(&raw)?)?;
    if parsed.module.name.0 != "relay"
        || !parsed.module.imports.is_empty()
        || parsed.module.definitions.len() != 1
    {
        return Err("one closed relay module required".into());
    }
    let definition = &parsed.module.definitions[0];
    if definition.name.0 != "main"
        || !definition.signature.inputs.is_empty()
        || definition.signature.outputs.is_empty()
        || definition.signature.outputs.len() > MAX_BYTES
        || definition
            .signature
            .outputs
            .iter()
            .any(|t| *t != ValueType::Real)
    {
        return Err("closed nonempty Real byte frontier required".into());
    }
    let mut terms = 0;
    inspect_term(&definition.body, 0, &mut terms)?;
    let linked = link_modules(vec![parsed])?;
    let compilation = compile_function(&linked, "relay", "main")?;
    let evaluation = evaluate(&compilation.result, &BTreeMap::new())?;
    let mut bytes = Vec::with_capacity(evaluation.values.len());
    for value in &evaluation.values {
        if !value.is_finite() || value.fract() != 0.0 || !(0.0..=255.0).contains(value) {
            return Err("byte observation requires finite integers in 0..255".into());
        }
        bytes.push(*value as u8);
    }
    let report = json!({
        "schema": "adva.quine-byte-observation.research.v0", "status": "ByteFrontierEvaluated",
        "source_blake3": blake3::hash(&raw).to_hex().to_string(), "source_bytes": raw.len(),
        "output_blake3": blake3::hash(&bytes).to_hex().to_string(), "output_bytes": bytes.len(),
        "ast_terms": terms, "compiled_nodes": compilation.result.nodes.len(),
        "source_count": compilation.result.source_partition().len(),
        "compilation": compilation, "evaluation": evaluation,
        "scope": "integer-valued byte observation of this finite PSC0 result; no source identity quotient"
    });
    fresh(output, &bytes)?;
    Ok(report)
}

fn libraries(internal: &str, external: &str) -> Result<Value, Box<dyn Error>> {
    let mut budget = LibraryBudgetV0::new(50_000)?;
    budget.charge()?; // Report/checkpoint work belongs to the same finite account.
    let mut readings = Vec::new();
    for (role, directory) in [
        ("embedded-pinned", internal),
        ("standalone-named", external),
    ] {
        let loaded = load_library_v0(&Path::new(directory).join("stability"), 1, &mut budget)?;
        let word = loaded
            .snapshot()
            .words
            .first()
            .ok_or("missing library word")?;
        let x = ExactExprV0::variable("x");
        let before = ExactExprV0::product(ExactExprV0::constant(2), x.clone());
        let after = ExactExprV0::sum(x.clone(), x);
        let catalogue = &loaded.snapshot().input.catalogue;
        if catalogue.get(word.left) != Some(&before) || catalogue.get(word.right) != Some(&after) {
            return Err("the frozen doubling word differs".into());
        }
        let mut reuses = Vec::new();
        for input in 1..=8 {
            let reuse = reuse_library_word_v0(&loaded, 0, input, &mut budget)?;
            if reuse.guarded_values != [format!("{}", 2 * input), format!("{}", 2 * input)] {
                return Err("unexpected guarded doubling".into());
            }
            reuses.push(reuse);
        }
        let zero_error = reuse_library_word_v0(&loaded, 0, 0, &mut budget)
            .expect_err("zero must not pass the retained nonzero guard")
            .to_string();
        readings.push(
            json!({"role": role, "path": directory, "digest": loaded.digest(),
            "word": word, "reuses": reuses, "zero_refusal": zero_error}),
        );
    }
    if readings[0]["digest"] != readings[1]["digest"] || readings[0]["word"] != readings[1]["word"]
    {
        return Err("library snapshots differ".into());
    }
    Ok(
        json!({"schema": "adva.quine-library-reading.research.v0", "status": "BothSnapshotsRechecked",
        "readings": readings, "fuel": budget, "same_snapshot_content": true,
        "contexts_identified": false, "native_programs_identified": false}),
    )
}

fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 4 || !["emit", "libraries"].contains(&args[0].as_str()) {
        return Err("usage: quine_relay emit SOURCE NEW-OUTPUT NEW-REPORT | libraries INTERNAL EXTERNAL NEW-REPORT".into());
    }
    if Path::new(&args[3]).exists() {
        return Err("report already exists".into());
    }
    let result = if args[0] == "emit" {
        emit(&args[1], &args[2])
    } else {
        libraries(&args[1], &args[2])
    };
    match result {
        Ok(report) => fresh(&args[3], &serde_json::to_vec(&report)?),
        Err(error) => {
            fresh(
                &args[3],
                &serde_json::to_vec(&json!({"status": "Rejected", "error": error.to_string()}))?,
            )?;
            Err(error)
        }
    }
}
