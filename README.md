# torrent_free

This script was written in 2012 ago in order to provide an easy way
to "free" a torrent from its private tracker, making it accessible to
anyone.

I am putting it on github so that it can get some use.

# depends

This script requires python and the libtorrent-rasterbar library
with python bindings installed.

# usage

```
usage: torrent_free.py [-h] [-f] source destination

Convert a private torrent to a public one.

positional arguments:
  source       The original (private) torrent
  destination  The target file to write in

optional arguments:
  -h, --help   show this help message and exit
  -f, --force  Modify the torrent even if it is already public
```

# license

This is Free software, released unser the WTFPL, due to its simplicity
and short size. Do whatever you want.
