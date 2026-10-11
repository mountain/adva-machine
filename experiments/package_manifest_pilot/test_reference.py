"""Offline exact-reference controls with fresh project-original Git fixtures."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from check_manifest import encode_report
from lookup_reference import lookup


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root/'repo'; self.repo.mkdir()
        def git(*args):
            return subprocess.check_output(['git','-C',str(self.repo),*args], stderr=subprocess.DEVNULL).decode().strip()
        git('init','-q')
        (self.repo/'note.txt').write_text('Original reference fixture.\n')
        (self.repo/'large.txt').write_bytes(b'x'*65537)
        git('add','note.txt','large.txt')
        git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Original bounded fixture')
        self.commit = git('rev-parse','HEAD')
        self.ref = {'repository':'example/library','commit':self.commit,'path':'note.txt'}
        self.reference = self.root/'reference.json'

    def check(self, expected, code=None, seconds=2):
        self.reference.write_text(json.dumps(self.ref))
        result = lookup(self.reference,'example/library',self.commit,self.repo,seconds)
        self.assertEqual(result['status'],expected,result)
        if code: self.assertEqual(result['reason_code'],code,result)
        self.assertEqual(result['native_admission'],'NotGranted')
        self.assertEqual(result['semantic_verification'],'NotRun')
        self.assertLessEqual(len(encode_report(result)),8192)
        return result

    def test_exact_blob_ignores_dirty_worktree(self):
        (self.repo/'note.txt').write_text('Dirty unrelated bytes')
        r=self.check('ReferenceBytesLocated','Located')
        self.assertEqual(r['sha256'],hashlib.sha256(b'Original reference fixture.\n').hexdigest())
        self.assertEqual(r['account']['git_calls'],3)

    def test_matching_digest(self):
        self.ref['sha256']=hashlib.sha256(b'Original reference fixture.\n').hexdigest()
        self.check('ReferenceBytesLocated')

    def test_missing_path(self):
        self.ref['path']='absent.txt'
        self.check('Unknown','Unavailable')

    def test_missing_commit(self):
        self.commit='0'*40; self.ref['commit']=self.commit
        self.check('Unknown','Unavailable')

    def test_foreign_repository(self):
        self.ref['repository']='other/library'
        self.check('Rejected','UnsupportedRepository')

    def test_incompatible_revision(self):
        self.ref['commit']='0'*40
        self.check('Rejected','IncompatibleRevision')

    def test_digest_mismatch(self):
        self.ref['sha256']='0'*64
        self.check('Rejected','IncompatibleDigest')

    def test_branch_not_immutable(self):
        self.ref['commit']='main'
        self.check('Rejected','UnsupportedReference')

    def test_path_escape(self):
        self.ref['path']='../note.txt'
        self.check('Rejected','UnsupportedReference')

    def test_unsupported_url(self):
        self.ref={'url':'https://example.invalid/file'}
        self.check('Rejected','UnsupportedReference')

    def test_byte_exhaustion(self):
        self.ref['path']='large.txt'
        self.check('Unknown','BudgetExhausted')

    def test_time_exhaustion(self):
        self.check('Unknown','BudgetExhausted',seconds=-1)

    def test_tree_is_not_blob(self):
        (self.repo/'folder').mkdir(); (self.repo/'folder'/'x').write_text('Original')
        subprocess.check_call(['git','-C',str(self.repo),'add','folder'])
        subprocess.check_call(['git','-C',str(self.repo),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','Folder fixture'])
        self.commit=subprocess.check_output(['git','-C',str(self.repo),'rev-parse','HEAD']).decode().strip()
        self.ref.update(commit=self.commit,path='folder')
        self.check('Rejected','UnsupportedReference')

    def test_git_network_and_replacements_disabled(self):
        real_run=subprocess.run
        with patch('lookup_reference.subprocess.run',wraps=real_run) as calls:
            self.check('ReferenceBytesLocated')
            for call in calls.call_args_list:
                command=call.args[0]
                self.assertIn('--no-lazy-fetch',command)
                self.assertIn('--no-replace-objects',command)
                self.assertIn('protocol.allow=never',command)
                self.assertEqual(call.kwargs['env']['GIT_NO_LAZY_FETCH'],'1')

    def test_old_git_is_explicitly_unknown(self):
        response=subprocess.CompletedProcess([],129,b'',b'unknown option: --no-lazy-fetch')
        with patch('lookup_reference.subprocess.run',return_value=response):
            self.check('Unknown','UnsupportedToolchain')

    def test_no_success_flag(self):
        self.ref['Verified']=True
        self.check('Rejected','UnsupportedReference')


if __name__=='__main__': unittest.main(verbosity=2)
