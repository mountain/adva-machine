//! Research-local checker for rename declarations.
//!
//! Run:
//! ```text
//! cargo run --quiet -- --contract fixtures/contract.json --out result.json
//! ```
//!
//! It adds no Adva `ValueType`, `OperationSpec`, registry entry, IR version or
//! `Seal`, and native admission is NotGranted.  It is an executable contract
//! plus its retained evidence, nothing more.

mod algebra;
mod declaration;
mod grammar;
mod kernel;
mod level;
mod sha256;

use declaration::{Declaration, check};
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

fn arguments() -> Result<(PathBuf, PathBuf, PathBuf), String> {
    let mut contract = PathBuf::from("fixtures/contract.json");
    let mut out = PathBuf::from("result.json");
    // the crate lives at <root>/experiments/rename-declaration, and a
    // declaration names its source relative to the repository root
    let mut root = PathBuf::from("../..");
    let mut args = std::env::args().skip(1);
    while let Some(argument) = args.next() {
        match argument.as_str() {
            "--contract" => {
                contract = args.next().ok_or("--contract needs a path")?.into();
            }
            "--out" => {
                out = args.next().ok_or("--out needs a path")?.into();
            }
            "--root" => {
                root = args.next().ok_or("--root needs a path")?.into();
            }
            other => return Err(format!("unexpected argument {other:?}")),
        }
    }
    Ok((contract, out, root))
}

fn read_json(path: &Path) -> Result<Value, String> {
    let text =
        std::fs::read_to_string(path).map_err(|e| format!("reading {}: {e}", path.display()))?;
    serde_json::from_str(&text).map_err(|e| format!("parsing {}: {e}", path.display()))
}

fn read_declaration(path: &Path) -> Result<Declaration, String> {
    let text =
        std::fs::read_to_string(path).map_err(|e| format!("reading {}: {e}", path.display()))?;
    serde_json::from_str(&text).map_err(|e| format!("parsing {}: {e}", path.display()))
}

/// Evaluate one declared control against the run's outcomes.
fn eval_control(control: &Value, outcomes: &BTreeMap<String, Value>) -> Result<(), String> {
    let id = control["id"].as_str().ok_or("control without an id")?;
    let declaration = control["declaration"]
        .as_str()
        .ok_or_else(|| format!("control {id:?} names no declaration"))?;
    let actual = outcomes
        .get(declaration)
        .ok_or_else(|| format!("control {id:?} names unknown declaration {declaration:?}"))?;
    let expect = control
        .get("expect")
        .ok_or_else(|| format!("control {id:?} declares no expectation"))?;

    let check_field = |path: &str, expected: &Value| -> Result<(), String> {
        let found = actual
            .pointer(path)
            .ok_or_else(|| format!("control {id:?}: no field at {path} in {declaration:?}"))?;
        if found == expected {
            Ok(())
        } else {
            Err(format!(
                "control {id:?}: {path} is {found}, declared {expected}"
            ))
        }
    };

    if let Some(expected) = expect.get("outcome") {
        check_field("/outcome", expected)?;
    }
    if let Some(expected) = expect.get("digest_verified") {
        check_field("/source/digest_verified", expected)?;
    }
    if let Some(expected) = expect.get("algebra_order_profile") {
        let found = actual["algebra_profile"]["element_order_profile"].clone();
        if &found != expected {
            return Err(format!(
                "control {id:?}: the algebra's element-order profile is {found}, declared {expected}"
            ));
        }
    }
    if let Some(needle) = expect.get("violation_contains").and_then(Value::as_str) {
        // a control may name either kind of violation: the signature's or the
        // level's.  Both are refusals of the declared rename.
        let mut violations: Vec<String> = actual["declared_rename"]["signature_violations"]
            .as_array()
            .cloned()
            .unwrap_or_default()
            .iter()
            .filter_map(|v| v.as_str().map(str::to_string))
            .collect();
        if let Some(level) = actual["level"]["level_violations"].as_array() {
            violations.extend(level.iter().filter_map(|v| v.as_str().map(str::to_string)));
        }
        if !violations.iter().any(|v| v.contains(needle)) {
            return Err(format!(
                "control {id:?}: no signature or level violation contains {needle:?}; saw {violations:?}"
            ));
        }
    }
    if expect.get("collisions_nonempty").and_then(Value::as_bool) == Some(true) {
        let collisions = &actual["declared_rename"]["collisions"];
        if collisions.as_array().is_none_or(|a| a.is_empty()) {
            return Err(format!("control {id:?}: expected a collision, found none"));
        }
    }
    if let Some(relation_set) = control["relation_set"].as_str() {
        let witnesses = actual["kernel_witnesses"]
            .as_array()
            .cloned()
            .unwrap_or_default();
        let witness = witnesses
            .iter()
            .find(|w| w["relation_set"] == Value::String(relation_set.to_string()))
            .ok_or_else(|| {
                format!("control {id:?}: no kernel witness for relation set {relation_set:?}")
            })?;
        if let Some(expected) = expect.get("kernel_is_total") {
            if &witness["kernel_is_total"] != expected {
                return Err(format!(
                    "control {id:?}: kernel_is_total is {}, declared {expected}",
                    witness["kernel_is_total"]
                ));
            }
        }
        if let Some(expected) = expect.get("cross_level_is") {
            if &witness["cross_level"] != expected {
                return Err(format!(
                    "control {id:?}: cross_level is {}, declared {expected}",
                    witness["cross_level"]
                ));
            }
        }
        if let Some(expected) = expect.get("measuring_level_is") {
            if &witness["measuring_level"] != expected {
                return Err(format!(
                    "control {id:?}: measuring_level is {}, declared {expected}",
                    witness["measuring_level"]
                ));
            }
        }
        if let Some(bound) = expect.get("kernel_order_at_most").and_then(Value::as_u64) {
            let order = witness["kernel_order"].as_u64().unwrap_or(u64::MAX);
            if order > bound {
                return Err(format!(
                    "control {id:?}: kernel order {order} exceeds the declared bound {bound}"
                ));
            }
        }
        if let Some(bound) = expect.get("kernel_order_at_least").and_then(Value::as_u64) {
            let order = witness["kernel_order"].as_u64().unwrap_or(0);
            if order < bound {
                return Err(format!(
                    "control {id:?}: kernel order {order} is below the declared bound {bound}"
                ));
            }
        }
        if let Some(expected) = expect
            .get("kernel_touching_the_source_len")
            .and_then(Value::as_u64)
        {
            let len = witness["kernel_restricted_to_renames_touching_the_source"]
                .as_array()
                .map_or(0, Vec::len) as u64;
            if len != expected {
                return Err(format!(
                    "control {id:?}: {len} kernel members touch the source, declared {expected}"
                ));
            }
        }
        if expect
            .get("has_non_abelian_witness")
            .and_then(Value::as_bool)
            == Some(true)
            && witness["non_abelian_kernel_witness"].is_null()
        {
            return Err(format!(
                "control {id:?}: expected a non-abelian kernel witness, found none"
            ));
        }

        // invariants that hold by construction, checked rather than assumed
        let kernel = witness["kernel_order"].as_u64().unwrap_or(0);
        let visible = witness["visible_renames"].as_u64().unwrap_or(0);
        let admissible = witness["admissible_renames"].as_u64().unwrap_or(u64::MAX);
        let moving_nothing = witness["kernel_moving_nothing"].as_u64().unwrap_or(0);
        if expect
            .get("kernel_plus_visible_equals_admissible")
            .and_then(Value::as_bool)
            == Some(true)
            && kernel + visible != admissible
        {
            return Err(format!(
                "control {id:?}: kernel {kernel} + visible {visible} != admissible {admissible}"
            ));
        }
        if expect
            .get("kernel_equals_admissible")
            .and_then(Value::as_bool)
            == Some(true)
            && kernel != admissible
        {
            return Err(format!(
                "control {id:?}: the kernel {kernel} is not the whole admissible set {admissible}"
            ));
        }
        if expect
            .get("kernel_strictly_inside_admissible")
            .and_then(Value::as_bool)
            == Some(true)
            && kernel >= admissible
        {
            return Err(format!(
                "control {id:?}: the kernel {kernel} is not strictly inside the admissible set {admissible}"
            ));
        }
        if expect
            .get("every_rename_that_moves_nothing_is_in_the_kernel")
            .and_then(Value::as_bool)
            == Some(true)
            && moving_nothing > kernel
        {
            return Err(format!(
                "control {id:?}: {moving_nothing} renames move nothing but only {kernel} are in the kernel"
            ));
        }
    }
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(failures) if failures.is_empty() => ExitCode::SUCCESS,
        Ok(failures) => {
            eprintln!(
                "{} declared control(s) did not behave as declared",
                failures.len()
            );
            for failure in &failures {
                eprintln!("  - {failure}");
            }
            ExitCode::FAILURE
        }
        Err(message) => {
            eprintln!("error: {message}");
            ExitCode::FAILURE
        }
    }
}

fn run() -> Result<Vec<String>, String> {
    let (contract_path, out_path, root) = arguments()?;
    let contract = read_json(&contract_path)?;
    if contract["schema"] != "adva.rename-declaration.contract.v0" {
        return Err(format!(
            "unexpected contract schema {:?}",
            contract["schema"]
        ));
    }
    let base = contract_path
        .parent()
        .map_or_else(|| PathBuf::from("."), Path::to_path_buf);

    let mut outcomes: BTreeMap<String, Value> = BTreeMap::new();
    let mut order: Vec<String> = Vec::new();
    for entry in contract["declarations"]
        .as_array()
        .ok_or("contract declares no declarations")?
    {
        let relative = entry.as_str().ok_or("declaration entry is not a path")?;
        let path = base.join(relative);
        let declaration = read_declaration(&path)?;
        let outcome = check(&declaration, &root).map_err(|e| format!("{}: {e}", path.display()))?;
        order.push(declaration.name.clone());
        outcomes.insert(declaration.name.clone(), outcome);
    }

    let mut control_rows: Vec<Value> = Vec::new();
    let mut failures: Vec<String> = Vec::new();
    for control in contract["controls"]
        .as_array()
        .ok_or("contract declares no controls")?
    {
        let id = control["id"].as_str().unwrap_or("<unnamed>").to_string();
        match eval_control(control, &outcomes) {
            Ok(()) => control_rows.push(json!({ "id": id, "held": true })),
            Err(message) => {
                control_rows.push(json!({ "id": id, "held": false, "reason": message }));
                failures.push(message);
            }
        }
    }

    let all_controls_held = failures.is_empty();
    let result = json!({
        "schema": "adva.rename-declaration.result.v0",
        "profile": contract["profile"],
        "question": contract["question"],
        "level": contract["level"],
        "outcome": if all_controls_held { "RenameDeclarationsChecked" } else { "ControlFailed" },
        "declarations": order.iter().map(|name| outcomes[name].clone()).collect::<Vec<_>>(),
        "controls": control_rows,
        "controls_held": all_controls_held,
        "acceptance": contract["acceptance"],
        "residual": contract["residual"],
    });

    let text = serde_json::to_string_pretty(&result).map_err(|e| e.to_string())?;
    std::fs::write(&out_path, format!("{text}\n"))
        .map_err(|e| format!("writing {}: {e}", out_path.display()))?;
    println!(
        "{} declarations, {} controls, {} failed -> {}",
        order.len(),
        control_rows.len(),
        failures.len(),
        out_path.display()
    );
    Ok(failures)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A synthetic outcome, so the control machinery can be tested without
    /// running the whole contract.  It deliberately satisfies the invariants
    /// kernel + visible = admissible and moves-nothing <= kernel.
    fn outcomes() -> BTreeMap<String, Value> {
        let mut outcomes = BTreeMap::new();
        outcomes.insert(
            "d".to_string(),
            json!({
                "outcome": "Accepted",
                "declared_rename": {
                    "signature_violations": ["KindChanged { token: '*' }"],
                    "collisions": [],
                },
                "algebra_profile": {
                    "element_order_profile": {"1": 1, "2": 5, "4": 2},
                },
                "kernel_witnesses": [{
                    "relation_set": "k",
                    "inverse_monoid_order": 209,
                    "admissible_renames": 65,
                    "visible_renames": 0,
                    "kernel_order": 65,
                    "kernel_is_total": true,
                    "kernel_is_abelian": false,
                    "kernel_moving_nothing": 16,
                    "kernel_restricted_to_renames_touching_the_source": [],
                    "non_abelian_kernel_witness": ["a->b", "b->a"],
                }],
            }),
        );
        outcomes
    }

    fn control(body: Value) -> Value {
        body
    }

    #[test]
    fn a_control_that_holds_is_accepted() {
        let outcomes = outcomes();
        let c = control(json!({
            "id": "ok",
            "declaration": "d",
            "expect": {"outcome": "Accepted"},
        }));
        assert!(eval_control(&c, &outcomes).is_ok());
    }

    #[test]
    fn a_control_that_does_not_hold_fails_with_a_located_reason() {
        let outcomes = outcomes();
        let c = control(json!({
            "id": "wrong-outcome",
            "declaration": "d",
            "expect": {"outcome": "Refused"},
        }));
        let error = eval_control(&c, &outcomes).unwrap_err();
        assert!(error.contains("wrong-outcome"), "{error}");
        assert!(error.contains("/outcome"), "{error}");
    }

    #[test]
    fn the_algebra_profile_control_catches_a_wrong_group() {
        let outcomes = outcomes();
        // the four named generators alone have profile {1:1, 2:2, 4:1}; the
        // full closure has {1:1, 2:5, 4:2}.  Declaring the former must fail.
        let c = control(json!({
            "id": "wrong-group",
            "declaration": "d",
            "expect": {"algebra_order_profile": {"1": 1, "2": 2, "4": 1}},
        }));
        assert!(eval_control(&c, &outcomes).is_err());
    }

    #[test]
    fn the_invariant_controls_catch_a_broken_kernel() {
        // break kernel + visible = admissible
        let mut broken_sum = outcomes();
        broken_sum.get_mut("d").unwrap()["kernel_witnesses"][0]["kernel_order"] = json!(60);
        let c = control(json!({
            "id": "broken-sum",
            "declaration": "d",
            "relation_set": "k",
            "expect": {"kernel_plus_visible_equals_admissible": true},
        }));
        let error = eval_control(&c, &broken_sum).unwrap_err();
        assert!(error.contains("admissible"), "{error}");

        // break "every rename that moves nothing is in the kernel": the
        // invariant is moving_nothing <= kernel, so this has to exceed 65
        let mut broken_kernel = outcomes();
        broken_kernel.get_mut("d").unwrap()["kernel_witnesses"][0]["kernel_moving_nothing"] =
            json!(66);
        let c = control(json!({
            "id": "moving-nothing-outside",
            "declaration": "d",
            "relation_set": "k",
            "expect": {"every_rename_that_moves_nothing_is_in_the_kernel": true},
        }));
        assert!(eval_control(&c, &broken_kernel).is_err());
    }

    #[test]
    fn a_control_naming_an_unknown_declaration_fails() {
        let outcomes = outcomes();
        let c = control(json!({
            "id": "typo",
            "declaration": "not-there",
            "expect": {"outcome": "Accepted"},
        }));
        let error = eval_control(&c, &outcomes).unwrap_err();
        assert!(error.contains("unknown declaration"), "{error}");
    }

    #[test]
    fn a_control_referring_to_a_missing_relation_set_fails() {
        let outcomes = outcomes();
        let c = control(json!({
            "id": "missing-set",
            "declaration": "d",
            "relation_set": "no-such-set",
            "expect": {"kernel_is_total": true},
        }));
        let error = eval_control(&c, &outcomes).unwrap_err();
        assert!(error.contains("no kernel witness"), "{error}");
    }
}
