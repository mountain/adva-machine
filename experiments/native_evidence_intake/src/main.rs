//! Bounded primitive intake, distinct from unchanged documentary transport.
mod intake;
// The retained module contains its original comparison/control entry points.
// They remain tested unchanged, but are not exposed by this successor CLI.
#[allow(dead_code)]
mod native;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    match args.as_slice() {
        [command] if command == "emit-fixture" => {
            use std::io::Write;
            std::io::stdout().write_all(&intake::canonical(&intake::fixture()))?;
        }
        [command] if command == "receiver-binding" => {
            use std::io::Write;
            std::io::stdout().write_all(&intake::emit_binding().map_err(|e| format!("{e:?}"))?)?;
        }
        [command, payload, binding, pin_flag, expected, receiver_flag, receiver, context_flag, context]
            if command == "check" && pin_flag == "--expect-binding" && receiver_flag == "--receiver" && context_flag == "--context" => {
                let report = intake::check_paths(payload.as_ref(), binding.as_ref(), expected, receiver, context);
                intake::print_report(&report)?;
                std::process::exit(match report.outcome { "LocalCheckedAndUsed" => 0, "Rejected" => 2, _ => 3 });
            }
        _ => return Err("expected emit-fixture | receiver-binding | check PAYLOAD BINDING --expect-binding BLAKE3 --receiver NAME --context CONTEXT; no receipt/checked-handle loader".into()),
    }
    Ok(())
}
