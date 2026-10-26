"""Release publishing must refuse unexpected remote history or published assets."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
import publish_release


class PublishingGuards(unittest.TestCase):
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


if __name__=='__main__':
    unittest.main()
