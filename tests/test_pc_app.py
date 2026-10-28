"""A network error must not unlock an unrelated package build."""
import queue
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'pc'))
from app import App


class BuildState(unittest.TestCase):
    def test_only_the_build_worker_releases_its_busy_flag(self):
        app = App.__new__(App)
        app.root = None
        app.status = Mock()
        app.build_info = Mock()
        app.base_zip = Mock()
        app.base_zip.get.return_value = 'backup.zip'
        app.events = queue.Queue()
        app.local_busy = False
        completed = Mock()
        with patch('app.subprocess.run', side_effect=OSError('Builder could not start')), \
             patch('app.messagebox.showerror'):
            app.run_builder('build.py', [], completed)
            app.show_error('Unrelated Pi connection error')
            self.assertTrue(app.local_busy)
            app.events.get(timeout=3)()
        self.assertFalse(app.local_busy)
        completed.assert_not_called()
        app.status.set.assert_called_with('Builder could not start')


if __name__ == '__main__':
    unittest.main()
