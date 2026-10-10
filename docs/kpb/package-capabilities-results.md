# Package-capability and reference trial: local results

Date: 2026-10-10. Draft evidence for the
[proposal](../../spec/framework/package-capabilities-v0.1-proposal.md), not adoption.
Authored and run by dot (OpenAI), under Unknown v0.3, prepared for submission
through Mingli Yuan's account as an authorized proxy; account use is not his
technical review, endorsement or a correctness guarantee.

The [retained trial report](package-capabilities-trial-2026-10-10.json) records
exact tested source digests, Python/jsonschema/Git versions, all 46 unit test
names, two subsequent manifest rechecks and aggregate observed costs. The
10-second aggregate trial passed. The reference controls use locally generated
original Git fixtures; no external content, PDF, library migration or network
reference fetch is part of the trial. Manifest success and located-reference
success both retain semantic verification NotRun and native admission NotGranted.

The code changed during independent review before the retained run: predecessor
source-contract naming was clarified, resource accounting/timeout evidence was
improved, schema/depth controls were added, and lazy fetch was disabled explicitly.
The first attempted outer timing command failed because /usr/bin/time was absent;
no tests were executed by that command. The replacement Python supervisor records
its own timing boundaries and limits. Earlier smoke tests are not substituted for
this final trial. No failed mathematical result or old evidence was overwritten.

The publication check found no identified withdrawn content in 4,569 unique
staged/index blobs and 12,444 scanned members (388,159,880 expanded bytes). Its
history check covered only locally reachable objects in the shallow checkout;
submodules and unavailable older history were not certified. This is the
repository's known-withdrawal check, not a copyright/admission or whole-history
guarantee. Newly authored files contain original prose, schemas, code and fixtures
only; no third-party implementation or source payload is bundled.

Local verification does not include the full Rust or repository Python suite.
No native semantic files, operation registry, dependency lock, existing contract,
frozen evidence, source home or consumer pin was changed. The new focused CI
workflow runs the same documentary tests on pull requests; its eventual status
must be checked against the exact published commit separately.
