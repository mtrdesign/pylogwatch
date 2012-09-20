import os, sys, sqlite3, itertools, time
from datetime import datetime
import ConfigParser
from raven import Client

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

proj_path = lambda x: os.path.abspath(os.path.join(PROJECT_DIR,x))

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
        conn = sqlite3.connect (proj_path(dbname))
        curs = conn.cursor()
        sql = 'create table if not exists file_cursor (filename TEXT PRIMARY KEY, inode INTEGER, lastbyte INTEGER, updated INTEGER)'
        curs.execute (sql)
        sql = 'create table if not exists events (event TEXT PRIMARY KEY, args TEXT, updated INTEGER)'
        curs.execute (sql)
        conn.commit()
        return conn

    def readlines (self, f, lastpos = 0):
        """Read full lines from the file object f starting from lastpos"""
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
        print result
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

    def process_lines (self, fname, lines):
        """Dummy line processor - should be overridden"""
        print '##### Processed %s:' % fname
        for line in lines:
            print line
            pass
        print

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
            try:
                f = open(fn)
            except:
                continue
            newlines = itertools.chain(newlines, self.readlines (f, lastbyte))
            self.process_lines (fn, newlines)
            lastbyte = f.tell()
            lastinode = os.stat(fn)[1]
            f.close()
            self.save_fileinfo (fn, lastinode, lastbyte)
            if rotated:
                rotated.close()


class PyLogConf (PyLog):
    def __init__ (self, conf):
        self.conf = conf
        self.client = Client (conf.RAVEN['dsn'])
        self.available_formatters = [item_import(f) for f in self.conf.FORMATTERS]
        return super(PyLogConf, self).__init__ (self.conf.FILES)

    def get_file_signature(self, fname):
        maxcount = 10
        count = 0
        result = []
        with open(fname) as f:
            while count < maxcount:
                result.append(f.readline())
                count+=1
        return result


    def process_lines (self, fname, lines):
        enabled_formatters = []
        sig = self.get_file_signature(fname)
        for F in self.available_formatters:
            fobj = F (fname, sig)
            if fobj.active:
                enabled_formatters.append(fobj)

        for line in lines:
            data = {'event_type':'Message', 'message': line,'data' : {'logger':fname}}
            for fobj in enabled_formatters:
                fobj.format_line(line, data)
            print data
            self.client.capture(**data)

