"""Release publishing must refuse unexpected remote history or published assets."""
import sys
import struct
import tempfile
import hashlib
import os
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'maintainer'))
import publish_release
from package_save import portable_metadata


class StarterMetadata(unittest.TestCase):
    def test_jksv_layout_retains_game_sizes_and_blanks_personal_fields(self):
        data = portable_metadata()
        self.assertEqual(len(data),86)
        self.assertEqual(data[:5],b'JKSV\x01')
        self.assertEqual(struct.unpack_from('<Q',data,5)[0],0x010042D022AEA000)
        self.assertEqual(data[13:29],bytes(16))
        self.assertEqual(data[49:57],bytes(8))
        self.assertEqual(data[77:85],bytes(8))
        self.assertEqual(struct.unpack_from('<qq',data,61),(33554432,33554432))


class PublishingGuards(unittest.TestCase):
    def test_resumed_asset_requires_matching_bytes_and_completed_state(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'asset.zip'
            path.write_bytes(b'expected test asset')
            asset = {'state':'uploaded','size':path.stat().st_size,
                     'digest':'sha256:'+hashlib.sha256(path.read_bytes()).hexdigest()}
            self.assertTrue(publish_release.uploaded_asset_matches(asset,path))
            for change in ({'state':'starter'},{'size':1},{'digest':'sha256:wrong'},{'digest':None}):
                self.assertFalse(publish_release.uploaded_asset_matches(dict(asset,**change),path))

    def fake_git(self, remote, count='1'):
        local = 'a'*40
        state = {'remote':remote, 'pushes':[]}
        def run(*args,**kwargs):
            if args==('remote','get-url','origin'):return publish_release.REMOTE_URL
            if args==('status','--porcelain'):return ''
            if args==('branch','--show-current'):return 'main'
            if args==('rev-parse','HEAD'):return local
            if args==('ls-remote','origin','refs/heads/main'):return state['remote']+'\trefs/heads/main'
            if args==('rev-list','--count','HEAD'):return count
            if args==('merge-base','--is-ancestor',state['remote'],local):return ''
            if args[0]=='push':
                state['pushes'].append(args)
                state['remote']=local
                return ''
            raise AssertionError(args)
        return run,state

    def test_unexpected_remote_never_gets_force_pushed(self):
        run,state = self.fake_git('c'*40)
        with patch.object(publish_release,'git',side_effect=run), patch.object(publish_release,'credential') as credential:
            with self.assertRaisesRegex(RuntimeError,'Remote main changed'):
                publish_release.publish('b'*40)
        self.assertEqual(state['pushes'],[])
        credential.assert_not_called()

    def test_replacement_requires_single_commit_and_exact_lease(self):
        run,state = self.fake_git('b'*40,count='2')
        with patch.object(publish_release,'git',side_effect=run):
            with self.assertRaisesRegex(RuntimeError,'single-commit'):
                publish_release.publish('b'*40)
        self.assertEqual(state['pushes'],[])
        run,state = self.fake_git('b'*40)
        with patch.object(publish_release,'git',side_effect=run), patch.object(publish_release,'package',return_value={}), \
             patch.object(publish_release,'credential',side_effect=RuntimeError('stop before API')):
            with self.assertRaisesRegex(RuntimeError,'stop before API'):
                publish_release.publish('b'*40)
        self.assertEqual(len(state['pushes']),1)
        self.assertIn('--force-with-lease=refs/heads/main:'+'b'*40,state['pushes'][0])

    def test_published_release_is_not_replaced(self):
        run,state = self.fake_git('a'*40)
        with patch.object(publish_release,'git',side_effect=run), \
             patch.object(publish_release,'package',return_value={}), \
             patch.object(publish_release,'credential',return_value='dummy-test-credential'), \
             patch.object(publish_release,'request',return_value={'draft':False}) as request:
            with self.assertRaisesRegex(RuntimeError,'already published'):
                publish_release.publish()
        self.assertEqual(state['pushes'],[])
        self.assertEqual(request.call_count,1)

    def test_followup_release_uses_a_normal_push(self):
        run,state = self.fake_git('b'*40,count='3')
        with patch.object(publish_release,'git',side_effect=run), patch.object(publish_release,'package',return_value={}), \
             patch.object(publish_release,'credential',side_effect=RuntimeError('stop before API')):
            with self.assertRaisesRegex(RuntimeError,'stop before API'):
                publish_release.publish()
        self.assertEqual(state['pushes'],[('push','-u','origin','HEAD:main')])


class TaggedPublication(unittest.TestCase):
    def setUp(self):
        self.tag = 'v'+(ROOT/'VERSION').read_text().strip()
        self.head = 'a'*40
        self.env = {'GITHUB_ACTIONS':'true', 'GITHUB_REPOSITORY':publish_release.REPOSITORY,
                    'GITHUB_REF':'refs/tags/'+self.tag, 'GITHUB_SHA':self.head,
                    'GITHUB_TOKEN':'dummy-test-workflow-token'}

    def fake_git(self, *args, **kwargs):
        if args==('remote','get-url','origin'):return publish_release.REMOTE_URL
        if args==('status','--porcelain'):return ''
        if args==('rev-parse','HEAD'):return self.head
        if args==('ls-remote','origin','refs/tags/'+self.tag,'refs/tags/'+self.tag+'^{}'):
            return self.head+'\trefs/tags/'+self.tag
        if args==('merge-base','--is-ancestor',self.head,'origin/main'):return ''
        raise AssertionError('Unexpected Git operation: '+repr(args))

    def test_valid_tag_publishes_without_credentials_or_branch_push(self):
        with patch.dict(os.environ,self.env), patch.object(publish_release,'git',side_effect=self.fake_git), \
             patch.object(publish_release,'credential') as credential, \
             patch.object(publish_release,'publish_assets',return_value='published') as assets:
            self.assertEqual(publish_release.publish(ci_tag=self.tag),'published')
        credential.assert_not_called()
        assets.assert_called_once_with(self.head,'dummy-test-workflow-token')

    def test_wrong_tag_or_event_never_publishes(self):
        with patch.dict(os.environ,self.env), patch.object(publish_release,'git',side_effect=self.fake_git), \
             patch.object(publish_release,'publish_assets') as assets:
            with self.assertRaisesRegex(RuntimeError,'match VERSION'):
                publish_release.publish(ci_tag='v999.0.0')
            with patch.dict(os.environ,{'GITHUB_REF':'refs/heads/main'}):
                with self.assertRaisesRegex(RuntimeError,'matching repository tag event'):
                    publish_release.publish(ci_tag=self.tag)
            with self.assertRaisesRegex(RuntimeError,'cannot replace branch history'):
                publish_release.publish(expected_head='b'*40,ci_tag=self.tag)
        assets.assert_not_called()

    def test_remote_tag_and_main_ancestry_are_required(self):
        with patch.dict(os.environ,self.env), patch.object(publish_release,'git',return_value='b'*40+'\trefs/tags/'+self.tag):
            with self.assertRaisesRegex(RuntimeError,'Remote release tag'):
                publish_release.verify_ci_tag(self.tag,self.head)
        def unrelated(*args,**kwargs):
            if args[0]=='merge-base':raise RuntimeError('unrelated commit')
            return self.fake_git(*args,**kwargs)
        with patch.dict(os.environ,self.env), patch.object(publish_release,'git',side_effect=unrelated):
            with self.assertRaisesRegex(RuntimeError,'already on main'):
                publish_release.verify_ci_tag(self.tag,self.head)


if __name__=='__main__':
    unittest.main()
