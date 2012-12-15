# Python 2.5 compatibility
from __future__ import with_statement

# Python version
import sys
if sys.version_info < (2, 5):
    raise "Required python 2.5 or greater"

import os, sqlite3, itertools, time
from datetime import datetime

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
proj_path = lambda x: os.path.abspath(os.path.join(PROJECT_DIR,x))
# Check if we are bundled together with raven, and add our dir to the pythonpath if we are
if os.path.exists(proj_path( 'raven')):
    sys.path.append(PROJECT_DIR)

from raven import Client


def item_import(name):
    d = name.rfind(".")
    classname = name[d+1:]
    m = __import__(name[:d], globals(), locals(), [classname])
    return getattr(m, classname)

class PyLog (object):
    def __init__ (self, filenames, dbname = 'logw.db', filetable = 'file_cursor', eventtable = 'events'):
        self._filetable = filetable
        self._eventtable = eventtable
        self.conn = self.init_db(dbname)
        self.curs = self.conn.cursor()
        self.fnames = filenames

    def init_db (self, dbname):
        """Set up the DB"""
        conn = sqlite3.connect (dbname)
        curs = conn.cursor()
        sql = 'create table if not exists file_cursor (filename TEXT PRIMARY KEY, inode INTEGER, lastbyte INTEGER, updated INTEGER)'
        curs.execute (sql)
        sql = 'create table if not exists events (event TEXT PRIMARY KEY, args TEXT, updated INTEGER)'
        curs.execute (sql)
        conn.commit()
        return conn

    def readlines (self, f, lastpos = 0):
        """Read full lines from the file object f starting from lastpos"""
        self.save_fileinfo (f.name, os.stat(f.name)[1], lastpos)
        f.seek(lastpos)
        result = []
        for line in f:
            # handle lines that are not yet finished (no \n)
            curpos = f.tell()
            if not line.endswith('\n'):
                f.seek(curpos)
                raise StopIteration
            yield line

    def get_fileinfo (self, fname):
        self.curs.execute ('SELECT filename, inode, lastbyte from file_cursor where filename=?', [fname,])
        result = self.curs.fetchone()
        if result and len(result)==3:
            f, inode, lastbyte = result
            return inode,lastbyte
        else:
            return None,0

    def save_fileinfo (self, fname, inode, lastbyte):
        self.curs.execute ("REPLACE into file_cursor (filename, inode, lastbyte, updated) \
        values (?,?,?,datetime())", [fname,inode, lastbyte ])
        self.conn.commit()
        return

    def update_bytes (self,fname, lastbyte):
        """
        Only updates the lastbyte property of a file, without touching the inode.
        Meant for calling after each line is processed
        """
        def save_fileinfo (self, fname, inode, lastbyte):
            self.curs.execute ("UPDATE into file_cursor set lastbyte=? where filename=?",\
                               [fname,inode, lastbyte ])
            self.conn.commit()
            return

    def process_lines (self, fname, lines):
        """Dummy line processor - should be overridden"""
        raise NotImplementedError

    def open_rotated_version(self, fname):
        sufxs = ['.1','.1.gz','.0']
        for sufx in sufxs:
            newname = fname + sufx
            if not os.path.exists (newname):
                continue
            try:
                f = open(newname)
                return f
            except:
                continue

    def run (self):
        for fn in self.fnames:
            if not os.path.exists (fn):
                continue

            newlines = []
            rotated = None
            lastinode, lastbyte = self.get_fileinfo (fn)
            if lastbyte and not lastinode == os.stat(fn)[1]:
                # handle rotated files
                rotated = self.open_rotated_version(fn)
                if rotated:
                    newlines = self.readlines (rotated, lastbyte)
                    lastbyte = 0
                    self.process_lines (fn, rotated, newlines)
            try:
                f = open(fn)
            except:
                continue
            self.process_lines (fn, f, self.readlines (f, lastbyte))
            lastbyte = f.tell()
            lastinode = os.stat(fn)[1]
            f.close()
            self.save_fileinfo (fn, lastinode, lastbyte)
            if rotated:
                rotated.close()


class PyLogConf (PyLog):
    def __init__ (self, conf):
        """
        Initialize object based on the provided configuration
        """
        self.conf = conf
        self.client = Client (conf.RAVEN['dsn'])
        self.formatters = {}
        for k,v in self.conf.FILE_FORMATTERS.iteritems():
            if isinstance(v,str):
                raise ValueError ('Please use a list or a tuple for the file formatters values')
            self.formatters[k] = [item_import(i)() for i in v]
        dbname = os.path.join(os.path.dirname(conf.__file__),'pylogwatch.db')
        return super(PyLogConf, self).__init__ (self.conf.FILE_FORMATTERS.keys(), dbname = dbname)

    def process_lines (self, fname, fileobject, lines):
        """Main workhorse. Called with the filename that is being logged and an iterable of lines"""
        for line in lines:
            paramdict = {}
            data = {'event_type':'Message', 'message': line.replace('%','%%'), 'data' :{'logger':fname}}
            for fobj in self.formatters[fname]:
                fobj.format_line(line, data, paramdict)
            if not data.pop('_do_not_send', False): # Skip lines that have the '_do_not_send' key
                if paramdict:
                    data['params'] = tuple([paramdict[i] for i in sorted(paramdict.keys())])
                if self.conf.DEBUG:
                    print data
                self.client.capture(**data)
                self.update_bytes(fname, fileobject.tell())

