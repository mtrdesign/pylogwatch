import re
import time
from datetime import datetime

class BaseFormatter (object):
    """
    Specific format dettection based on the inspected filename and the
    line being given.
    """
    active = False
    activate_on_fname_suffix = ()

    def __init__ (self, fname, line):
        """Should be overridden to enable detection based on the first line
        and the filename of the log file. Must be overriden
        """
        for sufx in self.activate_on_fname_suffix:
            if fname.endswith(sufx):
                self.active = True
                break

    def format_line (self, line, datadict):
        """
        This code will only be called if self.active = True. Must be overriden
        by code that reads the line argument, and then changes the contents of
        dataditct (which are ultimately passed to Raven's capture func) """
        raise NotImplementedError

class SysLogDateFormatter (BaseFormatter):
    activate_on_fname_suffix = ('/syslog','/messages','/auth.log', '/kern.log')
    def __init__ (self, *args, **kwargs):
        super(SysLogDateFormatter, self).__init__(*args, **kwargs)
        self.year = datetime.now().year # this needs some more complex logic

    def format_line (self, line, datadict):
        parts = line.split()
        raw_datestr = ' '.join (parts[:3]) + ' '
        datestr = raw_datestr + unicode(self.year)
        try:
            timestruct = time.strptime(datestr, "%b %d %H:%M:%S %Y")
        except ValueError: # Uh-oh, line with an unexpected format
            return datadict
        self.dt = datetime.fromtimestamp(time.mktime(timestruct))
        datadict ['date']=self.dt
        datadict ['message'] = datadict ['message'].replace(raw_datestr ,'')
        datadict.setdefault('extra',{})['Raw Datestring'] = raw_datestr


class SysLogProcFormatter (SysLogDateFormatter):
    PROC_RE = re.compile(r'(\[[0-9.]+\])')
    def format_line (self, line, datadict):
        match = self.PROC_RE.search(line)
        if match:
            # get the matching text
            procstr = match.group(1)
            datadict ['message'] = datadict ['message'].replace(procstr,'',1)
            datadict.setdefault('extra',{})['proc_stamp'] = procstr
        return datadict
