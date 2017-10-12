import hashlib
import json
import math
import os
import subprocess
import time
import urllib2
from string import Template

TOP_DIR = os.path.dirname(__file__)
OSASCRIPT = os.path.join(TOP_DIR, 'SpotifyNowPlaying.js')
CACHE_DIR = os.path.expanduser('~/.cache/SpotifyNowPlaying')
ARTWORK = os.path.join(CACHE_DIR, 'Artwork.jpg')
ARTWORK_SUM = os.path.join(CACHE_DIR, 'Artwork.sha1sum')
ARTWORK_DEFAULT = os.path.join(TOP_DIR, 'DefaultArtwork', 'DefaultArtwork.png')
HTML_TEMPLATE = os.path.join(TOP_DIR, 'template.html')
FONT_FILE = os.path.join(CACHE_DIR, 'Open_Sans.ttf')
FONT_URL = 'https://fonts.gstatic.com/s/opensans/v15/cJZKeOuBrn4kERxqtaUH3aCWcynf_cDxXwCLxiixG1c.ttf'
FONT_SUM = '92d652578c531e2c3d9db4622584f6a1ab2c225a'


def get_html_template():
    with open(HTML_TEMPLATE, 'rb') as fp:
        return fp.read()


def get_spotify_now_playing():
    r = json.loads(subprocess.check_output(['/usr/bin/osascript', '-l', 'JavaScript', OSASCRIPT]))
    return r


def get_cached_checksum():
    try:
        with open(ARTWORK_SUM, 'rb') as fp:
            return fp.read()
    except IOError:
        return ""


def create_cache_dir():
    if not os.path.isdir(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def get_font_file():
    try:
        mtime = os.path.getmtime(FONT_FILE)
        if time.time() - mtime < 86400:
            return
    except OSError:
        pass

    # File is older than 1 day or doesn't exist. Checksum it if it exists.
    try:
        with open(FONT_FILE, 'rb') as fp:
            cksum = hashlib.sha1(fp.read()).hexdigest()
            if cksum == FONT_SUM:
                os.utime(FONT_FILE, None)
                return
    except IOError:
        pass

    create_cache_dir()

    with open(FONT_FILE, 'wb') as fp:
        response = urllib2.urlopen(FONT_URL)
        data = response.read()
        fp.write(data)


def update_artwork(artwork_url):
    create_cache_dir()

    if artwork_url:
        previous_sum = get_cached_checksum()
        current_sum = hashlib.sha1(artwork_url).hexdigest()

        if previous_sum == current_sum:
            return

        with open(ARTWORK, 'wb') as artwork:
            response = urllib2.urlopen(artwork_url)
            img_data = response.read()
            artwork.write(img_data)

        with open(ARTWORK_SUM, 'wb') as checksum:
            checksum.write(current_sum)


def format_time(time_int):
    if time_int > 1000:
        time_int = time_int / 1000

    minutes = math.floor(time_int / 60)
    seconds = math.floor(time_int % 60)

    return '%d:%02d' % (minutes, seconds)


def main():
    dat = get_spotify_now_playing()

    if not dat['running']:
        return ""

    if 'artwork_url' in dat:
        artwork_uri = 'file://' + ARTWORK
        update_artwork(dat['artwork_url'])
    else:
        artwork_uri = 'file://' + ARTWORK_DEFAULT

    dat['player_position'] = format_time(dat['player_position'])
    dat['duration'] = format_time(dat['duration'])

    get_font_file()

    template = get_html_template()
    return Template(template).safe_substitute(
        artwork_uri=artwork_uri,
        font_file='font://' + FONT_FILE,
        **dat
    )


def timing():
    import timeit
    n = 10
    print 'Seconds per iteration:', timeit.timeit('main()', setup='from __main__ import main', number=n) / n


if __name__ == '__main__':
    print main().encode('utf-8')
