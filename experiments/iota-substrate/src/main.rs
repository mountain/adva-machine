//! Command-line entry for the research-local native Iota substrate.
//!
//! Usage:
//!
//! ```sh
//! cargo run --release -p adva-iota-substrate -- \
//!   --contract experiments/iota-substrate/contract.json \
//!   --output /tmp/iota-substrate-run-01
//! ```
//!
//! The output directory must not exist. Nothing outside it is written.

use adva_iota_substrate::{load_contract, run_contract};
use std::env;
use std::fs;
use std::path::PathBuf;
use std::process::ExitCode;

fn main() -> ExitCode {
    let mut contract: Option<PathBuf> = None;
    let mut output: Option<PathBuf> = None;
    let mut origin: Option<PathBuf> = None;
    let mut arguments = env::args().skip(1);
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--contract" => contract = arguments.next().map(PathBuf::from),
            "--output" => output = arguments.next().map(PathBuf::from),
            "--origin" => origin = arguments.next().map(PathBuf::from),
            "--help" | "-h" => {
                println!(
                    "usage: adva-iota-substrate --contract FILE --output FRESH_DIRECTORY [--origin DIR]"
                );
                return ExitCode::SUCCESS;
            }
            other => {
                eprintln!("unexpected argument {other}");
                return ExitCode::from(2);
            }
        }
    }
    let (Some(contract_path), Some(output_path)) = (contract, output) else {
        eprintln!(
            "usage: adva-iota-substrate --contract FILE --output FRESH_DIRECTORY [--origin DIR]"
        );
        return ExitCode::from(2);
    };
    if output_path.exists() {
        eprintln!("output directory {} already exists", output_path.display());
        return ExitCode::from(2);
    }
    let contract = match load_contract(&contract_path) {
        Ok(contract) => contract,
        Err(error) => {
            eprintln!("contract refused: {error}");
            return ExitCode::from(3);
        }
    };
    let origin_root = origin.unwrap_or_else(|| PathBuf::from("."));
    let report = match run_contract(&contract, &origin_root) {
        Ok(report) => report,
        Err(error) => {
            eprintln!("run refused: {error}");
            return ExitCode::from(3);
        }
    };
    if let Err(error) = fs::create_dir_all(&output_path) {
        eprintln!("output directory creation failed: {error}");
        return ExitCode::from(3);
    }
    let rendered = match serde_json::to_vec_pretty(&report) {
        Ok(rendered) => rendered,
        Err(error) => {
            eprintln!("report encoding failed: {error}");
            return ExitCode::from(3);
        }
    };
    let result_path = output_path.join("result.json");
    if let Err(error) = fs::write(&result_path, rendered) {
        eprintln!("report write failed: {error}");
        return ExitCode::from(3);
    }
    println!(
        "outcome={} families={} cases={}/{} transcript={}/{} contractions={} trace={}/{} controls={} wall={:.3}s",
        report.outcome,
        report.checked_families,
        report.cases_matched,
        report.cases.len(),
        report.transcript_rows_agreeing,
        report.transcript_rows_compared,
        report.total_contractions,
        report.trace_rows_matched,
        report.trace_rows_compared,
        report.controls.iter().filter(|c| c.passed).count(),
        report.wall_seconds
    );
    for case in &report.readings {
        println!(
            "  reading {:<22} {:<13} expected {:<20} observed {:<20} {}",
            case.label,
            case.reading,
            case.expected,
            case.observed.as_deref().unwrap_or("Unknown"),
            case.verdict
        );
    }
    for case in &report.cases {
        println!(
            "  case {:<12} {:>4} contractions  expected {:<18} observed {:<18} {}",
            case.label,
            case.contractions,
            case.expected,
            case.observed.as_deref().unwrap_or("Unknown"),
            case.verdict
        );
    }
    for family in &report.families {
        println!(
            "  {:<12} {:>6} contractions  peak {:>6}  {}",
            family.label, family.contractions, family.peak_nodes, family.verdict
        );
    }
    println!("result: {}", result_path.display());
    if report.outcome == "IotaSubstrateChecked" {
        ExitCode::SUCCESS
    } else {
        ExitCode::from(1)
    }
}
