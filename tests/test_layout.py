"""Public archives must retain working paths after the source reorganization."""
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'maintainer'))
from package_release import PUBLIC_FILES, package


class SourceLayout(unittest.TestCase):
    def test_local_documentation_and_image_links_resolve(self):
        for name in PUBLIC_FILES:
            if not name.endswith('.md'):
                continue
            path = ROOT/name
            text = path.read_text(encoding='utf-8')
            targets = re.findall(r'\]\(([^)]+)\)', text) + re.findall(r'(?:href|src)="([^"]+)"', text)
            for target in targets:
                target = unquote(target.split('#')[0])
                if not target or urlsplit(target).scheme:
                    continue
                with self.subTest(document=name, target=target):
                    self.assertTrue((path.parent/target).exists(), target)

    def test_extracted_bundle_has_launchers_tools_and_maintainer_entrypoints(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            info = package(output/'archive')
            with zipfile.ZipFile(info['zip']) as archive:
                self.assertEqual(set(archive.namelist()), {'seedsow-lua-editor/'+n for n in PUBLIC_FILES})
                archive.extractall(output/'extracted')
                for name in PUBLIC_FILES:
                    if name.endswith('.jpg'):
                        self.assertEqual(archive.read('seedsow-lua-editor/'+name), (ROOT/name).read_bytes())
            extracted = output/'extracted/seedsow-lua-editor'
            self.assertIn('pc\\app.py', (extracted/'START WINDOWS.cmd').read_text())
            self.assertTrue((extracted/'pi/install.sh').is_file())
            scripts = ('editor/build.py', 'editor/build_side_editor.py',
                       'maintainer/package_save.py', 'maintainer/package_release.py',
                       'maintainer/publish_release.py', 'maintainer/check_starter.py')
            for script in scripts:
                with self.subTest(script=script):
                    result = subprocess.run([sys.executable, str(extracted/script), '--help'],
                                            cwd=temp, capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)
            # A distributed archive can itself produce a complete source archive.
            subprocess.run([sys.executable, str(extracted/'maintainer/package_release.py'),
                            '--output', str(output/'repacked')], cwd=temp,
                           check=True, capture_output=True, timeout=30)


if __name__ == '__main__':
    unittest.main()
