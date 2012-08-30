#!/usr/bin/env python
# Main executable

from logwlib import PyLogIniRaven

if __name__=='__main__':
    pl = PyLogIniRaven('logw.ini')
    pl.run()
