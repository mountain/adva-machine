# Public repository admission boundary

Mingli Yuan's direction, 2026-09-16: material outside the public domain must
not be brought into the public repositories. This common policy applies to
`adva`, `adva-library`, and `adva-machine`.

**Default: do not admit content until its publication basis is established.**
Public availability, lawful access, attribution, and permission to redistribute
are not substitutes for this project's public-domain admission requirement.
This is a contribution and publication policy, not a change to the licenses
already granted to recipients.

## Eligible content

| Basis | Required evidence |
| --- | --- |
| Project-original | The contributor created the content, controls the relevant rights, and contributes those rights under Unknown v0.3. Identify any incorporated third-party components separately. |
| Verified CC0 | The exact material and version are covered by CC0 applied by an identifiable rights holder with authority to do so. Record the source and dedication evidence. |
| Verified public domain | Document why the exact material is in the public domain, including the relevant jurisdictions and any limitations. Unresolved or conflicting status blocks admission. |

An open license such as CC BY, CC BY-SA, MIT, or Apache-2.0 is not itself a
public-domain basis. Do not copy newly supplied third-party content into these
repositories merely because its license permits redistribution. A fair-use
argument, research purpose, or an agent's assertion also does not establish
eligibility under this stricter project policy. Do not apply Unknown to rights
held by someone else. An AI-assisted origin does not itself establish that an
output contains no third-party expression.

Apply this review to the complete publication unit: code, prose, quotations,
full texts, figures, page images, audio, video, datasets, test fixtures,
embedded resources, and all nested archive members. Transformation does not
clear the source: OCR, translation, transcription, rendering, cropping,
compression, encoding, and reversible representations retain their provenance
obligations. An original addition cannot clear an incorporated ineligible part.
An old public-domain work does not automatically clear a modern edition,
translation, annotation, photograph, or other added component.

## Publication record and workflow

For each imported resource or externally derived publication unit, complete
[`governance/publication/admission-record.template.json`](governance/publication/admission-record.template.json).
Keep the draft and candidate bytes outside repository directories. Record:

1. Exact destination paths, byte sizes, and SHA-256 digests.
2. Source/version, creator or rights holder, and incorporated source components.
3. The eligible basis, supporting source links, and jurisdictional assessment.
4. Transformations and the basis for publishing their resulting contents.
5. The actual reviewer, review date, decision, and unresolved questions.

The template starts `pending` and admits nothing. Only `admitted` with complete
evidence, every component accounted for, and no unresolved eligibility question
allows import. A missing record, placeholder, unknown basis, or conflicting
evidence means refusal for publication. Changing the bytes or adding a
component requires a new review; an old digest does not cover the new file.
Keep completed records in `governance/publication/records/` with the admitted
files. Include concise evidence references, not copies of ineligible material.

Routine first-party code and documentation changes may use their explicit
contribution under Unknown and normal author/proxy attribution as their origin
record. This does not waive review of copied or externally derived parts.
Never name Mingli as the reviewer merely because his account submits a change.

Before committing or uploading, inspect the exact staged diff and file list,
then run the existing known-withdrawal check:

```sh
git diff --cached --stat
git diff --cached
python scripts/check_publication_boundary.py --history
```

The commands inspect staged content and locally available history. They are
supplementary checks, not approval of rights. Publish only the reviewed payload;
avoid bulk directory imports that can include unrelated local research files.
Review must precede **any public upload**, including side branches and draft
pull requests, not just a merge into `main`.

## External research and software dependencies

Material lacking an eligible basis stays outside repository directories and
public publishing workflows. Where access and processing are permitted, a
private experiment may receive explicitly supplied external inputs. Do not
automatically download them into the repository, public CI, or release staging.
An ignored directory is not sufficient isolation: forced staging, archives,
logs, caches, and artifact upload can still disclose its contents.

The public side may retain reviewed bibliographic identifiers, source links,
digests, original methods, and independently reviewed results. A digest grants
neither access nor publication rights. Generated outputs, logs, reports,
caches, screenshots, test evidence, and release bundles undergo the same review;
calling something a summary or measurement is not automatic clearance.
Missing private inputs must yield an explicit unavailable/refused/skipped
outcome, not a new claim that the original experiment passed. Use original or
verified public-domain fixtures for publicly reproducible multimodal tests.

Software dependencies remain separately identified, version-pinned, and
obtained in dependency/build environments under their own licenses. A manifest,
lock, or Git reference does not dedicate dependency contents to the public
domain. Do not vendor newly acquired non-public-domain source or bundle it into
public artifacts under the project's dedication. Retain existing third-party
notices; this policy does not relicense existing dependencies or authorize
breaking verified dependency chains. Any proposed redistribution of dependency
contents needs its own explicit policy decision before publication.

## What is enforced and what remains open

This document and `AGENTS.md` establish a mandatory contributor/agent workflow.
The admission record is a review record, not an executable authorization token.
No native Adva `accept`, `Seal`, or general communication operation is created
by this document.

The current `check_publication_boundary.py` detects the **identified withdrawn
bytes**, including its supported archive cases, and optionally their reachable
Git object identities. It does not implement this new admission-record policy,
identify arbitrary third-party expression, or decide copyright status. GitHub
Actions run after upload; a passing or required CI check cannot prevent first
disclosure on a public branch. Existing push permissions have not been changed.

A future enforced publishing route must validate records against exact payloads
before upload, cover all contributors and publication channels, and retain
rights review as a separate obligation. Local hooks can prevent accidents but
are bypassable. Do not report that such a route already exists.

Previously committed content is not certified by this policy. The completed
withdrawal covers its identified inventory; remaining legacy content and future
imports still require appropriate review. Neither an existing baseline nor a
green check establishes that the entire repository is public-domain material.

## References and authorship

- [Creative Commons: public-domain tools](https://creativecommons.org/public-domain/)
  distinguishes public-domain dedication from copyright licenses.
- [Creative Commons: Public Domain Mark](https://creativecommons.org/public-domain/pdm/)
  explains the mark and the limits of jurisdiction-specific status.
- [LICENSING.md](LICENSING.md) defines the project's own dedication and its scope.

Policy direction: Mingli Yuan. Drafting and repository integration: ChatGPT
(OpenAI), through Mingli Yuan's authorized account proxy. Account use is not
Mingli's authorship, legal review, or a correctness guarantee.
