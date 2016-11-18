#!/usr/bin/env python3
"""
Usage: ./torrent_free.py [-h] [-f] source destination

This script converts a torrent bound to a private tracker to a public torrent
with eventual trackers and webseeds associated.

Since the private flag has been removed, torrent clients should see two
different torrents (different infohashes), but be able to use the same source
files for both.

This scripts depends on the libtorrent-rasterbar library
<http://www.rasterbar.com/products/libtorrent/>.

This script is licensed under the WTFPL
<http://www.wtfpl.net/>
"""

__version__ = '1.0'
__author__ = 'Mathieu Pasquet <http://mathieui.net>'
__date__ = '27-06-2012'

import warnings
# annoying libtorrent RuntimeWarnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import libtorrent as lt

# Due to how the automated libtorrent bindings for python3 work,
# all the library takes are bytes. strings might accidentally work,
# but it’s better not to use them
TRACKERS = [
    b'udp://tracker.opentrackr.org:1337',
    b'udp://tracker.coppersurfer.tk:6969',
    b'udp://tracker.leechers-paradise.org:6969',
    b'udp://zer0day.ch:1337',
    b'udp://explodie.org:6969'
]

# If the torrent only contains one file, then the subsequent webseeds will
# be http://server/path/name_of_file.ext but if it is multifile, it will be
# http://server/path/torrent_info_name/path/to/one.file.ext, so only the root
# (http://server/path/) is needed
# http://www.getright.com/seedtorrent.html
WEBSEEDS = []

def remove_private(torrent):
    """
    Remove the private flag.
    """
    if not b'private' in torrent[b'info']:
        return False
    else:
        del torrent[b'info'][b'private']
    return True

def swap_trackers(torrent):
    """
    Replace the trackers with the ones defined before.
    """
    # replace trackers
    if TRACKERS:
        torrent[b'announce'] = TRACKERS[0]
        if len(TRACKERS) > 1:
            torrent[b'announce-list'] = []
            for tracker in TRACKERS:
                torrent[b'announce-list'].append([tracker])
    # only remove them
    elif torrent.get(b'announce') or torrent.get(b'announce-list'):
        if torrent.get(b'announce'):
            del torrent[b'announce']
        if torrent.get(b'announce-list'):
            del torrent[b'announce-list']

def swap_webseeds(torrent):
    """
    Replace the webseeds with the ones defined before.
    """
    if WEBSEEDS: # multi-file torrent
        if b'files' in torrent[b'info']:
            torrent[b'url-list'] = WEBSEEDS
        else: # single-file torrent
            torrent[b'url-list'] = []
            name = torrent[b'info'][b'name']
            for root in WEBSEEDS:
                torrent[b'url-list'].append(b'%s%s' % (root, name))
    elif b'url-list' in torrent: # only remove preexisting webseeds
        del torrent[b'url-list']

def write_torrent(torrent, fd):
    """
    Write the modified torrent to the disk.
    """
    try:
        fd.write(lt.bencode(torrent))
        fd.close()
    except IOError:
        return False
    return True

def main(results):
    """
    Main function, takes the results from argparse.
    """
    torrent = lt.bdecode(results.source.read())
    results.source.close()

    if not torrent:
        print('The source file does not seem to be a proper torrent file.')
        results.destination.close()
        exit(1)

    if not remove_private(torrent) and not results.force:
        print('This torrent is already public. Stopping...')
        exit(2)
    swap_trackers(torrent)
    swap_webseeds(torrent)
    return write_torrent(torrent, results.destination)

if __name__ == '__main__':
    import argparse
    from sys import argv
    parser = argparse.ArgumentParser(
        description='Convert a private torrent to a public one.')
    parser.add_argument('source',
        type=argparse.FileType('rb'),
        action='store',
        help='The original (private) torrent')
    parser.add_argument('destination',
        type=argparse.FileType('wb'),
        action='store',
        help='The target file to write in')
    parser.add_argument('-f', '--force',
        action='store_true',
        dest='force',
        help='Modify the torrent even if it is already public')

    results = parser.parse_args()
    success = main(results)

    if success:
        print('The torrent %s was written successfully.' % argv[2])
        exit(0)
    else:
        print('Could not write %s.' % argv[2])
        exit(3)
