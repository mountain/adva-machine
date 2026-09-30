"""Project-original finite projected-ledger controls, dot (OpenAI), Unknown v0.3."""
import copy
import itertools
import io
import json
from pathlib import Path
import random
import unittest
from unittest.mock import patch

from finite_structure_match import (ALGORITHM, AUTHORITY, Budget, DIGESTS, FILES, Incomplete,
    PROFILE, canonical, compare, decode, encode_report, extract, load_package, PIN,
    read_source, run, sha, term, verify_mapping, verify_witness, main, git, LIMITS)

ROOT = Path(__file__).resolve().parents[1]


def package():
    return load_package(ROOT, 'mountain/adva-machine', PIN, 'machine', Budget())


def graph(name='copy'):
    p = package()
    f = next(f for f in p['families'] if f['name'] == name)
    return extract(f, p, Budget())


def relabel(g):
    """Change every graph handle and reverse node/edge serialization; no anchored label changes."""
    new = copy.deepcopy(g)
    mapping = {n: 'renamed:' + str(i) for i, n in enumerate(reversed(list(g['nodes'])))}
    new['nodes'] = {mapping[n]: copy.deepcopy(v) for n, v in reversed(list(g['nodes'].items()))}
    new['edges'] = [dict(e, id='renamed-edge:' + str(i), source=mapping[e['source']],
                         target=mapping[e['target']]) for i, e in enumerate(reversed(g['edges']))]
    return new


def simple_graph(n, edges):
    return dict(profile=PROFILE, nodes={str(i):dict(kind='TestVertex', labels={}, selector=str(i)) for i in range(n)},
                edges=[dict(id=str(i), source=str(a), target=str(b), label=label, selector=str(i))
                       for i, (a,b,label) in enumerate(edges)],
                source=dict(test='project-original finite control'), conditions={}, residuals=[])


class MatchingControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = package()
        cls.graphs = {f['name']: extract(f, cls.package, Budget()) for f in cls.package['families']}

    def check_mutation(self, change, name='copy'):
        a = self.graphs[name]
        b = copy.deepcopy(a)
        change(b)
        self.assertNotEqual(compare(a, b, Budget())['status'], 'StructuralMatchCandidate')

    def test_positive_all_twelve_projected_ledgers(self):
        for name, a in self.graphs.items():
            with self.subTest(name=name):
                b = relabel(a)
                r = compare(a, b, Budget())
                self.assertEqual(r['status'], 'StructuralMatchCandidate')
                self.assertTrue(verify_mapping(a, b, dict(r['witness']['nodes']), Budget()))
                self.assertEqual(len(r['witness']['edges']), len(a['edges']))
                self.assertEqual(r['authority'], AUTHORITY)
                self.assertEqual(r['witness']['unmatched_left'], [])
                self.assertEqual(r['witness']['lost_conditions'], [])

    def test_event_cut_transition_serialization_permutation(self):
        p = copy.deepcopy(self.package)
        f = next(f for f in p['families'] if f['name'] == 'copy-pending')
        n = len(f['events'])
        mapping = {i: n - 1 - i for i in range(n)}
        def mask(value):
            return sum(1 << mapping[i] for i in range(n) if value & (1 << i))
        f['events'].reverse()
        for e in f['events']:
            e['deps'] = [mapping[d] for d in reversed(e['deps'])]
        f['cuts'] = [dict(c, mask=mask(c['mask'])) for c in reversed(f['cuts'])]
        f['edges'] = [[mask(a), mask(b), mapping[e]] for a,b,e in reversed(f['edges'])]
        f['clocks'] = {k:list(reversed(v)) for k,v in f['clocks'].items()}
        b = extract(f, p, Budget())
        a = self.graphs[f['name']]
        result = compare(a, b, Budget())
        self.assertEqual(result['status'], 'StructuralMatchCandidate')
        self.assertNotEqual(result['witness']['left_graph_sha256'], result['witness']['right_graph_sha256'])
        self.assertTrue(verify_mapping(a,b,dict(result['witness']['nodes']),Budget()))

    def test_cross_repository_coordinates_do_not_become_native_identity(self):
        a = self.graphs['identity']; b = relabel(a)
        b['source'] = dict(a['source'], repository='another-receiver', commit='0'*40)
        r = compare(a,b,Budget())
        self.assertEqual(r['status'], 'StructuralMatchCandidate')
        self.assertNotEqual(r['left'], r['right'])
        self.assertEqual(r['authority']['native_admission'], 'NotGranted')

    def test_equal_final_term_does_not_erase_history(self):
        a,b = self.graphs['identity'], self.graphs['double-identity']
        self.assertEqual(a['nodes']['boundary']['labels']['normal'], b['nodes']['boundary']['labels']['normal'])
        self.assertEqual(compare(a,b,Budget())['status'], 'NoMatchWithinProfile')

    def test_changed_roles_and_pending_copy_are_negative(self):
        for a,b in [('independent-iota','changed-roles'),('copy','copy-pending')]:
            self.assertEqual(compare(self.graphs[a],self.graphs[b],Budget())['status'],'NoMatchWithinProfile')

    def test_direction(self):
        def change(g):
            e=next(e for e in g['edges'] if e['label']=='depends-before')
            e['source'],e['target']=e['target'],e['source']
        self.check_mutation(change)

    def test_multiplicity(self):
        def change(g):
            e=copy.deepcopy(g['edges'][0]); e['id']='extra'; g['edges'].append(e)
        self.check_mutation(change)

    def test_missing_dependency_transition_and_lineage(self):
        for label in ('depends-before','transition-event','copy-lineage:0:branch:0'):
            with self.subTest(label=label):
                self.check_mutation(lambda g: g['edges'].remove(next(e for e in g['edges'] if e['label']==label)))

    def test_ordered_output_and_term_path(self):
        def change(g):
            g['nodes']['boundary']['labels']['entry_roles'].reverse()
        self.check_mutation(change)
        self.check_mutation(lambda g: g['nodes']['event:0']['labels']['path'].append(1))

    def test_discard_and_anchored_occurrence(self):
        def change(g):
            next(n for n in g['nodes'].values() if n['kind']=='LedgerEvent' and n['labels']['discard'] is not None)['labels']['discard']=None
        self.check_mutation(change,'discard')
        self.check_mutation(lambda g: g['nodes']['occurrence:0']['labels'].update(occurrence='invented'))

    def test_copy_occurrences_stay_distinct(self):
        a=self.graphs['copy']
        nodes=[n for n in a['nodes'].values() if n['kind']=='ApertureOccurrence']
        self.assertEqual([n['labels']['port'] for n in nodes],[0,2,1,2])
        self.assertEqual(len({n['labels']['occurrence'] for n in nodes}),4)
        self.check_mutation(lambda g: g['nodes']['occurrence:1']['labels'].update(origin='another-source'))

    def test_conditions_and_missing_guards_never_discharged(self):
        a=self.graphs['identity']
        self.assertEqual(a['conditions']['guards']['status'],'Unavailable')
        for field in ('premises','guards','residuals','dependencies','preservation'):
            self.check_mutation(lambda g:g['conditions'].pop(field),'identity')
        self.check_mutation(lambda g:g['residuals'].clear(),'identity')

    def test_unsupported_profile_or_self_granted_rule(self):
        a=self.graphs['identity']; b=copy.deepcopy(a)
        b['profile']='invented-with-commutativity'
        with self.assertRaisesRegex(ValueError,'unsupported'):
            compare(a,b,Budget())
        b=copy.deepcopy(a); b['verified']=True
        with self.assertRaisesRegex(ValueError,'unsupported fields'):
            compare(a,b,Budget())

    def test_degree_histogram_is_not_isomorphism(self):
        a=simple_graph(6,[(i,(i+1)%6,'next') for i in range(6)])
        b=simple_graph(6,[(i, (i//3)*3+(i+1)%3,'next') for i in range(6)])
        r=compare(a,b,Budget())
        self.assertEqual(r['status'],'NoMatchWithinProfile')
        self.assertEqual(r['differences'][0]['kind'],'finite-search-exhausted-all-bijections')

    def test_independent_permutation_oracle_36_pairs(self):
        rng=random.Random(710)
        for _ in range(36):
            n=4
            a=simple_graph(n,[(i,j,'e') for i in range(n) for j in range(n) if rng.randrange(4)==0])
            b=relabel(a) if rng.randrange(2) else simple_graph(n,[(i,j,'e') for i in range(n) for j in range(n) if rng.randrange(4)==0])
            ae=sorted((e['source'],e['target'],e['label']) for e in a['edges'])
            expected=False
            for values in itertools.permutations(b['nodes']):
                m=dict(zip(a['nodes'],values))
                mapped=sorted((m[x],m[y],label) for x,y,label in ae)
                if mapped==sorted((e['source'],e['target'],e['label']) for e in b['edges']):
                    expected=True;break
            self.assertEqual(compare(a,b,Budget())['status']=='StructuralMatchCandidate',expected)

    def test_bijection_and_complete_edge_checker_reject_forgery(self):
        a=self.graphs['copy']; b=relabel(a)
        mapping=dict(compare(a,b,Budget())['witness']['nodes'])
        mapping.pop(next(iter(mapping)))
        self.assertFalse(verify_mapping(a,b,mapping,Budget()))
        mapping=dict(compare(a,b,Budget())['witness']['nodes'])
        keys=list(mapping);mapping[keys[0]]=mapping[keys[1]]
        self.assertFalse(verify_mapping(a,b,mapping,Budget()))
        b['edges'][0]['label']='forged'
        self.assertFalse(verify_mapping(a,b,dict(compare(a,relabel(a),Budget())['witness']['nodes']),Budget()))

    def test_opaque_boolean_integer_conditions_do_not_conflate(self):
        for key in ('conditions', 'residuals'):
            a=simple_graph(1,[]);b=copy.deepcopy(a)
            a[key]={'guard':True} if key=='conditions' else [True]
            b[key]={'guard':1} if key=='conditions' else [1]
            self.assertEqual(compare(a,b,Budget())['status'],'NoMatchWithinProfile')
            self.assertFalse(verify_mapping(a,b,{'0':'0'},Budget()))

    def test_malformed_edge_labels_and_records_rejected(self):
        for edge in (None, [], 1, dict(id='e',source='0',target='0',label=True,selector='')):
            a=simple_graph(1,[]);a['edges']=[edge]
            with self.assertRaises(ValueError):compare(a,a,Budget())
        a=simple_graph(1,[(0,0,'e')]);b=copy.deepcopy(a);b['edges'][0]['label']=1
        with self.assertRaises(ValueError):verify_mapping(a,b,{'0':'0'},Budget())

    def test_full_emitted_witness_rejects_forged_edges_anchors_and_digests(self):
        a=self.graphs['copy'];b=relabel(a);w=compare(a,b,Budget())['witness']
        self.assertTrue(verify_witness(a,b,w,Budget()))
        for change in (lambda x:x['edges'].pop(),lambda x:x['occurrences'].clear(),
                       lambda x:x.update(left_graph_sha256='0'*64),
                       lambda x:x['nodes'].append(x['nodes'][0]),
                       lambda x:x['unmatched_right'].append('forgotten')):
            altered=copy.deepcopy(w);change(altered)
            self.assertFalse(verify_witness(a,b,altered,Budget()))

    def test_step_exhaustion_is_unknown_with_partial_position(self):
        a=simple_graph(6,[(i,(i+1)%6,'next') for i in range(6)])
        b=relabel(a)
        r=compare(a,b,Budget(dict(steps=65)))
        self.assertEqual(r['status'],'Unknown'); self.assertFalse(r['complete'])
        self.assertTrue(r['partial_mapping']);self.assertIn('stopping_position',r)
        self.assertEqual(r,compare(a,b,Budget(dict(steps=65))))

    def test_wall_exhaustion_is_unknown(self):
        a=self.graphs['identity']; budget=Budget()
        with patch('finite_structure_match.time.monotonic',return_value=budget.started+121):
            result=compare(a,a,budget)
        self.assertEqual(result['status'],'Unknown')
        self.assertIn('nondeterministic',result['reason'])

    def test_node_edge_depth_and_invocation_limits(self):
        for key in ('nodes','edges','depth'):
            with self.subTest(key=key),self.assertRaises(Incomplete):
                extract(self.package['families'][0],self.package,Budget({key:1}))
        b=Budget(dict(comparisons=1));a=self.graphs['identity']
        self.assertEqual(compare(a,a,b)['status'],'StructuralMatchCandidate')
        self.assertEqual(compare(a,a,b)['status'],'Unknown')

    def test_malformed_and_unsupported_source_fields(self):
        for change in [lambda f:f.update(new_rule=True), lambda f:f.pop('events'),
                       lambda f:f['final_apertures'][1].update(occurrence=f['final_apertures'][0]['occurrence']),
                       lambda f:f['edges'][0].__setitem__(2,999),
                       lambda f:f['events'][0].update(before='@a')]:
            p=copy.deepcopy(self.package);f=next(f for f in p['families'] if f['name']=='copy');change(f)
            with self.assertRaises(ValueError):extract(f,p,Budget())

    def test_source_digest_mismatch_and_missing_git_object(self):
        path='knowledge/received/iota-process-machine-2026-09-17-v1/materials/interpretations.json'
        with self.assertRaisesRegex(ValueError,'binding mismatch'):
            read_source(ROOT,'mountain/adva-machine',PIN,path,'0'*64,Budget())
        with self.assertRaisesRegex(Incomplete,'unavailable'):
            read_source(ROOT,'mountain/adva-machine','0'*40,path,DIGESTS[FILES[0]],Budget())
        with self.assertRaisesRegex(ValueError,'immutable'):
            read_source(ROOT,'mountain/adva-machine','HEAD',path,DIGESTS[FILES[0]],Budget())

    def test_mid_package_cutoff_retains_observed_source_manifest(self):
        r=run(ROOT,ROOT,dict(input_bytes=31000))
        self.assertEqual(r['status'],'Unknown')
        self.assertEqual(r['budget']['spent']['input_bytes'],29903)
        self.assertEqual(len(r['sources']),1)
        self.assertEqual(r['sources'][0]['source_sha256'],DIGESTS['interpretations.json'])
        self.assertTrue(r['stopping_position'][-1].endswith('contract.json'))
        self.assertEqual(r['graphs'],[])

    def test_decode_cutoff_retains_byte_binding_without_parsed_claim(self):
        for limit in (dict(steps=1),dict(depth=1),dict(git_calls=4)):
            with self.subTest(limit=limit):
                r=run(ROOT,ROOT,limit)
                self.assertEqual(r['status'],'Unknown')
                self.assertEqual(len(r['sources']),1)
                self.assertEqual(r['sources'][0]['source_sha256'],DIGESTS['interpretations.json'])
                self.assertEqual(r['sources'][0]['commit'],PIN)
                self.assertEqual(r['graphs'],[])

    def test_byte_limit_before_json_decode(self):
        with patch('finite_structure_match.json.loads',side_effect=AssertionError('must not parse')):
            with self.assertRaises(Incomplete):decode(b'{}',Budget(dict(input_bytes=1)),'too-big')

    def test_json_duplicate_float_and_nonfinite_rejected(self):
        for raw in (b'{"a":1,"a":2}',b'{"x":1.5}',b'{"x":NaN}'):
            with self.assertRaises(ValueError):decode(raw,Budget(),'invalid')

    def test_ordered_prefix_syntax(self):
        for value in ('@','@a','a@','x',''):
            with self.assertRaises(ValueError):term(value,Budget(),'bad')
        term('@@abc',Budget(),'valid')

    def test_output_budget_retains_unknown(self):
        report=dict(sources=[],budget=Budget().record(),graphs=['x'*10000])
        r=json.loads(encode_report(report,2048))
        self.assertEqual(r['status'],'Unknown');self.assertFalse(r['complete'])
        self.assertIn('omitted_payload_sha256',r)
        with self.assertRaises(ValueError):encode_report(report,1)

    def test_cli_storage_exhaustion_returns_nonzero_unknown(self):
        report=dict(sources=[],budget=Budget().record(),graphs=['x'*10000],complete=True)
        with patch('finite_structure_match.run',return_value=report), \
             patch('sys.argv',['finite_structure_match.py','--knowledge-root','.']), \
             patch.dict(LIMITS,report_bytes=2048),patch('sys.stdout',new_callable=io.StringIO) as output:
            code=main()
        self.assertEqual(code,2)
        emitted=json.loads(output.getvalue())
        self.assertEqual(emitted['status'],'Unknown')
        self.assertEqual(emitted['budget']['spent']['report_bytes'],len(output.getvalue().encode()))

    def test_git_disables_lazy_fetch_and_optional_locks(self):
        with patch('finite_structure_match.subprocess.check_output',return_value=b'blob') as check:
            git(ROOT,['cat-file','-t','0'*40],Budget())
        self.assertEqual(check.call_args.kwargs['env']['GIT_NO_LAZY_FETCH'],'1')
        self.assertEqual(check.call_args.kwargs['env']['GIT_OPTIONAL_LOCKS'],'0')
        self.assertIn('--no-replace-objects',check.call_args.args[0])

    def test_repeatable_evidence_and_counted_cost(self):
        a=self.graphs['copy'];b=relabel(a);one,two=Budget(),Budget()
        self.assertEqual(canonical(compare(a,b,one)),canonical(compare(a,b,two)))
        self.assertEqual(one.record(),two.record())


if __name__=='__main__':unittest.main()
