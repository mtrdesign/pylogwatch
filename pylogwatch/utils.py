"""
Utilities.
"""

import fcntl

def lockfile (lockfile):
    """
    Create a and lock the file object supplied in lcokfile.
    Lockfile should be a file object opened with 'w'.
    """
    try:
        fcntl.lockf(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False
    return True
