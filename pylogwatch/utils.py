"""
Utilities.
"""

import fcntl

def lockfile (lockfile):
    """
    Create a lockfile. Thanks to http://amix.dk/blog/post/19531
    """
    fp = open(lockfile, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False
    return True
