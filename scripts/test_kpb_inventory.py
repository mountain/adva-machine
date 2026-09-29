"""Documentary negative controls, not executable KPB conformance."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from kpb_inventory import Repository, build, graph, metadata_issues


class DocumentaryControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.repos = {f'mountain/{name}': Repository(f'mountain/{name}', root if name == 'adva-machine' else root.parent / name)
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
        view = dict(units=[u('A', []), u('B', [dict(kind='declared-dependency', target='A')]),
                           u('C', [dict(kind='declared-dependency', target='B')]), u('similar-citation', [])])
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
