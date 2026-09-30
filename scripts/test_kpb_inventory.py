"""Documentary negative controls, not executable KPB conformance."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from kpb_inventory import Repository, build, graph, metadata_issues, resolve_dependency, dependency_report


class DocumentaryControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        pins = {'adva': '3287c61ab7d16253605b3d0cca818f5a698e258b',
                'adva-machine': 'acfc9806fe18a36d0f7194dcc196a380b2834adf',
                'adva-library': '19cede9c4532b7abd85f200daf7a9611a84563f0'}
        cls.repos = {f'mountain/{name}': Repository(f'mountain/{name}', root if name == 'adva-machine' else root.parent / name, pins[name])
                     for name in ('adva', 'adva-machine', 'adva-library')}
        cls.view = build(cls.repos)

    def test_B04_same_export_different_packages_and_versions(self):
        terms = [u for u in self.view['units'] if u['selector'] == 'communicate']
        self.assertEqual(len(terms), 2)
        self.assertNotEqual(terms[0]['documentary_id'], terms[1]['documentary_id'])
        operations = [u for u in self.view['units'] if u['selector'].startswith('constant@')]
        self.assertEqual({u['revision'] for u in operations}, {1, 2})
        # Identical bytes/exports across repositories still have different coordinates.
        with tempfile.TemporaryDirectory() as temp:
            for name in ('one', 'two'):
                root = Path(temp) / name
                root.mkdir()
                subprocess.run(['git', 'init', '-q', str(root)], check=True)
                (root / 'registry.json').write_text('{"export":"same"}')
                subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
                subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                                'commit', '-qm', 'original synthetic fixture'], check=True)
            from kpb_inventory import unit
            a, b = [unit(Repository('fixture/' + n, Path(temp) / n), 'registry.json', 'same', exports=['same']) for n in ('one', 'two')]
            self.assertEqual(a['source_sha256'], b['source_sha256'])
            self.assertNotEqual(a['documentary_id'], b['documentary_id'])

    def test_B06_deleted_premise_guard_and_forged_success(self):
        original = next(u for u in self.view['units'] if u['selector'] == 'witness-rules')
        self.assertEqual(metadata_issues(original), [])
        for field in ('premises', 'guards'):
            for value, expected in ((None, 'unavailable:' + field), ([], 'invalid:deleted ' + field)):
                candidate = copy.deepcopy(original)
                candidate[field] = value
                self.assertIn(expected, metadata_issues(candidate))
        candidate = dict(original, verified=True, native_admission=True)
        self.assertIn('invalid:untrusted success/admission flag', metadata_issues(candidate))

    def test_impact_excludes_citations_and_similarity(self):
        u = lambda n, edges: dict(documentary_id=n, dependency_edges=edges)
        view = dict(units=[u('A', []), u('B', [dict(kind='declared-dependency', target='A', status='resolved-metadata')]),
                           u('C', [dict(kind='declared-dependency', target='B', status='resolved-metadata')]), u('similar-citation', [])])
        dot, impact = graph(view)
        self.assertEqual(impact['A'], ['B', 'C'])
        self.assertNotIn('similar-citation', impact['A'])

    def test_repeatable_complete_coordinates_no_admission(self):
        self.assertEqual(self.view, build(self.repos))
        ids = [u['documentary_id'] for u in self.view['units']]
        self.assertEqual(len(ids), len(set(ids)))
        for u in self.view['units']:
            self.assertRegex(u['full_commit'], '^[a-f0-9]{40}$')
            self.assertIn('no native admission', u['authority_boundary'])
            self.assertIn('unresolved_fields', u)

    def test_explicit_local_path_bound_to_exact_source_and_impact(self):
        report = dependency_report(self.view)
        self.assertEqual(len(report['bound_file_dependencies']), 39)
        self.assertEqual(len(report['unresolved_claim_dependencies']), 2)
        by_id = {u['documentary_id']: u for u in self.view['units']}
        for record in report['bound_file_dependencies']:
            edge = record['edge']
            target = by_id[edge['target']]
            self.assertEqual(target['repository'], 'mountain/adva')
            self.assertEqual(edge['declared'], target['path'])
            self.assertEqual(edge['source_sha256'], target['source_sha256'])
            self.assertIn(record['consumer'], report['potential_impact_review'][edge['target']])
            self.assertIsNone(target['exports'])

    def test_missing_source_never_falls_back_to_other_repo_or_alias(self):
        path = 'docs/research/0244-proposal-three-the-pyritohedral-constellation-the-entry-window-and-a-transport-defect-disclosed.md'
        self.repos['mountain/adva'].read(path)  # Other repository really has it.
        edge = resolve_dependency(self.repos['mountain/adva-machine'], path, self.repos, {})
        self.assertEqual(edge['status'], 'unresolved')
        self.assertNotIn('target', edge)
        for missing in ('adva.bounded-experiment.leak-wall.v0', 'adva.exact.structural-forward-differential.v1'):
            edge = resolve_dependency(self.repos['mountain/adva'], missing, self.repos, {})
            self.assertEqual(edge['status'], 'unresolved')
            self.assertNotIn('target', edge)

    def test_dirty_worktree_does_not_change_projection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'x').write_text('original')
            subprocess.run(['git', '-C', str(root), 'add', 'x'], check=True)
            subprocess.run(['git', '-C', str(root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                            'commit', '-qm', 'fixture'], check=True)
            repo = Repository('fixture', root)
            (root / 'x').write_text('modified')
            self.assertEqual(repo.read('x'), 'original')
            with self.assertRaises(ValueError):
                repo.read('../x')


if __name__ == '__main__':
    unittest.main()
