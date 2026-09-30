"""Finite G1 documentary controls. These are not executable KPB conformance.

Original fixtures and tests by dot (OpenAI), under Unknown v0.3.
"""
import copy
import hashlib
import json
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from architecture_projection import (AuditedRepository, Budget, CAPABILITIES, Incomplete,
    encode_report, impact_graph, project_units, run, source_manifest, typed_edges,
    validate_statuses)
from kpb_inventory import Repository, build, graph, metadata_issues, resolve_dependency

ROOT = Path(__file__).resolve().parents[1]
PINS = {'adva': '3287c61ab7d16253605b3d0cca818f5a698e258b',
        'adva-machine': 'acfc9806fe18a36d0f7194dcc196a380b2834adf',
        'adva-library': '19cede9c4532b7abd85f200daf7a9611a84563f0'}
BINDINGS = {'mountain/' + n: (ROOT if n == 'adva-machine' else ROOT.parent / n, pin)
            for n, pin in PINS.items()}


def fixture_repo(root):
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    (root / 'folder').mkdir()
    (root / 'folder/a').write_bytes(b'valid exact source\n')
    (root / 'binary').write_bytes(b'\xff\x00')
    subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture',
                    '-c', 'user.email=fixture@example.invalid', 'commit', '-qm',
                    'project-original synthetic fixture'], check=True)


class ProjectionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.budget = Budget()
        cls.repos = {n: AuditedRepository(n, root, ref, cls.budget) for n, (root, ref) in BINDINGS.items()}
        cls.view = build(cls.repos)
        cls.records = project_units(cls.view, cls.repos, Budget(), 'test-attempt')
        cls.edges = typed_edges(cls.view, cls.records, Budget())
        cls.report = run(BINDINGS)

    def test_valid_pinned_projection_preserves_counts(self):
        self.assertEqual(self.report['status'], 'CompleteWithinDeclaredView')
        self.assertEqual(self.report['binding_summary'], dict(records=324, dependencies=348,
                                                             exact_documentary_bindings=346, unresolved=2))
        self.assertEqual(self.report['source_commits'], {n: p for n, (_, p) in BINDINGS.items()})

    def test_N01_mismatch_is_conflict_and_no_impact_edge(self):
        view = copy.deepcopy(self.view)
        unit = next(u for u in view['units'] if u['selector'] == 'witness-rules')
        unit['source_sha256'] = '0' * 64
        records = project_units(view, self.repos, Budget(), 'digest-negative')
        row = next(r for r in records if r['source']['documentary_id'] == unit['documentary_id'])
        self.assertEqual(row['statuses']['binding']['value'], 'Mismatch')
        self.assertEqual(row['statuses']['provenance']['value'], 'Conflict')
        self.assertEqual(row['permitted_uses'], [])
        related = [e for e in typed_edges(view, records, Budget()) if e['dependency'] and
                   e['dependency']['coordinate']['documentary_id'] == unit['documentary_id']]
        self.assertTrue(related)
        self.assertTrue(all(e['status'] == 'Conflict' and not e['propagates_review'] for e in related))

    def test_N01_catalog_mismatch_rejected_by_both_interfaces(self):
        unit = dict(self.view['units'][0], integrity_match=False)
        self.assertIn('invalid:source digest mismatch', metadata_issues(unit))
        row = project_units(dict(units=[unit]), self.repos, Budget(), 'catalog-negative')[0]
        self.assertEqual(row['statuses']['binding']['value'], 'Mismatch')

    def test_N02_missing_declarations_not_fabricated(self):
        gaps = self.report['unresolved_dependencies']
        self.assertEqual({e['declared_reference'] for e in gaps},
                         {'adva.bounded-experiment.leak-wall.v0', 'adva.exact.structural-forward-differential.v1'})
        self.assertTrue(all(e['dependency'] is None and e['status'] == 'Unresolved' and not e['propagates_review'] for e in gaps))

    def test_N03_same_export_and_separate_versions_not_identified(self):
        rows = [r for r in self.records if r['source']['selector'] == 'communicate']
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0]['record_id'], rows[1]['record_id'])
        self.assertNotEqual(rows[0]['source'], rows[1]['source'])
        self.assertTrue(all(r['package']['coordinate'] is None for r in rows))

    def test_N04_all_claim_conditions_preserved_exactly(self):
        raw = self.repos['mountain/adva'].read('docs/claims.toml')
        claims = {c['claim_id']: c for c in tomllib.loads(raw)['claim']}
        rows = [r for r in self.records if r['source']['repository'] == 'mountain/adva' and
                r['source']['path'] == 'docs/claims.toml']
        self.assertEqual(len(rows), 221)
        for row in rows:
            c = claims[row['source']['selector']]
            self.assertEqual(row['premises'], c['assumptions'])
            for field in ('assumptions', 'counterexample_boundary', 'forbidden_conflations'):
                self.assertEqual(row['source_conditions'][field], c[field])
            self.assertIsNone(row['occurrence_bindings'])
            self.assertTrue(any('occurrence' in r for r in row['residuals']))

    def test_N04_deleting_source_premise_is_rejected(self):
        original = next(u for u in self.view['units'] if u['path'] == 'docs/claims.toml')
        for value in (None, []):
            unit = dict(original, premises=value)
            with self.assertRaisesRegex(ValueError, 'premise differs'):
                project_units(dict(units=[unit]), self.repos, Budget(), 'premise-negative')

    def test_N04_missing_guard_retained_as_gap(self):
        original = next(u for u in self.view['units'] if u['selector'] == 'witness-rules')
        for value in (None, []):
            row = project_units(dict(units=[dict(original, guards=value)]), self.repos, Budget(), 'guard-negative')[0]
            self.assertTrue(any('guards' in r for r in row['residuals']))
            self.assertEqual(row['statuses']['interpretation']['value'], 'NotRun')

    def test_N05_N09_no_promoting_receipt_ack_listed_to_admission(self):
        states = self.records[0]['statuses']
        for field, value in [('documentary_acceptance', 'AcceptedDocumentary'), ('reply_observation', 'Acknowledged'),
                             ('registration', 'Listed'), ('interpretation', 'ScopedInterpretationChecked'),
                             ('native_admission', 'GrantedForProfile')]:
            changed = copy.deepcopy(states)
            changed[field]['value'] = value
            with self.assertRaisesRegex(ValueError, 'unsupported status promotion'):
                validate_statuses(changed)
        self.assertEqual(states['interpretation']['value'], 'NotRun')
        self.assertEqual(states['native_admission']['value'], 'NotGranted')

    def test_N05_status_observations_have_context(self):
        for record in self.records:
            validate_statuses(record['statuses'])
            for row in record['statuses'].values():
                self.assertEqual(row['input_pins'], [record['source']])
                self.assertTrue(row['observer'])
                self.assertEqual(row['attempt'], 'test-attempt')
                self.assertTrue(row['residuals'])

    def test_N09_N14_forged_native_verification_rejected(self):
        for flag in ('verified', 'native_admission'):
            unit = dict(self.view['units'][0], **{flag: True})
            with self.assertRaisesRegex(ValueError, 'untrusted semantic/native'):
                project_units(dict(units=[unit]), self.repos, Budget(), 'forged-flag')

    def test_N10_consumer_locks_retain_original_bytes(self):
        locks = self.report['consumer_locks']
        self.assertEqual(len(locks), 2)
        for row in locks:
            source = row['source']
            raw = self.repos[source['repository']].read(source['path'])
            self.assertEqual(row['declaration'], json.loads(raw))
            self.assertEqual(source['source_sha256'], hashlib.sha256(raw.encode()).hexdigest())
        serialized = json.dumps(locks)
        self.assertIn('e62d88dcc83fc4967260866518029942b9631b71', serialized)
        self.assertIn('73a6af4ac4ed8225366d3c16794e309cff15f51d', serialized)
        self.assertTrue(all(r['statuses']['adoption']['value'] == 'NotAdopted' for r in self.records))

    def test_N15_no_silent_library_home_replacement(self):
        original = next(u for u in self.view['units'] if u['path'] == 'math/manifest.json' and u.get('home'))
        with self.assertRaisesRegex(ValueError, 'material home differs'):
            project_units(dict(units=[dict(original, home='new-site/elsewhere')]), self.repos, Budget(), 'home-negative')
        row = project_units(dict(units=[original]), self.repos, Budget(), 'home-positive')[0]
        self.assertEqual(row['home'], original['home'])

    def test_N04_library_guard_premise_residual_deletion_rejected(self):
        original = next(u for u in self.view['units'] if u['path'] == 'math/manifest.json' and
                        u['selector'] == 'arithmetic-golden-ratio-receipt-calibration')
        for field in ('premises', 'guards'):
            with self.assertRaisesRegex(ValueError, 'library premise/guard'):
                project_units(dict(units=[dict(original, **{field: []})]), self.repos, Budget(), 'library-negative')
        with self.assertRaisesRegex(ValueError, 'library residual deleted'):
            project_units(dict(units=[dict(original, unresolved_fields=[])]), self.repos, Budget(), 'residual-negative')
        row = project_units(dict(units=[original]), self.repos, Budget(), 'library-positive')[0]
        self.assertEqual(row['source_conditions']['reuse_requires'], original['guards'])

    def test_N16_capabilities_remain_honest(self):
        self.assertTrue(CAPABILITIES['documentary_projection'])
        self.assertTrue(all(not v for k, v in CAPABILITIES.items() if k != 'documentary_projection'))
        self.assertTrue(all(r['registration_site']['site_snapshot'] is None for r in self.records))

    def test_manifest_all_exact_read_sources_and_no_identity_claim(self):
        sources = self.report['source_manifest']
        self.assertEqual(len(sources), len({(s['repository'], s['path']) for s in sources}))
        for item in sources:
            raw = self.repos[item['repository']].read(item['path'])
            self.assertEqual(item['bytes'], len(raw.encode()))
            self.assertEqual(item['source_sha256'], hashlib.sha256(raw.encode()).hexdigest())
            self.assertEqual(item['identity_verification'], 'NotPerformed')

    def test_N01_edge_digest_conflict_cannot_propagate(self):
        view = copy.deepcopy(self.view)
        edge = next(e for u in view['units'] for e in u['dependency_edges'] if e['kind'] == 'declared-file-dependency')
        edge['source_sha256'] = '0' * 64
        projected = typed_edges(view, self.records, Budget())
        row = next(e for e in projected if e['basis'] == edge)
        self.assertEqual(row['status'], 'Conflict')
        self.assertFalse(row['propagates_review'])

    def test_unresolved_status_with_target_cannot_propagate(self):
        view = copy.deepcopy(self.view)
        edge = next(e for u in view['units'] for e in u['dependency_edges'] if e.get('target'))
        edge['status'] = 'unresolved'
        row = next(e for e in typed_edges(view, self.records, Budget()) if e['basis'] == edge)
        self.assertEqual(row['status'], 'Unresolved')
        self.assertFalse(row['propagates_review'])

    def test_reproducible_complete_report(self):
        repeat = run(BINDINGS)
        self.assertEqual(self.report, repeat)
        self.assertEqual(encode_report(copy.deepcopy(self.report)), encode_report(copy.deepcopy(repeat)))

    def test_N08_N13_small_graph_budget_unknown(self):
        result = impact_graph(self.records, self.edges, Budget({'traversal_steps': 3}))
        self.assertEqual(result['status'], 'Unknown')
        self.assertFalse(result['complete'])
        self.assertIn('stop', result)

    def test_N08_small_node_budget_keeps_prefix_and_cost(self):
        result = run(BINDINGS, {'nodes': 1})
        self.assertEqual(result['status'], 'Unknown')
        self.assertEqual(len(result['records']), 1)
        self.assertEqual(result['resource_account']['spent']['nodes'], 1)
        self.assertTrue(result['source_manifest'])

    def test_N08_small_read_budget_unknown_and_no_retry(self):
        result = run(BINDINGS, {'source_bytes': 1})
        self.assertEqual(result['status'], 'Unknown')
        self.assertIn('source_bytes budget', result['stop']['reason'])
        self.assertEqual(result['resource_account']['spent']['source_bytes'], 0)

    def test_N08_output_budget_never_emits_full_success(self):
        result = copy.deepcopy(self.report)
        result['resource_account']['limits']['report_bytes'] = 10000
        raw = encode_report(result)
        self.assertLessEqual(len(raw), 10000)
        self.assertEqual(json.loads(raw)['status'], 'Unknown')
        self.assertNotIn('records', json.loads(raw))


class GraphControls(unittest.TestCase):
    def make(self):
        units = [dict(documentary_id=n, dependency_edges=[]) for n in ('A', 'B', 'C', 'D')]
        units[1]['dependency_edges'] = [dict(kind='declared-dependency', target='A', status='resolved-metadata')]
        units[2]['dependency_edges'] = [dict(kind='cites', target='A', status='resolved-metadata')]
        units[3]['dependency_edges'] = [dict(kind='structurally-matches', target='B', status='resolved-metadata')]
        return units

    def test_legacy_graph_excludes_real_citation_similarity_unresolved(self):
        units = self.make()
        units[0]['dependency_edges'] = [dict(kind='unknown-kind', target='D', status='resolved-metadata')]
        units[3]['dependency_edges'].append(dict(kind='declared-dependency', target='A', status='unresolved'))
        _, impact = graph(dict(units=units))
        self.assertEqual(impact, {'A': ['B']})

    def test_legacy_graph_excludes_digest_conflict(self):
        units = self.make()
        units[0]['integrity_match'] = False
        self.assertEqual(graph(dict(units=units))[1], {})

    def test_legacy_graph_edge_digest_and_coordinate_conflict(self):
        for altered in ({'source_sha256': '0' * 64}, {'target_source': {'repository': 'wrong'}}):
            units = self.make()
            units[0]['source_sha256'] = 'a' * 64
            units[1]['dependency_edges'][0].update(altered)
            self.assertEqual(graph(dict(units=units))[1], {})

    def test_N08_partial_current_origin_witnesses_retained(self):
        records = [dict(source=dict(documentary_id=n)) for n in ('A', 'B', 'C', 'D')]
        edges = [dict(edge_id=str(i), kind='source-byte-depends-on', propagates_review=True,
                      dependency=dict(coordinate=dict(documentary_id=a)),
                      consumer=dict(coordinate=dict(documentary_id=b)))
                 for i, (a, b) in enumerate([('A', 'B'), ('B', 'C'), ('C', 'D')])]
        result = impact_graph(records, edges, Budget({'traversal_steps': 18}))
        self.assertEqual(result['status'], 'Unknown')
        self.assertFalse(result['review_set_completion']['A'])
        self.assertEqual([r['consumer'] for r in result['review_sets']['A']], ['B', 'C'])
        self.assertTrue(result['scc_complete'])
        partial_scc = impact_graph(records, edges, Budget({'traversal_steps': 9}))
        self.assertFalse(partial_scc['scc_complete'])
        self.assertTrue(partial_scc['strongly_connected_components'])
        self.assertIn('partial_scc_observation', partial_scc)

    def test_N19_cycles_preserved_no_execution_and_hops_typed(self):
        records = [dict(source=dict(documentary_id=n)) for n in ('A', 'B', 'C')]
        edges = [dict(edge_id=str(i), kind='source-byte-depends-on', propagates_review=True,
                      dependency=dict(coordinate=dict(documentary_id=a)),
                      consumer=dict(coordinate=dict(documentary_id=b)))
                 for i, (a, b) in enumerate([('A', 'B'), ('B', 'A'), ('B', 'C')])]
        result = impact_graph(records, edges, Budget())
        self.assertTrue(result['complete'])
        self.assertEqual(result['cycles'], [['A', 'B']])
        self.assertEqual(next(r['edge_path'] for r in result['review_sets']['A'] if r['consumer'] == 'C'), ['0', '2'])
        self.assertFalse(CAPABILITIES['executable_loader'])


class SourceControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        fixture_repo(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_blob_exact_bytes_ignore_dirty_worktree(self):
        repo = AuditedRepository('fixture', self.root, 'HEAD', Budget())
        (self.root / 'folder/a').write_text('dirty')
        self.assertEqual(repo.read('folder/a'), 'valid exact source\n')
        self.assertEqual(len(source_manifest({'fixture': repo})), 1)

    def test_directory_is_not_a_byte_source(self):
        for cls in (Repository,):
            repo = cls('fixture', self.root)
            with self.assertRaisesRegex(ValueError, 'not a Git blob'):
                repo.read('folder')
            self.assertEqual(resolve_dependency(repo, 'folder/', {}, {})['status'], 'unresolved')
        repo = AuditedRepository('fixture', self.root, 'HEAD', Budget())
        with self.assertRaisesRegex(ValueError, 'not a blob'):
            repo.read('folder')

    def test_N02_absent_source_is_unknown_not_mismatch(self):
        repo = AuditedRepository('fixture', self.root, 'HEAD', Budget())
        with self.assertRaisesRegex(Incomplete, 'source unavailable'):
            repo.read('absent')
        self.assertEqual(repo.cache, {})

    def test_non_utf8_invalid_not_accepted(self):
        repo = AuditedRepository('fixture', self.root, 'HEAD', Budget())
        with self.assertRaises(UnicodeDecodeError):
            repo.read('binary')
        self.assertEqual(repo.cache, {})

    def test_unsafe_paths_refused(self):
        repo = AuditedRepository('fixture', self.root, 'HEAD', Budget())
        for path in ('../folder/a', '/folder/a', 'HEAD:folder/a'):
            with self.assertRaisesRegex(ValueError, 'unsafe repository path'):
                repo.read(path)

    def test_N08_timeout_unknown_preserves_spent_call(self):
        budget = Budget()
        repo = AuditedRepository('fixture', self.root, 'HEAD', budget)
        before = budget.spent['git_calls']
        with patch('architecture_projection.subprocess.check_output', side_effect=subprocess.TimeoutExpired('git', 20)):
            with self.assertRaisesRegex(Incomplete, 'Git read timeout'):
                repo.read('folder/a')
        self.assertEqual(budget.spent['git_calls'], before + 1)

    def test_N01_git_replace_cannot_substitute_pinned_bytes(self):
        original = subprocess.check_output(['git', '-C', str(self.root), 'rev-parse', 'HEAD'], text=True).strip()
        (self.root / 'folder/a').write_text('substituted bytes')
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'alternate fixture'], check=True)
        alternate = subprocess.check_output(['git', '-C', str(self.root), 'rev-parse', 'HEAD'], text=True).strip()
        subprocess.run(['git', '-C', str(self.root), 'replace', original, alternate], check=True)
        for repo in (Repository('fixture', self.root, original),
                     AuditedRepository('fixture', self.root, original, Budget())):
            self.assertEqual(repo.commit, original)
            self.assertEqual(repo.read('folder/a'), 'valid exact source\n')

    def test_N02_missing_revision_report_unknown(self):
        bindings = dict(BINDINGS, **{'mountain/adva': (self.root, '0' * 40)})
        result = run(bindings)
        self.assertEqual(result['status'], 'Unknown')
        self.assertIn('source revision unavailable', result['stop']['reason'])
        self.assertGreater(result['resource_account']['spent']['git_calls'], 0)

    def test_malformed_claim_registry_retains_refusal_and_manifest(self):
        (self.root / 'docs').mkdir()
        (self.root / 'docs/claims.toml').write_text('claim = 7\n')
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'malformed original fixture'], check=True)
        bindings = dict(BINDINGS, **{'mountain/adva': (self.root, 'HEAD')})
        result = run(bindings)
        self.assertEqual(result['status'], 'RefusedInvalidProjection')
        self.assertEqual(result['stop']['error_type'], 'TypeError')
        self.assertEqual(result['source_manifest'][0]['path'], 'docs/claims.toml')
        self.assertGreater(result['resource_account']['spent']['source_bytes'], 0)

    def test_N08_deadline_unknown_not_no_match(self):
        budget = Budget()
        budget.started -= budget.limits['wall_seconds'] + 1
        with self.assertRaisesRegex(Incomplete, 'wall-clock safety deadline'):
            budget.charge('traversal_steps')


if __name__ == '__main__':
    unittest.main()
