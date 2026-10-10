"""Original finite controls; no native semantic claims. Unknown v0.3."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from check_manifest import encode_report, lint

EXAMPLE = json.loads(Path(__file__).with_name('library-only.example.json').read_text())


class ManifestTests(unittest.TestCase):
    def run_case(self, value, expected='Rejected', **kwargs):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.json'
            path.write_text(value if isinstance(value, str) else json.dumps(value))
            result = lint(path, **kwargs)
            self.assertEqual(result['status'], expected, result)
            self.assertEqual(result['native_admission'], 'NotGranted')
            self.assertEqual(result['semantic_verification'], 'NotRun')
            self.assertLessEqual(len(encode_report(result)), 8192)
            return result

    def test_two_paths_share_material_without_duplication(self):
        r = self.run_case(EXAMPLE, 'MetadataConsistent')
        self.assertEqual(r['documentary_content_count'], 4)
        self.assertEqual(r['trail_count'], 2)
        self.assertEqual(r['account']['trail_step_checks'], 7)

    def test_reordered_narrative_not_execution(self):
        p = copy.deepcopy(EXAMPLE)
        p['trails'][0]['steps'].reverse()
        self.run_case(p, 'MetadataConsistent')

    def test_associative_cycle_allowed(self):
        p = copy.deepcopy(EXAMPLE)
        p['relations'].append({'kind':'associative','from':'cost','to':'question'})
        self.run_case(p, 'MetadataConsistent')

    def test_duplicate_json_keys(self):
        self.run_case('{"schema": "x", "schema": "y"}')

    def test_forged_top_level_authority(self):
        p = copy.deepcopy(EXAMPLE); p['Verified'] = True
        self.run_case(p)

    def test_required_extension_unknown(self):
        p = copy.deepcopy(EXAMPLE); p['extensions'][0]['required'] = True
        self.run_case(p, 'Unknown')

    def test_optional_extension_not_authority(self):
        p = copy.deepcopy(EXAMPLE); p['extensions'][0]['data']['Verified'] = True
        self.run_case(p, 'MetadataConsistent')

    def test_unsupported_declared_capability_unknown(self):
        for kind in ['compute', 'verify']:
            p = copy.deepcopy(EXAMPLE); p['capabilities'][0]['kind'] = kind
            self.run_case(p, 'Unknown')

    def test_actual_execution_requests_refused(self):
        for request in ['compute', 'verify']:
            self.run_case(EXAMPLE, requested=request)

    def test_no_capability(self):
        p = copy.deepcopy(EXAMPLE); p['capabilities'] = []
        self.run_case(p)

    def test_multiple_capabilities_have_no_automatic_receiver(self):
        p = copy.deepcopy(EXAMPLE)
        p['capabilities'].append({**p['capabilities'][0], 'kind':'verify'})
        self.run_case(p, 'Unknown')

    def test_duplicate_capability(self):
        p = copy.deepcopy(EXAMPLE); p['capabilities'] *= 2
        self.run_case(p)

    def test_unknown_schema(self):
        p = copy.deepcopy(EXAMPLE); p['schema'] += '-next'
        self.run_case(p)

    def test_depth_exhausted_shape(self):
        p = copy.deepcopy(EXAMPLE)
        value = {}
        for _ in range(33): value = {'nested':value}
        p['extensions'][0]['data'] = value
        self.run_case(p)

    def test_unknown_profile(self):
        p = copy.deepcopy(EXAMPLE); p['capabilities'][0]['profile'] += '-next'
        self.run_case(p, 'Unknown')

    def test_dangling_targets(self):
        for field in ['relations', 'trails']:
            p = copy.deepcopy(EXAMPLE)
            if field == 'relations': p[field][0]['to'] = 'missing'
            else: p[field][0]['steps'][0] = 'missing'
            self.run_case(p)

    def test_annotation_type(self):
        p = copy.deepcopy(EXAMPLE); p['relations'][2]['from'] = 'question'
        self.run_case(p)

    def test_dependency_edges_refused(self):
        for kind in ['computation-dependency', 'proof-premise']:
            p = copy.deepcopy(EXAMPLE); p['relations'][0]['kind'] = kind
            self.run_case(p)

    def test_duplicate_content_id(self):
        p = copy.deepcopy(EXAMPLE); p['content'][1]['id'] = 'question'
        self.run_case(p)

    def test_duplicate_trail_id(self):
        p = copy.deepcopy(EXAMPLE); p['trails'][1]['id'] = 'first-reading'
        self.run_case(p)

    def test_bad_branch_origin(self):
        for origin in [{'trail':'missing','step':0}, {'trail':'first-reading','step':9}]:
            p = copy.deepcopy(EXAMPLE); p['trails'][1]['origin'] = origin
            self.run_case(p)

    def test_cyclic_branch_origin(self):
        p = copy.deepcopy(EXAMPLE)
        p['trails'][0]['origin'] = {'trail':'cost-first','step':0}
        self.run_case(p)

    def test_reference_pins_and_paths(self):
        for key, value in [('commit','main'), ('path','../x'), ('path','/x')]:
            p = copy.deepcopy(EXAMPLE); p['provenance']['sources'][0][key] = value
            self.run_case(p)

    def test_bounded_cardinality(self):
        p = copy.deepcopy(EXAMPLE); p['trails'][0]['steps'] = ['question'] * 33
        self.run_case(p)

    def test_duplicate_extension(self):
        p = copy.deepcopy(EXAMPLE); p['extensions'] *= 2
        self.run_case(p)

    def test_invalid_json_and_nonfinite(self):
        for value in ['{', 'NaN', 'Infinity', '[]', 'null']:
            self.run_case(value)

    def test_input_bytes_limit(self):
        self.run_case(' ' * 65537, 'Unknown')

    def test_exhaustion_unknown_retains_spent(self):
        r = self.run_case(EXAMPLE, 'Unknown', deadline_seconds=-1)
        self.assertGreater(r['account']['bytes_read'], 0)

    def test_missing_bytes_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            r = lint(Path(d) / 'absent')
        self.assertEqual(r['status'], 'Unknown')
        self.assertEqual(r['native_admission'], 'NotGranted')

    def test_repeat_is_new_lint_not_cache_authority(self):
        a = self.run_case(EXAMPLE, 'MetadataConsistent')
        b = self.run_case(EXAMPLE, 'MetadataConsistent')
        self.assertEqual(a['account']['bytes_read'], b['account']['bytes_read'])
        self.assertEqual(a['account']['parse_calls'], b['account']['parse_calls'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
