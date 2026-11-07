import importlib.util
import io
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('download_release',ROOT/'skills/teerouter-setup/scripts/download_release.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)

def asset(content=b'official archive'):
    return {'name':'teeproxy-v1.0.0-windows-x64.zip','size':len(content),
            'digest':'sha256:'+hashlib.sha256(content).hexdigest(),
            'browser_download_url':'https://github.com/wangyi160/teeproxy/releases/download/v1.0.0/teeproxy-v1.0.0-windows-x64.zip'}

class DownloadTests(unittest.TestCase):
    def test_platform_and_ambiguous_archives(self):
        a=asset()
        self.assertEqual(helper.select_asset('teeproxy','windows-x64',{'assets':[a]}),a)
        for target,release in [('linux-x64',{'assets':[a]}),('windows-x64',{'assets':[a,a]}),('windows-x64',{'assets':[a],'prerelease':True})]:
            with self.assertRaises(ValueError):helper.select_asset('teeproxy',target,release)

    def test_foreign_repo_and_unsafe_filename(self):
        for change in [{'name':'../teeproxy-v1.0.0-windows-x64.zip'},
                       {'browser_download_url':'https://github.com/attacker/teeproxy/releases/download/v1/file.zip'},
                       {'browser_download_url':'http://github.com/wangyi160/teeproxy/releases/download/v1/file.zip'}]:
            with self.assertRaises(ValueError):helper.select_asset('teeproxy','windows-x64',{'assets':[dict(asset(),**change)]})
        for url in ['https://evil.example/file.zip','https://github.com.evil.example/file.zip','https://user:secret@github.com/file.zip']:
            self.assertFalse(helper.trusted_url(url))

    def test_matching_checksum_only(self):
        a=asset();expected=a.pop('digest')[7:]
        checksum={'name':'SHA256SUMS.txt','browser_download_url':'https://github.com/wangyi160/teeproxy/releases/download/v1/SHA256SUMS.txt'}
        release={'assets':[a,checksum]}
        with patch.object(helper,'read_small',return_value=(expected+'  '+a['name']+'\n').encode()):
            self.assertEqual(helper.expected_digest('teeproxy',release,a)[0],expected)
        with patch.object(helper,'read_small',return_value=(expected+'  unrelated.zip\n').encode()):
            with self.assertRaises(ValueError):helper.expected_digest('teeproxy',release,a)

    def test_verified_download_and_safe_reuse(self):
        payload=b'official archive';a=asset(payload)
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(helper,'open_url',return_value=io.BytesIO(payload)):
                path,reused=helper.download('teeproxy',a,a['digest'][7:],directory)
            self.assertFalse(reused);self.assertEqual(path.read_bytes(),payload)
            with patch.object(helper,'open_url',side_effect=AssertionError('must not download again')):
                self.assertTrue(helper.download('teeproxy',a,a['digest'][7:],directory)[1])
            path.write_bytes(b'existing different file')
            with self.assertRaises(ValueError):helper.download('teeproxy',a,a['digest'][7:],directory)
            self.assertEqual(path.read_bytes(),b'existing different file')

    def test_corrupt_or_oversized_download_is_not_published(self):
        a=asset()
        for payload in [b'x'*a['size'],b'x'*(a['size']+1),b'']:
            with tempfile.TemporaryDirectory() as directory,patch.object(helper,'open_url',return_value=io.BytesIO(payload)):
                with self.assertRaises(ValueError):helper.download('teeproxy',a,a['digest'][7:],directory)
                self.assertEqual(list(Path(directory).iterdir()),[])

if __name__=='__main__':unittest.main()
