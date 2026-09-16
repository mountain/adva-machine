use adva_witness::{
    AdvaDocumentV0, CLOSURE_TRANSPORT_CONTRACT_SCHEMA_V0, HYPOTHESIS_FORMATION_CONTRACT_SCHEMA_V0,
    M6NamingPlanV0, MAGIC_SQUARE_SEARCH_CONTRACT_SCHEMA_V0, PROBLEM_FORMATION_CONTRACT_SCHEMA_V0,
    VALUE_SEEKING_CONTRACT_SCHEMA_V0, calibrate_trace_arithmetic_v0,
    derive_inquiry_frontier_from_file_v0, learn_hypothesis_v0, load_closure_transport_contract_v0,
    load_closure_transport_plan_v0, load_exploration_contract_v0,
    load_hypothesis_formation_contract_v0, load_hypothesis_formation_frontier_v0,
    load_hypothesis_formation_resource_v0, load_imagination_resource_v0, load_inquiry_frontier_v0,
    load_local_closure_candidate_v0, load_magic_square_frontier_v0, load_magic_square_resource_v0,
    load_magic_square_search_contract_v0, load_problem_awareness_v0,
    load_problem_formation_contract_v0, load_problem_value_frontier_v0, load_resource_snapshot_v0,
    load_reveal_witness_v0, load_value_seeking_contract_v0, load_value_seeking_resource_v0,
    load_verification_contract_v0, load_verification_packet_v0, load_verification_subject_v0,
    run_closure_transport_v0, run_hypothesis_formation_v0, run_m6_reveal_v0,
    run_magic_square_search_v0, run_problem_formation_v0, run_value_seeking_v0,
    save_closure_transport_frontier_v0, save_closure_transport_transition_v0,
    save_hypothesis_formation_frontier_v0, save_hypothesis_formation_transition_v0,
    save_hypothesis_transition_v0, save_inquiry_frontier_v0, save_magic_square_frontier_v0,
    save_magic_square_transition_v0, save_problem_formation_transition_v0,
    save_problem_value_frontier_v0, save_reveal_witness_v0, save_trace_arithmetic_v0,
    save_value_seeking_transition_v0, save_verification_frontier_v0,
    save_verification_transition_v0, verify_obligations_v0,
};
use std::env;
use std::error::Error;
use std::fs;
use std::io::{self, ErrorKind};
use std::path::PathBuf;

#[path = "support/native_run_cli.rs"]
mod native_run_cli;

#[path = "support/data_machine_cli.rs"]
mod data_machine_cli;
#[path = "support/data_machine_v1_cli.rs"]
mod data_machine_v1_cli;
#[path = "support/data_machine_v2_cli.rs"]
mod data_machine_v2_cli;

#[path = "support/library_cli.rs"]
mod library_cli;

#[path = "support/communication_cli.rs"]
mod communication_cli;

const USAGE: &str = "usage:
  adva communicate <send|receive|acknowledge> --contract <json> --expect-contract <BLAKE3> [profile options]
  adva library check --path <library-root> --epoch N --output <new-report.json> [--fuel N] [--expect-digest BLAKE3]
  adva library reuse --path <library-root> --epoch N --word N --input N --output <new-report.json> [--fuel N] [--expect-digest BLAKE3]
  adva run <program.adva> --output <result.adva> [--print]
  adva data-run-v1 <program.adva> --input <data.json> --fuel N --quantum N --output <new-run.adva> [--resume <old-run.adva> | --check <old-run.adva>]
  adva data-run-v2 <program.adva> --input <data.json> --fuel N --quantum N --output <new-run.adva> [--resume <old-run.adva> | --check <old-run.adva>]
  adva data-run <program.adva> --input <data.json> --fuel N --quantum N --output <new-run.adva> [--resume <old-run.adva> | --check <old-run.adva>]
  adva reveal <program.adva> --output <witness.adva> [--fuel N] [--print]
  adva trace-arithmetic <reveal-witness.adva> --output <calibration.adva> [--print]
  adva frontier <calibration.adva> --output <frontier.adva> [--print]
  adva learn <subject.adva> <method.adva> <object.adva> --output <transition.adva> --frontier-output <next-frontier.adva> [--print]
  adva verify <subject.adva> <method.adva> <object.adva> --output <transition.adva> --frontier-output <next-frontier.adva> [--print]";

#[derive(Debug)]
struct RevealArgs {
    program: PathBuf,
    output: PathBuf,
    fuel: u64,
    print: bool,
}

#[derive(Debug)]
struct TraceArithmeticArgs {
    witness: PathBuf,
    output: PathBuf,
    print: bool,
}

#[derive(Debug)]
struct FrontierArgs {
    calibration: PathBuf,
    output: PathBuf,
    print: bool,
}

#[derive(Debug)]
struct LearnArgs {
    frontier: PathBuf,
    contract: PathBuf,
    resource: PathBuf,
    output: PathBuf,
    frontier_output: PathBuf,
    print: bool,
}

#[derive(Debug)]
struct VerifyArgs {
    frontier: PathBuf,
    contract: PathBuf,
    packet: PathBuf,
    output: PathBuf,
    frontier_output: PathBuf,
    print: bool,
}

fn main() {
    if let Err(error) = run() {
        eprintln!("adva: {error}");
        eprintln!("{USAGE}");
        std::process::exit(2);
    }
}

fn run() -> Result<(), Box<dyn Error>> {
    let mut arguments = env::args().skip(1);
    let command = arguments
        .next()
        .ok_or_else(|| invalid_input("missing command"))?;
    match command.as_str() {
        "communicate" => communication_cli::entry(arguments),
        "library" => library_cli::run(arguments),
        "run" => native_run_cli::run(arguments),
        "data-run-v1" => data_machine_v1_cli::run(arguments),
        "data-run-v2" => data_machine_v2_cli::run(arguments),
        "data-run" => data_machine_cli::run(arguments),
        "reveal" => run_reveal(parse_reveal_args(arguments)?),
        "trace-arithmetic" => run_trace_arithmetic(parse_trace_arithmetic_args(arguments)?),
        "frontier" => run_frontier(parse_frontier_args(arguments)?),
        "learn" => run_learn(parse_learn_args(arguments)?),
        "verify" => run_verify(parse_verify_args(arguments)?),
        _ => Err(invalid_input(format!("unknown command {command:?}")).into()),
    }
}

fn run_frontier(parsed: FrontierArgs) -> Result<(), Box<dyn Error>> {
    let frontier = derive_inquiry_frontier_from_file_v0(&parsed.calibration)?;
    let receipt = save_inquiry_frontier_v0(&parsed.output, &frontier)?;

    println!("sequence={}", frontier.lineage.sequence);
    println!("obligations={}", frontier.obligations.len());
    println!("pause={:?}", frontier.pause_reason);
    println!("source={}", frontier.source_calibration_digest);
    println!("frontier={}", receipt.artifact_digest);
    println!("output={}", receipt.path.display());
    if parsed.print {
        println!("INQUIRY_FRONTIER_BEGIN");
        println!("{}", frontier.to_json()?);
        println!("INQUIRY_FRONTIER_END");
    }
    Ok(())
}

fn run_learn(parsed: LearnArgs) -> Result<(), Box<dyn Error>> {
    let method_source = fs::read_to_string(&parsed.contract)?;
    let method_value: serde_json::Value = serde_json::from_str(&method_source)?;
    if method_value
        .get("schema")
        .and_then(serde_json::Value::as_str)
        == Some(adva_witness::FREE_ROUNDTRIP_CONTRACT_SCHEMA_V0)
    {
        return adva_witness::run_free_roundtrip_cli_v0(
            &parsed.frontier,
            &parsed.contract,
            &parsed.resource,
            &parsed.output,
            &parsed.frontier_output,
            parsed.print,
        );
    }
    if method_value
        .get("schema")
        .and_then(serde_json::Value::as_str)
        == Some(PROBLEM_FORMATION_CONTRACT_SCHEMA_V0)
    {
        return run_problem_formation(parsed);
    }
    if method_value
        .get("schema")
        .and_then(serde_json::Value::as_str)
        == Some(VALUE_SEEKING_CONTRACT_SCHEMA_V0)
    {
        return run_value_seeking(parsed);
    }
    if method_value
        .get("schema")
        .and_then(serde_json::Value::as_str)
        == Some(HYPOTHESIS_FORMATION_CONTRACT_SCHEMA_V0)
    {
        return run_hypothesis_formation(parsed);
    }
    if method_value
        .get("schema")
        .and_then(serde_json::Value::as_str)
        == Some(MAGIC_SQUARE_SEARCH_CONTRACT_SCHEMA_V0)
    {
        return run_magic_square_search(parsed);
    }

    let frontier = load_inquiry_frontier_v0(&parsed.frontier)?;
    let contract = load_exploration_contract_v0(&parsed.contract)?;
    let resource = load_resource_snapshot_v0(&parsed.resource)?;
    let transition = learn_hypothesis_v0(&frontier, &contract, &resource)?;
    let transition_receipt = save_hypothesis_transition_v0(&parsed.output, &transition)?;
    let next_frontier = &transition.output.evidence.next_frontier;
    let frontier_receipt = save_inquiry_frontier_v0(&parsed.frontier_output, next_frontier)?;

    println!("mechanism={:?}", transition.output.history.mechanism);
    println!("hypothesis={}", transition.output.result.local_name);
    println!("state={:?}", transition.output.result.state);
    println!("obligations={}", next_frontier.obligations.len());
    println!("next_sequence={}", next_frontier.lineage.sequence);
    println!(
        "new_words={}",
        transition.output.history.introduced_words.join(",")
    );
    println!("resource={}", transition.output.result.resource_digest);
    println!("transition={}", transition_receipt.artifact_digest);
    println!("next_frontier={}", frontier_receipt.artifact_digest);
    println!("output={}", transition_receipt.path.display());
    println!("frontier_output={}", frontier_receipt.path.display());
    if parsed.print {
        println!("HYPOTHESIS_TRANSITION_BEGIN");
        println!("{}", transition.to_json()?);
        println!("HYPOTHESIS_TRANSITION_END");
        println!("NEXT_INQUIRY_FRONTIER_BEGIN");
        println!("{}", next_frontier.to_json()?);
        println!("NEXT_INQUIRY_FRONTIER_END");
    }
    Ok(())
}

fn run_problem_formation(parsed: LearnArgs) -> Result<(), Box<dyn Error>> {
    let subject = load_problem_awareness_v0(&parsed.frontier)?;
    let method = load_problem_formation_contract_v0(&parsed.contract)?;
    let object = load_imagination_resource_v0(&parsed.resource)?;
    let transition = run_problem_formation_v0(&subject, &method, &object)?;
    let transition_receipt = save_problem_formation_transition_v0(&parsed.output, &transition)?;
    let next_frontier = &transition.output.evidence.next_frontier;
    let frontier_receipt = save_problem_value_frontier_v0(&parsed.frontier_output, next_frontier)?;

    println!("mechanism={:?}", transition.output.history.mechanism);
    println!("program={}", transition.input.method.program_name);
    println!("state={:?}", transition.output.result.state);
    println!(
        "quorum_fault_cases_examined={}",
        transition.output.history.quorum_fault_cases_examined
    );
    println!("problem={}", transition.output.result.problem_digest);
    println!(
        "new_words={}",
        transition.output.result.introduced_vocabulary.join(",")
    );
    println!("transition={}", transition_receipt.artifact_digest);
    println!("next_frontier={}", frontier_receipt.artifact_digest);
    println!("output={}", transition_receipt.path.display());
    println!("frontier_output={}", frontier_receipt.path.display());
    if parsed.print {
        println!("PROBLEM_FORMATION_TRANSITION_BEGIN");
        println!("{}", transition.to_json()?);
        println!("PROBLEM_FORMATION_TRANSITION_END");
        println!("PROBLEM_VALUE_FRONTIER_BEGIN");
        println!("{}", next_frontier.to_json()?);
        println!("PROBLEM_VALUE_FRONTIER_END");
    }
    Ok(())
}

fn run_value_seeking(parsed: LearnArgs) -> Result<(), Box<dyn Error>> {
    let subject = load_problem_value_frontier_v0(&parsed.frontier)?;
    let method = load_value_seeking_contract_v0(&parsed.contract)?;
    let object = load_value_seeking_resource_v0(&parsed.resource)?;
    let transition = run_value_seeking_v0(&subject, &method, &object)?;
    let transition_receipt = save_value_seeking_transition_v0(&parsed.output, &transition)?;
    let next_frontier = &transition.output.evidence.next_frontier;
    let frontier_receipt = save_problem_value_frontier_v0(&parsed.frontier_output, next_frontier)?;

    println!("mechanism={:?}", transition.output.history.mechanism);
    println!("program={}", transition.input.method.program_name);
    println!("state={:?}", transition.output.result.state);
    println!(
        "candidates_examined={}",
        transition.output.history.candidates_examined
    );
    if let Some(witness) = &transition.output.result.witness {
        println!("threshold={}", witness.selected_threshold);
        println!("honest_overlap={}", witness.guaranteed_honest_overlap);
        println!(
            "comparison={:?}:{}>{}",
            witness.comparison, witness.merge_capacity, witness.rupture_load
        );
        println!("witness={}", witness.digest(&subject, &method, &object)?);
    }
    println!("transition={}", transition_receipt.artifact_digest);
    println!("next_frontier={}", frontier_receipt.artifact_digest);
    println!("output={}", transition_receipt.path.display());
    println!("frontier_output={}", frontier_receipt.path.display());
    if parsed.print {
        println!("VALUE_SEEKING_TRANSITION_BEGIN");
        println!("{}", transition.to_json()?);
        println!("VALUE_SEEKING_TRANSITION_END");
        println!("VALUE_SEEKING_FRONTIER_BEGIN");
        println!("{}", next_frontier.to_json()?);
        println!("VALUE_SEEKING_FRONTIER_END");
    }
    Ok(())
}

fn run_hypothesis_formation(parsed: LearnArgs) -> Result<(), Box<dyn Error>> {
    let subject = load_hypothesis_formation_frontier_v0(&parsed.frontier)?;
    let method = load_hypothesis_formation_contract_v0(&parsed.contract)?;
    let object = load_hypothesis_formation_resource_v0(&parsed.resource)?;
    let transition = run_hypothesis_formation_v0(&subject, &method, &object)?;
    let transition_receipt = save_hypothesis_formation_transition_v0(&parsed.output, &transition)?;
    let next_frontier = &transition.output.evidence.next_frontier;
    let frontier_receipt =
        save_hypothesis_formation_frontier_v0(&parsed.frontier_output, next_frontier)?;

    println!("mechanism={:?}", transition.output.history.mechanism);
    println!("program={}", transition.input.method.program_name);
    println!("crossing={}", transition.output.history.crossing.name);
    println!("state={:?}", transition.output.result.state);
    println!(
        "candidates_examined={}",
        transition.output.history.candidates_examined
    );
    println!("formed_words={}", next_frontier.formed_words.len());
    if let Some(word) = &transition.output.result.search_word {
        println!("word={}({})", word.local_name, word.display_name_zh);
        println!("witness={}", word.witness_digest);
        println!("closure={}", word.witness.closure.digest()?);
    }
    println!("transition={}", transition_receipt.artifact_digest);
    println!("next_frontier={}", frontier_receipt.artifact_digest);
    println!("output={}", transition_receipt.path.display());
    println!("frontier_output={}", frontier_receipt.path.display());
    if parsed.print {
        println!("HYPOTHESIS_FORMATION_TRANSITION_BEGIN");
        println!("{}", transition.to_json()?);
        println!("HYPOTHESIS_FORMATION_TRANSITION_END");
        println!("HYPOTHESIS_FORMATION_FRONTIER_BEGIN");
        println!("{}", next_frontier.to_json()?);
        println!("HYPOTHESIS_FORMATION_FRONTIER_END");
    }
    Ok(())
}

fn run_magic_square_search(parsed: LearnArgs) -> Result<(), Box<dyn Error>> {
    let subject = load_magic_square_frontier_v0(&parsed.frontier)?;
    let method = load_magic_square_search_contract_v0(&parsed.contract)?;
    let object = load_magic_square_resource_v0(&parsed.resource)?;
    let transition = run_magic_square_search_v0(&subject, &method, &object)?;
    let transition_receipt = save_magic_square_transition_v0(&parsed.output, &transition)?;
    let next_frontier = &transition.output.evidence.next_frontier;
    let frontier_receipt = save_magic_square_frontier_v0(&parsed.frontier_output, next_frontier)?;

    println!("mechanism={:?}", transition.output.history.mechanism);
    println!("state={:?}", transition.output.result.state);
    println!(
        "nodes_expanded={}",
        transition.output.history.nodes_expanded
    );
    println!("branches_cut={}", transition.output.history.branches_cut);
    println!(
        "unselected_closures={}",
        transition.output.history.unselected_closure_digests.len()
    );
    if let Some(solution) = &transition.output.result.solution {
        println!("closure={}", solution.digest()?);
        println!("content={}", solution.content.digest()?);
    }
    if let Some(family) = &transition.output.evidence.closure_family {
        println!("family_members={}", family.members.len());
        println!("family_edges={}", family.edges.len());
        println!("line_occurrences={}", family.line_occurrences);
        println!("unique_line_contents={}", family.unique_line_contents.len());
        println!("influences={}", family.influences.len());
    }
    println!("transition={}", transition_receipt.artifact_digest);
    println!("next_frontier={}", frontier_receipt.artifact_digest);
    println!("output={}", transition_receipt.path.display());
    println!("frontier_output={}", frontier_receipt.path.display());
    if parsed.print {
        println!("MAGIC_SQUARE_TRANSITION_BEGIN");
        println!("{}", transition.to_json()?);
        println!("MAGIC_SQUARE_TRANSITION_END");
        println!("MAGIC_SQUARE_FRONTIER_BEGIN");
        println!("{}", next_frontier.to_json()?);
        println!("MAGIC_SQUARE_FRONTIER_END");
    }
    Ok(())
}

fn run_verify(parsed: VerifyArgs) -> Result<(), Box<dyn Error>> {
    let method_source = fs::read_to_string(&parsed.contract)?;
    let method_value: serde_json::Value = serde_json::from_str(&method_source)?;
    if method_value
        .get("schema")
        .and_then(serde_json::Value::as_str)
        == Some(CLOSURE_TRANSPORT_CONTRACT_SCHEMA_V0)
    {
        return run_closure_transport(parsed);
    }

    let subject = load_verification_subject_v0(&parsed.frontier)?;
    let contract = load_verification_contract_v0(&parsed.contract)?;
    let packet = load_verification_packet_v0(&parsed.packet)?;
    let transition = verify_obligations_v0(&subject, &contract, &packet)?;
    let transition_receipt = save_verification_transition_v0(&parsed.output, &transition)?;
    let next_frontier = &transition.output.evidence.residual_frontier;
    let frontier_receipt = save_verification_frontier_v0(&parsed.frontier_output, next_frontier)?;

    println!("mechanism={:?}", transition.output.history.mechanism);
    println!("state={:?}", transition.output.result.state);
    println!(
        "semantic_leaves={}->{}",
        transition.output.history.leaf_delta.semantic_before,
        transition.output.history.leaf_delta.semantic_after
    );
    println!(
        "custody_leaves={}->{}",
        transition.output.history.leaf_delta.custody_before,
        transition.output.history.leaf_delta.custody_after
    );
    println!("forks={}", transition.output.result.unresolved_forks);
    println!(
        "certificate={}",
        transition.output.result.certificate.is_some()
    );
    println!("transition={}", transition_receipt.artifact_digest);
    println!("next_frontier={}", frontier_receipt.artifact_digest);
    println!("output={}", transition_receipt.path.display());
    println!("frontier_output={}", frontier_receipt.path.display());
    if parsed.print {
        println!("VERIFICATION_TRANSITION_BEGIN");
        println!("{}", transition.to_json()?);
        println!("VERIFICATION_TRANSITION_END");
        println!("VERIFICATION_FRONTIER_BEGIN");
        println!("{}", next_frontier.to_json()?);
        println!("VERIFICATION_FRONTIER_END");
    }
    Ok(())
}

fn run_closure_transport(parsed: VerifyArgs) -> Result<(), Box<dyn Error>> {
    let subject = load_local_closure_candidate_v0(&parsed.frontier)?;
    let contract = load_closure_transport_contract_v0(&parsed.contract)?;
    let plan = load_closure_transport_plan_v0(&parsed.packet)?;
    let transition = run_closure_transport_v0(&subject, &contract, &plan)?;
    let transition_receipt = save_closure_transport_transition_v0(&parsed.output, &transition)?;
    let frontier = &transition.output.evidence.residual_frontier;
    let frontier_receipt = save_closure_transport_frontier_v0(&parsed.frontier_output, frontier)?;

    println!("mechanism={:?}", transition.output.history.mechanism);
    println!("local_closure=Checked");
    println!("transport_composition=Checked");
    println!("direct_equals_staged=Checked");
    println!("negative_controls=2/2_rejected");
    println!("frontier={:?}", frontier.state);
    println!(
        "reopened_scopes={}",
        frontier.reopened_after_challenge.len()
    );
    println!("certificate={}", transition.output.result.local.digest()?);
    println!("transition={}", transition_receipt.artifact_digest);
    println!("next_frontier={}", frontier_receipt.artifact_digest);
    println!("output={}", transition_receipt.path.display());
    println!("frontier_output={}", frontier_receipt.path.display());
    if parsed.print {
        println!("CLOSURE_TRANSPORT_TRANSITION_BEGIN");
        println!("{}", transition.to_json()?);
        println!("CLOSURE_TRANSPORT_TRANSITION_END");
        println!("CLOSURE_TRANSPORT_FRONTIER_BEGIN");
        println!("{}", frontier.to_json()?);
        println!("CLOSURE_TRANSPORT_FRONTIER_END");
    }
    Ok(())
}

fn run_reveal(parsed: RevealArgs) -> Result<(), Box<dyn Error>> {
    let source = fs::read_to_string(&parsed.program)?;
    let document = AdvaDocumentV0::from_json(&source)?;
    let witness = run_m6_reveal_v0(&document, M6NamingPlanV0::first_calibration(), parsed.fuel)?;
    let receipt = save_reveal_witness_v0(&parsed.output, &witness)?;

    println!("state={:?}", witness.state);
    println!("fuel={}/{}", witness.fuel_used, witness.fuel_requested);
    println!("questions={}", witness.questions.len());
    println!("source={}", witness.source_document_digest);
    println!("witness={}", receipt.witness_digest);
    println!("output={}", receipt.path.display());
    if parsed.print {
        println!("FIRST_REVEAL_WITNESS_BEGIN");
        println!("{}", witness.to_json()?);
        println!("FIRST_REVEAL_WITNESS_END");
    }
    Ok(())
}

fn run_trace_arithmetic(parsed: TraceArithmeticArgs) -> Result<(), Box<dyn Error>> {
    let witness = load_reveal_witness_v0(&parsed.witness)?;
    let calibration = calibrate_trace_arithmetic_v0(&witness)?;
    let receipt = save_trace_arithmetic_v0(&parsed.output, &calibration)?;

    println!("time={:?}", calibration.alignment.time);
    println!("space={:?}", calibration.alignment.space);
    println!("construction={:?}", calibration.alignment.construction);
    println!(
        "holonomy_one={}",
        calibration.commutative_holonomy.right_over_left.is_one()
    );
    println!("truth_fiber={:?}", calibration.truth_fiber.state);
    println!("questions={}", calibration.questions.len());
    println!("source={}", calibration.source_witness_digest);
    println!("calibration={}", receipt.calibration_digest);
    println!("output={}", receipt.path.display());
    if parsed.print {
        println!("TRACE_ARITHMETIC_CALIBRATION_BEGIN");
        println!("{}", calibration.to_json()?);
        println!("TRACE_ARITHMETIC_CALIBRATION_END");
    }
    Ok(())
}

fn parse_reveal_args(arguments: impl IntoIterator<Item = String>) -> io::Result<RevealArgs> {
    let mut arguments = arguments.into_iter();
    let program = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing reveal program"))?;
    let mut output = None;
    let mut fuel = 6;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--output requires a path"))?;
                output = Some(PathBuf::from(value));
            }
            "--fuel" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--fuel requires an integer"))?;
                fuel = value
                    .parse::<u64>()
                    .map_err(|_| invalid_input("--fuel must be a nonnegative integer"))?;
            }
            "--print" => print = true,
            _ => return Err(invalid_input(format!("unknown argument {argument:?}"))),
        }
    }
    let output = output.ok_or_else(|| invalid_input("--output is required"))?;
    Ok(RevealArgs {
        program,
        output,
        fuel,
        print,
    })
}

fn parse_trace_arithmetic_args(
    arguments: impl IntoIterator<Item = String>,
) -> io::Result<TraceArithmeticArgs> {
    let mut arguments = arguments.into_iter();
    let witness = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing reveal witness"))?;
    let mut output = None;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--output requires a path"))?;
                output = Some(PathBuf::from(value));
            }
            "--print" => print = true,
            _ => return Err(invalid_input(format!("unknown argument {argument:?}"))),
        }
    }
    let output = output.ok_or_else(|| invalid_input("--output is required"))?;
    Ok(TraceArithmeticArgs {
        witness,
        output,
        print,
    })
}

fn parse_frontier_args(arguments: impl IntoIterator<Item = String>) -> io::Result<FrontierArgs> {
    let mut arguments = arguments.into_iter();
    let calibration = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing trace-arithmetic calibration"))?;
    let mut output = None;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--output requires a path"))?;
                output = Some(PathBuf::from(value));
            }
            "--print" => print = true,
            _ => return Err(invalid_input(format!("unknown argument {argument:?}"))),
        }
    }
    Ok(FrontierArgs {
        calibration,
        output: output.ok_or_else(|| invalid_input("--output is required"))?,
        print,
    })
}

fn parse_learn_args(arguments: impl IntoIterator<Item = String>) -> io::Result<LearnArgs> {
    let mut arguments = arguments.into_iter();
    let frontier = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing inquiry frontier"))?;
    let contract = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing exploration contract"))?;
    let resource = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing resource snapshot"))?;
    let mut output = None;
    let mut frontier_output = None;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--output requires a path"))?;
                output = Some(PathBuf::from(value));
            }
            "--frontier-output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--frontier-output requires a path"))?;
                frontier_output = Some(PathBuf::from(value));
            }
            "--print" => print = true,
            _ => return Err(invalid_input(format!("unknown argument {argument:?}"))),
        }
    }
    Ok(LearnArgs {
        frontier,
        contract,
        resource,
        output: output.ok_or_else(|| invalid_input("--output is required"))?,
        frontier_output: frontier_output
            .ok_or_else(|| invalid_input("--frontier-output is required"))?,
        print,
    })
}

fn parse_verify_args(arguments: impl IntoIterator<Item = String>) -> io::Result<VerifyArgs> {
    let mut arguments = arguments.into_iter();
    let frontier = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing verification frontier"))?;
    let contract = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing verification contract"))?;
    let packet = arguments
        .next()
        .map(PathBuf::from)
        .ok_or_else(|| invalid_input("missing verification packet"))?;
    let mut output = None;
    let mut frontier_output = None;
    let mut print = false;
    while let Some(argument) = arguments.next() {
        match argument.as_str() {
            "--output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--output requires a path"))?;
                output = Some(PathBuf::from(value));
            }
            "--frontier-output" => {
                let value = arguments
                    .next()
                    .ok_or_else(|| invalid_input("--frontier-output requires a path"))?;
                frontier_output = Some(PathBuf::from(value));
            }
            "--print" => print = true,
            _ => return Err(invalid_input(format!("unknown argument {argument:?}"))),
        }
    }
    Ok(VerifyArgs {
        frontier,
        contract,
        packet,
        output: output.ok_or_else(|| invalid_input("--output is required"))?,
        frontier_output: frontier_output
            .ok_or_else(|| invalid_input("--frontier-output is required"))?,
        print,
    })
}

fn invalid_input(detail: impl Into<String>) -> io::Error {
    io::Error::new(ErrorKind::InvalidInput, detail.into())
}
