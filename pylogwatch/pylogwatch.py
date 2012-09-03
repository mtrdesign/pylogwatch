#!/usr/bin/env python
# Main executable

import config

from logwlib import PyLogConf

if __name__=='__main__':
    pl = PyLogConf(config)
    pl.run()
