#! /usr/bin/env python

"""
Compute git hash values.
This is meant to work with both Python2 and Python3; it
has been tested with Python2.7 and Python 3.4.
"""

from __future__ import print_function

import argparse
import os
import stat
import sys

from hashlib import sha1

if sys.version_info[0] >= 3:
    # Python3 encodes "impossible" strings using UTF-8 and
    # surrogate escapes.  For instance, a file named <\300><\300>eek
    # (where \300 is octal 300, 0xc0 hex) turns into '\udcc0\udcc0eek'.
    # This is how we can losslessly re-encode this as a byte string:
    path_to_bytes = lambda path: path.encode('utf8', 'surrogateescape')

    # If we wish to print one of these byte strings, we have a
    # problem, because they're not valid UTF-8.  This method
    # treats the encoded bytes as pass-through, which is
    # probably the best we can do.
    bpath_to_str = lambda path: path.decode('unicode_escape')
else:
    # Python2 just uses byte strings, so OS paths are already
    # byte strings and we return them unmodified.
    path_to_bytes = lambda path: path
    bpath_to_str = lambda path: path

def strmode(mode):
    """
    Turn internal mode (octal with leading 0s suppressed) into
    print form (i.e., left pad => right justify with 0s as needed).
    """
    return mode.rjust(6, '0')

def classify(path):
    """
    Return git classification of a path (as both mode,
    100644/100755 etc, and git object type, i.e., blob vs tree).
    Also throw in st_size field since we want it for file blobs.
    """
    # We need the X bit of regular files for the mode, so
    # might as well just use lstat rather than os.isdir().
    st = os.lstat(path)
    if stat.S_ISLNK(st.st_mode):
        gitclass = 'blob'
        mode = '120000'
    elif stat.S_ISDIR(st.st_mode):
        gitclass = 'tree'
        mode = '40000' # note: no leading 0!
    elif stat.S_ISREG(st.st_mode):
        # 100755 if any execute permission bit set, else 100644
        gitclass = 'blob'
        mode = '100755' if (st.st_mode & 0o111) != 0 else '100644'
    else:
        raise ValueError('un-git-able file system entity %s' % fullpath)
    return mode, gitclass, st.st_size

def blob_hash(stream, size):
    """
    Return (as hash instance) the hash of a blob,
    as read from the given stream.
    """
    hasher = sha1()
    hasher.update(('blob %u\0' % size).encode('ascii'))
    nread = 0
    while True:
        # We read just 64K at a time to be kind to
        # runtime storage requirements.
        data = stream.read(65536)
        if data == b'':
            break
        nread += len(data)
        hasher.update(data)
    if nread != size:
        raise ValueError('%s: expected %u bytes, found %u bytes' %
            (stream.name, size, nread))
    return hasher

def symlink_hash(path):
    """
    Return (as hash instance) the hash of a symlink.
    Caller must use hexdigest() or digest() as needed on
    the result.
    """
    hasher = sha1()
    data = path_to_bytes(os.readlink(path))
    hasher.update(('blob %u\0' % len(data)).encode('ascii'))
    hasher.update(data)
    return hasher


def tree_hash(path, args):
    """
    Return the hash of a tree.  We need to know all
    files and sub-trees.  Since order matters, we must
    walk the sub-trees and files in their natural (byte) order,
    so we cannot use os.walk.
    This is also slightly defective in that it does not know
    about .gitignore files (we can't just read them since git
    retains files that are in the index, even if they would be
    ignored by a .gitignore directive).
    We also do not (cannot) deal with submodules here.
    """
    # Annoyingly, the tree object encodes its size, which requires
    # two passes, one to find the size and one to compute the hash.
    contents = os.listdir(path)
    tsize = 0
    to_skip = ('.', '..') if args.keep_dot_git else ('.', '..', '.git')
    pass1 = []
    for entry in contents:
        if entry not in to_skip:
            fullpath = os.path.join(path, entry)
            mode, gitclass, esize = classify(fullpath)
            # git stores as mode<sp><entry-name>\0<digest-bytes>
            encoded_form = path_to_bytes(entry)
            tsize += len(mode) + 1 + len(encoded_form) + 1 + 20
            pass1.append((fullpath, mode, gitclass, esize, encoded_form))

    # Git's cache sorts foo/bar before fooXbar but after foo-bar,
    # because it actually stores foo/bar as the literal string
    # "foo/bar" in the index, rather than using recursion.  That is,
    # a directory name should sort as if it ends with '/' rather than
    # with '\0'.  Sort pass1 contents with funky sorting.
    #
    # (i[4] is the utf-8 encoded form of the name, i[1] is the
    # mode which is '40000' for directories.)
    pass1.sort(key = lambda i: i[4] + '/' if i[1] == '40000' else i[4])

    args.depth += 1
    hasher = sha1()
    hasher.update(('tree %u\0' % tsize).encode('ascii'))
    for (fullpath, mode, gitclass, esize, encoded_form) in pass1:
        sub_hash = generic_hash(fullpath, mode, esize, args)
        if args.debug: # and args.depth == 0:
            print('%s%s %s %s\t%s' % ('    ' * args.depth,
                strmode(mode), gitclass, sub_hash.hexdigest(),
                bpath_to_str(encoded_form)))

        # Annoyingly, git stores the tree hash as 20 bytes, rather
        # than 40 ASCII characters.  This is why we return the
        # hash instance (so we can use .digest() directly).
        # The format here is <mode><sp><path>\0<raw-hash>.
        hasher.update(mode.encode('ascii'))
        hasher.update(b' ')
        hasher.update(encoded_form)
        hasher.update(b'\0')
        hasher.update(sub_hash.digest())
    args.depth -= 1
    return hasher

def generic_hash(path, mode, size, args):
    """
    Hash an object based on its mode.
    """
    if mode == '120000':
        hasher = symlink_hash(path)
    elif mode == '40000':
        hasher = tree_hash(path, args)
    else:
        # 100755 if any execute permission bit set, else 100644
        with open(path, 'rb') as stream:
            hasher = blob_hash(stream, size)
    return hasher

def main():
    """
    Parse arguments and invoke hashers.
    """
    parser = argparse.ArgumentParser('compute git hashes')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-k', '--keep-dot-git', action='store_true')
    parser.add_argument('path', nargs='+')
    args = parser.parse_args()
    args.depth = -1 # for debug print
    status = 0
    for path in args.path:
        try:
            try:
                mode, gitclass, size = classify(path)
            except ValueError:
                print('%s: unhashable!' % path)
                status = 1
                continue
            hasher = generic_hash(path, mode, size, args)
            result = hasher.hexdigest()
            if args.debug:
                print('%s %s %s\t%s' % (strmode(mode), gitclass, result,
                    path))
            else:
                print('%s: %s hash = %s' % (path, gitclass, result))
        except OSError as err:
            print(str(err))
            status = 1
    sys.exit(status)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit('\nInterrupted')