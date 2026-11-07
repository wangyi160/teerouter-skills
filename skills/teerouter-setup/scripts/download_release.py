#!/usr/bin/env python3
"""Inspect/download a stable official release. Python 3.10+, standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import tempfile
import time
from urllib.parse import quote, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

PRODUCTS = {'teeproxy': ('windows-x64',), 'teemerchant': ('windows-x64', 'linux-x64')}
MAX_ARCHIVE = 512 * 1024 * 1024
MAX_METADATA = 2 * 1024 * 1024


def trusted_url(url):
    u = urlsplit(url)
    return (u.scheme == 'https' and not u.username and not u.password and u.port in (None, 443)
            and u.hostname in {'api.github.com', 'github.com', 'release-assets.githubusercontent.com',
                               'objects.githubusercontent.com'})


class GitHubRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not trusted_url(newurl):
            raise ValueError('Refusing a download redirect outside GitHub release hosts')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_url(url):
    if not trusted_url(url):
        raise ValueError('Expected an official HTTPS GitHub release URL')
    request = Request(url, headers={'User-Agent': 'teerouter-skills/0.1.0',
                                    'Accept': 'application/vnd.github+json' if urlsplit(url).hostname == 'api.github.com' else 'application/octet-stream'})
    return build_opener(GitHubRedirects()).open(request, timeout=45)


def read_small(url):
    with open_url(url) as response:
        data = response.read(MAX_METADATA + 1)
    if len(data) > MAX_METADATA:
        raise ValueError('Release metadata/checksum exceeds the size limit')
    return data


def host_target():
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine not in ('amd64', 'x86_64') or system not in ('windows', 'linux'):
        raise ValueError('No supported native release for this OS/architecture; specify --platform only for an intentional download target')
    return system + '-x64'


def asset_url(product, asset):
    url = asset.get('browser_download_url', '')
    u = urlsplit(url)
    prefix = f'/wangyi160/{product}/releases/download/'
    if (not trusted_url(url) or u.hostname != 'github.com' or not u.path.startswith(prefix)
            or u.query or u.fragment):
        raise ValueError('Asset URL does not belong to the selected official repository')
    return url


def select_asset(product, target, release):
    if target not in PRODUCTS[product]:
        raise ValueError(f'{product} has no supported {target} package')
    if release.get('draft') or release.get('prerelease'):
        raise ValueError('This helper accepts stable published releases only')
    suffix = target + ('.zip' if target.startswith('windows') else '.tar.gz')
    matches = [a for a in release.get('assets', []) if a.get('name', '').startswith(product + '-')
               and a['name'].endswith('-' + suffix)]
    if len(matches) != 1:
        raise ValueError('Expected exactly one matching archive; inspect the release assets manually')
    asset = matches[0]
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,199}', asset['name']):
        raise ValueError('Unsafe release filename')
    size = asset.get('size')
    if type(size) is not int or not 0 < size <= MAX_ARCHIVE:
        raise ValueError('Archive size is missing or outside the supported limit')
    asset_url(product, asset)
    return asset


def expected_digest(product, release, asset):
    digest = asset.get('digest')
    if digest:
        if not re.fullmatch(r'sha256:[0-9a-fA-F]{64}', digest):
            raise ValueError('Unsupported GitHub asset digest')
        return digest[7:].lower(), 'github-asset-digest'
    names = (asset['name'] + '.sha256', 'SHA256SUMS.txt', 'SHA256SUMS')
    for name in names:
        candidates = [a for a in release.get('assets', []) if a.get('name') == name]
        if len(candidates) != 1:
            continue
        text = read_small(asset_url(product, candidates[0])).decode('utf-8-sig')
        values = []
        for line in text.splitlines():
            match = re.fullmatch(r'([0-9a-fA-F]{64})\s+\*?(.+)', line.strip())
            if match and match[2].removeprefix('./') == asset['name']:
                values.append(match[1].lower())
        if len(values) == 1:
            return values[0], 'release-checksum:' + name
    raise ValueError('No unambiguous SHA-256 checksum; do not run an unverified download')


def file_digest(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def download(product, asset, expected, directory):
    directory = Path(directory).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / asset['name']
    if destination.exists() or destination.is_symlink():
        if destination.is_symlink() or not destination.is_file():
            raise ValueError('Refusing an existing non-regular destination')
        if destination.stat().st_size != asset['size'] or file_digest(destination) != expected:
            raise ValueError('An existing archive differs; choose another download directory')
        return destination, True
    descriptor, temporary = tempfile.mkstemp(prefix='.teerouter-download-', suffix='.part', dir=directory)
    temporary = Path(temporary)
    try:
        digest = hashlib.sha256()
        total = 0
        started = last_progress = time.monotonic()
        print(f"Downloading {asset['name']} ({asset['size']} bytes)", file=sys.stderr, flush=True)
        with os.fdopen(descriptor, 'wb') as output, open_url(asset_url(product, asset)) as response:
            while True:
                if time.monotonic() - started > 600:
                    raise ValueError('Download exceeded 10 minutes; retry explicitly after checking the connection')
                block = response.read1(64 * 1024)
                if not block:
                    break
                total += len(block)
                if total > asset['size'] or total > MAX_ARCHIVE:
                    raise ValueError('Download exceeds its declared size')
                output.write(block)
                digest.update(block)
                if time.monotonic() - last_progress >= 10:
                    print(f"Downloaded {total}/{asset['size']} bytes", file=sys.stderr, flush=True)
                    last_progress = time.monotonic()
        if total != asset['size'] or digest.hexdigest() != expected:
            raise ValueError('Download size or SHA-256 mismatch; archive not published')
        # Exclusive creation also works on portable FAT/exFAT drives.
        created = False
        try:
            with destination.open('xb') as output:
                created = True
                with temporary.open('rb') as source:
                    shutil.copyfileobj(source, output)
        except BaseException:
            if created:
                destination.unlink(missing_ok=True)
            raise
        return destination, False
    finally:
        temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('product', choices=PRODUCTS)
    parser.add_argument('--platform', choices=('windows-x64', 'linux-x64'))
    parser.add_argument('--version', default='latest', help='latest or a stable release tag, e.g. v0.22.4')
    parser.add_argument('--download', metavar='DIRECTORY', help='Download and verify; otherwise only inspect metadata')
    args = parser.parse_args(argv)
    target = args.platform or host_target()
    if target not in PRODUCTS[args.product]:
        raise ValueError(f'{args.product} has no supported {target} package')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}', args.version):
        raise ValueError('Invalid release tag')
    api = f'https://api.github.com/repos/wangyi160/{args.product}/releases/'
    api += 'latest' if args.version == 'latest' else 'tags/' + quote(args.version, safe='')
    release = json.loads(read_small(api))
    if args.version != 'latest' and release.get('tag_name') != args.version:
        raise ValueError('Release tag differs from the requested version')
    asset = select_asset(args.product, target, release)
    digest, source = expected_digest(args.product, release, asset)
    result = {'product': args.product, 'version': release['tag_name'], 'platform': target,
              'release_url': f'https://github.com/wangyi160/{args.product}/releases/tag/' + quote(release['tag_name'], safe=''),
              'asset': asset['name'], 'bytes': asset['size'], 'url': asset_url(args.product, asset),
              'sha256': digest, 'checksum_source': source, 'downloaded': False}
    if args.download:
        archive, reused = download(args.product, asset, digest, args.download)
        result.update(downloaded=True, verified=True, reused=reused, archive=str(archive))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        # Omit raw transport exception text: it can include a proxy URL/password.
        message = str(error) if isinstance(error, ValueError) else type(error).__name__ + ': inspect network/release availability and retry explicitly'
        print(json.dumps({'error': message}), file=sys.stderr)
        sys.exit(1)
