#!/usr/bin/env python
# Main executable

import optparse
import sys, os
import imp

from pylogwatch.logwlib import PyLogConf


def load_cfg_module (cfgpath):
    try:
        return imp.load_source ('PyLogConfig',os.path.realpath(cfgpath))
    except ImportError, err:
        sys.exit ('Cannot load config file %s: %s' % (cfgpath, err))

if __name__=='__main__':
    p = optparse.OptionParser()
    p.add_option('--config', '-c', default="config.py", help="Filesystem path to (python) configuration file [default: %default]")
    options, arguments = p.parse_args()
    cfgmod = load_cfg_module(options.config)
    print cfgmod.FILES
    pl = PyLogConf(cfgmod)
    pl.run()
