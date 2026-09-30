//! Research-only local checked-cache pilot. No stable API or serialized loader.
//! Project-original, contributed under Unknown v0.3 by dot (OpenAI), through
//! Mingli Yuan's authorized account proxy; account use is not technical review.

#[path = "checked_roundtrip.rs"]
mod pilot;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    if std::env::args_os().len() != 1 {
        return Err(
            "this fixed pilot accepts no arguments, serialized cache, proof or success flag".into(),
        );
    }
    let report = pilot::compare()?;
    let (bytes, delivery_account) = pilot::encode_report(&report)?;
    // Encoding/storage counts are a separate delivery account, not hidden in reuse.
    eprintln!("report_encoding_account={delivery_account}");
    use std::io::Write;
    std::io::stdout().write_all(&bytes)?;
    std::io::stdout().write_all(b"\n")?;
    Ok(())
}
