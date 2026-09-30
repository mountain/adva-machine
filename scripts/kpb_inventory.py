#!/usr/bin/env python3
"""KPB-14 documentary projection. Never imports, executes or admits packages.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through
Mingli Yuan's authorized account proxy; not his review or endorsement.
"""
import argparse
import ast
import hashlib
import json
import re
import subprocess
import tomllib
from pathlib import Path

AUTHORITY = 'documentary tooling; metadata consistency only; no native admission'
MAX_BYTES = 8 * 1024 * 1024


class Repository:
    def __init__(self, name, root, revision='HEAD'):
        self.name, self.root = name, Path(root)
        self.cache = {}
        self.total_bytes = 0
        self.commit = self.git('rev-parse', '--verify', revision + '^{commit}').strip()
        if not re.fullmatch('[0-9a-f]{40}', self.commit):
            raise ValueError('full commit required')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], timeout=20,
                                       stderr=subprocess.PIPE).decode()

    def read(self, path):
        if path.startswith('/') or '..' in Path(path).parts or ':' in path:
            raise ValueError('unsafe repository path')
        if path in self.cache:
            return self.cache[path]
        size = int(self.git('cat-file', '-s', self.commit + ':' + path))
        if size > MAX_BYTES or self.total_bytes + size > 32 * MAX_BYTES:
            raise ValueError('read byte budget exhausted')
        self.total_bytes += size
        self.cache[path] = self.git('show', self.commit + ':' + path)
        return self.cache[path]

    def ref(self, path):
        return dict(repository=self.name, path=path, full_commit=self.commit)


def unit(repo, path, selector, revision=None, premises=None, exports=None,
         checker=None, guards=None, dependencies=None):
    raw = repo.read(path)
    fields = dict(revision=revision, premises=premises, exports=exports,
                  checker_profile=checker, guards=guards)
    return dict(repo.ref(path), selector=selector,
                documentary_id=f'{repo.name}@{repo.commit}:{path}#{selector}',
                source_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                **fields, dependency_edges=dependencies or [],
                dependency_coverage='Only explicit registry dependencies and documented pilot implementation edges; other dependencies unresolved',
                authority_boundary=AUTHORITY,
                unresolved_fields=[k for k, v in fields.items() if v is None] +
                ['authorship/publication basis: consult source policy',
                 'resource enforcement/build bindings: not established by this view',
                 'interface/effects/input bindings: consult scoped source, not validated here',
                 'evidence receiver/lifecycle/custody: not established by this view',
                 'receiving/admission: not executed'])


def metadata_issues(u):
    issues = []
    for field in ('premises', 'guards', 'checker_profile'):
        if u.get(field) is None:
            issues.append('unavailable:' + field)
        elif field in u.get('required_nonempty', []) and not u[field]:
            issues.append('invalid:deleted ' + field)
    if u.get('verified') or u.get('native_admission'):
        issues.append('invalid:untrusted success/admission flag')
    return issues


def resolve_dependency(source, value, repositories, claim_ids):
    # IDs are resolved only in the owning registry. No name/number fallback.
    if isinstance(value, str) and value in claim_ids:
        return dict(kind='declared-dependency', declared=value,
                    target=claim_ids[value], status='resolved-metadata',
                    resolution_basis='exact ID in owning claims registry')
    # An explicitly declared relative path in the owning registry is a local
    # source reference. Bind that exact path only, never a similar filename or
    # a file in another repository. This resolves bytes, not a proof premise.
    if isinstance(value, str) and '/' in value:
        try:
            raw = source.read(value)
        except (ValueError, subprocess.CalledProcessError):
            return dict(kind='declared-dependency', declared=value, status='unresolved',
                        attempted_source=source.ref(value),
                        reason='Exact local path unavailable or refused; no cross-repository fallback')
        return dict(kind='declared-file-dependency', declared=value,
                    target=f'{source.name}@{source.commit}:{value}#dependency-file',
                    target_source=source.ref(value),
                    source_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                    status='resolved-metadata',
                    resolution_basis='explicit relative path in owning registry at selected immutable commit',
                    semantic_boundary='File availability/integrity only; no imported judgment, proof derivation or admission')
    return dict(kind='declared-dependency', declared=value, status='unresolved',
                attempted_source=source.ref('docs/claims.toml'),
                reason='Exact claim ID absent from owning registry; no alias, number or similarity substitution')


def build(repos):
    units = []
    adva, machine, library = [repos['mountain/' + n] for n in ('adva', 'adva-machine', 'adva-library')]
    claims_path = 'docs/claims.toml'
    claims = tomllib.loads(adva.read(claims_path))['claim']
    claim_units = []
    for c in claims:
        u = unit(adva, claims_path, c['claim_id'], premises=c.get('assumptions'),
                 exports=[dict(claim_id=c['claim_id'], scope=c.get('scope'), status=c.get('status'))],
                 checker=dict(declared_evidence=c.get('proof_or_certificate'),
                              code_symbol=c.get('code_symbol')))
        u['revision'] = c.get('version')  # Never infer a version from an ID suffix.
        claim_units.append((u, c))
    ids = {c['claim_id']: u['documentary_id'] for u, c in claim_units}
    if len(ids) != len(claim_units):
        raise ValueError('duplicate claim ID within owning registry')
    for u, c in claim_units:
        u['dependency_edges'] = [resolve_dependency(adva, d, repos, ids) for d in c.get('dependencies', [])]
        if 'dependencies' not in c:
            u['unresolved_fields'].append('dependency declaration unavailable')
        units.append(u)
    dependency_paths = sorted({e['declared'] for u, _ in claim_units
                               for e in u['dependency_edges']
                               if e['kind'] == 'declared-file-dependency'})
    for path in dependency_paths:
        units.append(unit(adva, path, 'dependency-file'))

    # Parse constants without importing Python or executing its catalog checker.
    path = 'python/adva/math_catalog.py'
    constants = {}
    for node in ast.parse(adva.read(path)).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                constants[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    units.append(unit(adva, path, 'math-catalog-consumer', exports=['read-only math topic catalog checks'],
                      checker={'policy': constants.get('POLICY'), 'declared_limits': constants.get('LIMITS')}))
    # A source adapter over the one OperationSpec table; no parallel operation list.
    path = 'crates/adva-lisp/src/operation.rs'
    text = adva.read(path)
    builtin_version = re.search(r'pub const BUILTIN_VERSION: u32 = (\d+);', text)[1]
    blocks = re.findall(r'OperationSpec\s*\{\s*namespace:(.*?)\n\s*\}', text, re.S)
    if not blocks:
        raise ValueError('OperationSpec adapter no longer matches registry; refuse empty projection')
    for block in blocks:
        name = re.search(r'name:\s*"([^"]+)"', block)
        version = re.search(r'version:\s*(\d+|BUILTIN_VERSION)', block)
        if not name or not version:
            raise ValueError('unrecognized operation declaration')
        version_number = builtin_version if version[1] == 'BUILTIN_VERSION' else version[1]
        fields = dict(re.findall(r'(input_types|output_types|parameters|lineage_rule|surface_form):\s*([^,\n]+)', block))
        units.append(unit(adva, path, name[1] + '@' + version_number, revision=int(version_number),
                          exports=[name[1]], checker={'registry': 'OperationSpec', 'declaration': fields}))

    path = 'spec/catalog.json'
    catalog = json.loads(machine.read(path))
    for p, digest in catalog['files'].items():
        u = unit(machine, p, 'spec-catalog-file', checker={'catalog_authority': catalog['authority']})
        u['declared_sha256'] = digest
        u['integrity_match'] = digest == u['source_sha256']
        units.append(u)
    for version in (1, 2):
        path = f'spec/framework/vocabulary-v{version}.json'
        vocab = json.loads(machine.read(path))
        for term in vocab['terms']:
            units.append(unit(machine, path, term['word'], revision=vocab['version'], exports=[term],
                              checker={'source_authority': vocab['authority'], 'implementation': vocab['implementation']}))

    path = 'math/manifest.json'
    manifest = json.loads(library.read(path))
    for entry in manifest['entries']:
        u = unit(library, path, entry['key'], revision=entry.get('theory', {}).get('version'),
                 premises=entry.get('assumptions'), exports=[dict(title=entry['title'], scope=entry.get('scope'),
                                                              recorded_status=entry.get('recorded_status'))],
                 checker=entry.get('checker'), guards=entry.get('reuse_requires'))
        u['home'] = entry.get('home')
        u['unresolved_fields'].extend(entry.get('open_obligations', []))
        # Historical monorepo paths are ambiguous after the split. Preserve and
        # disclose them rather than choosing whichever repository has that file.
        u['documentary_references'] = entry.get('materials', []) + entry.get('evidence', [])
        if u['documentary_references']:
            u['unresolved_fields'].append('historical material/evidence paths lack repository/commit binding')
        units.append(u)
    path = 'index.json'
    for entry in json.loads(library.read(path))['entries']:
        u = unit(library, entry['path'], 'library-index-material', revision=entry.get('version'),
                 exports=[{'schema': entry.get('schema'), 'status': entry.get('status')}])
        u['integrity_match'] = u['source_sha256'] == entry['sha256']
        units.append(u)

    # Three bounded pilot descriptions point to existing rule/contract homes.
    # Mappings below are documentary interpretation, not new package declarations.
    pilots = [
        ('witness-rules', 'crates/adva-witness/src/witness.rs',
         'docs/research/0107-reusable-six-word-witness-kernel.md',
         ['Each child formed before composition; exact ordered endpoints', 'Exact polynomial arithmetic and fresh occurrence bindings'],
         ['Seed', 'ArithmeticTransition', 'Instantiate', 'Compose', 'Seal'],
         ['Retained concrete nonzero obligations; ZeroFault cannot be cancelled']),
        ('learning-method', 'crates/adva-witness/src/free_roundtrip.rs',
         'docs/research/0136-native-learn-guarded-roundtrip.md',
         ['Supplied recipe p=x+y*z, q=2*p; integers in [-16,16]', 'Six finite stages; earlier transitions replayed'],
         ['Bounded guarded roundtrip; interpretation free remains Proposed'],
         ['Concrete nonzero obligations and literal endpoint correspondence']),
        ('library-consumer', 'crates/adva-witness/src/library_checkpoint.rs',
         'docs/adr/0038-checked-persistent-research-library-epochs.md',
         ['Complete parent chain, maximum four epochs', 'Checker-source/dependency revisions fixed'],
         ['CheckedLibraryV0 through original load_library_v0 receiving route'],
         ['Fresh reuse checks every concrete nonzero obligation'])]
    pilot_ids = {}
    for name, path, contract, premises, exports, guards in pilots:
        machine.read(contract)
        u = unit(machine, path, name, revision='bounded research V0 (documentary mapping)',
                 premises=premises, exports=exports, guards=guards,
                 checker={'profile': 'existing bounded Rust research profile; distinct from PSC0',
                          'contract': machine.ref(contract), 'source': machine.ref(path),
                          'trusted_components': ['Rust checking source', 'JSON parser/decoder',
                                                 'exact arithmetic implementation', 'build dependencies', 'platform/configuration'],
                          'build_lock': machine.ref('Cargo.lock')})
        u['mapping_basis'] = machine.ref(contract)
        u['required_nonempty'] = ['premises', 'guards']
        machine.read('Cargo.lock')
        pilot_ids[name] = u['documentary_id']
        if name != 'witness-rules':
            u['dependency_edges'] = [dict(kind='implementation-dependency', target=pilot_ids['witness-rules'],
                                          status='documentary-source-inspection', evidence=machine.ref(path))]
        units.append(u)
    units.sort(key=lambda x: x['documentary_id'])
    for u in units:
        u['metadata_issues'] = metadata_issues(u)
    groups = {}
    for u in units:
        # Shape only: not a text/filename-based semantic equivalence claim.
        shape = (bool(u['premises']), bool(u['guards']), bool(u['checker_profile']),
                 tuple(sorted(e['kind'] for e in u['dependency_edges'])))
        groups.setdefault(str(shape), []).append(u['documentary_id'])
    candidates = [dict(shape=k, units=v, status='suggestion-only',
                       reason='Repeated documentary interface shape; inspect shared adapter/refactor opportunities',
                       semantic_equivalence='not established', admission='not granted')
                  for k, v in sorted(groups.items()) if len(v) > 1]
    return dict(schema='adva.kpb-documentary-view.v0.2', authority=AUTHORITY,
                source_commits={k: v.commit for k, v in sorted(repos.items())},
                consumer_library_pins={r.name: r.git('ls-tree', r.commit, 'adva-library').strip()
                                       for r in (adva, machine)},
                consumer_pin_boundary='Current independent checkouts do not upgrade consumer gitlinks; pinned historical consumers remain separate',
                scope='Listed registries and three pilot units; not an exhaustive package inventory',
                units=units, refactor_candidates=candidates)


def graph(view):
    lines = ['digraph documentary_dependencies {', '  rankdir=TB;',
             '  label="Documentary dependencies / reverse impact review; no admission";']
    ids = {u['documentary_id']: 'n' + str(i) for i, u in enumerate(view['units'])}
    impact = {}
    for u in view['units']:
        source = u['documentary_id']
        lines.append(f'  {ids[source]} [label={json.dumps(source)}];')
        for edge in u['dependency_edges']:
            target = edge.get('target')
            if target in ids:
                # dependency -> consumer, so reachability is potential impact.
                lines.append(f'  {ids[target]} -> {ids[source]} [label={json.dumps(edge["kind"])}];')
                impact.setdefault(target, set()).add(source)
    lines.append('}')
    closure = {}
    for origin in impact:
        seen, frontier = set(), list(impact[origin])
        while frontier:
            node = frontier.pop()
            if node not in seen:
                seen.add(node)
                frontier.extend(impact.get(node, ()))
        closure[origin] = sorted(seen)
    return '\n'.join(lines) + '\n', closure


def dependency_report(view):
    """Compact derived binding report; never read as registry input."""
    bound, unresolved = [], []
    for u in view['units']:
        for edge in u['dependency_edges']:
            record = dict(consumer=u['documentary_id'], edge=edge)
            if edge['kind'] == 'declared-file-dependency':
                bound.append(record)
            elif edge['status'] == 'unresolved':
                unresolved.append(record)
    _, impact = graph(view)
    new_sources = {record['edge']['target'] for record in bound}
    affected_consumers = {record['consumer'] for record in bound}
    shard = []
    for u in view['units']:
        if u['documentary_id'] in new_sources | affected_consumers:
            shard.append(dict(u, dependency_edges=[e for e in u['dependency_edges']
                                                   if e['kind'] == 'declared-file-dependency']))
    dot, _ = graph(dict(units=shard))
    return dict(schema='adva.kpb-documentary-dependency-bindings.v0.1',
                authority=AUTHORITY, source_commits=view['source_commits'],
                scope='Explicit path dependency bindings and still-absent exact claim IDs; not all metadata gaps',
                units_in_current_view=len(view['units']),
                dependency_records=sum(len(u['dependency_edges']) for u in view['units']),
                bound_file_dependencies=bound, unresolved_claim_dependencies=unresolved,
                binding_graph_dot=dot,
                potential_impact_review={n: impact.get(n, []) for n in sorted(new_sources)},
                semantic_boundary='Binding source bytes never discharges premises or implies equivalence/admission')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', action='append', required=True, help='mountain/name=checkout@revision')
    parser.add_argument('--report-only', action='store_true', help='Emit compact path-binding/remaining-gap report')
    args = parser.parse_args()
    repos = {}
    for value in args.repository:
        name, location = value.split('=', 1)
        root, revision = location.rsplit('@', 1)
        if name in repos:
            parser.error('duplicate repository binding')
        repos[name] = Repository(name, root, revision)
    view = build(repos)
    dot, impact = graph(view)
    view['dependency_impact_dot'] = dot
    view['potential_impact_review'] = impact
    print(json.dumps(dependency_report(view) if args.report_only else view, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
