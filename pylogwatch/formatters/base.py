import re
import time
from datetime import datetime
from dateutil.parser import parse

class BaseFormatter (object):
    def format_line (self, line, datadict, paramdict):
        """
        Must be overriden
        by code that reads the line argument, and then changes the contents of
        dataditct (which are ultimately passed to Raven's capture func).
        Paramdict is a dictionary with replaced values, where the key is the
        string index of the replacement, and the value is the replaced string."""
        raise NotImplementedError

    def replace_param (self, original_line, msg, val, paramdict):
        """
        Replaces the first occurrence of val in the msg, and updates
        paramdict with the index of the replaced value found in original_line
        and the value itself.
        Returns the new line resulted from the potential replace in msg.
	"""
        index = original_line.find(val)
        if index > -1:
            newline = msg.replace(val,'%s', 1)
            paramdict[index] = val
            return newline
        return msg

class SysLogDateFormatter (BaseFormatter):
    def __init__ (self, *args, **kwargs):
        super(SysLogDateFormatter, self).__init__(*args, **kwargs)
        self.year = datetime.now().year # this needs some more complex logic

    def format_line (self, line, datadict, paramdict):
        parts = line.split()
        raw_datestr = ' '.join (parts[:3]) + ' '
        datestr = raw_datestr + unicode(self.year)
        try:
            dt = parse(datestr)
        except ValueError: # Uh-oh, line with an unexpected format
            return datadict
        datadict ['date'] = dt
        datadict ['message'] = self.replace_param (line, datadict ['message'], raw_datestr, paramdict)

class SysLogProcFormatter (SysLogDateFormatter):
    PROC_RE = re.compile(r'(\[[0-9.]+\])')
    def format_line (self, line, datadict, paramdict):
        match = self.PROC_RE.search(line)
        if match:
            # get the matching text
            procstr = match.group(1)
            datadict ['message'] = self.replace_param (line, datadict ['message'], procstr, paramdict)
