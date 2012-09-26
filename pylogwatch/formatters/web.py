from formatters.base import BaseFormatter
from dateutil.parser import parse

import logging

class ApacheErrorLogFormatter (BaseFormatter):
    """
    Relies on the following parts:
    [date] [severity] [client XXX] everything else
    """
    levels = logging._levelNames
    activate_on_fname_suffix = ('error.log','error_log')

    def format_line (self, line, datadict):
        line_parts = [p.strip().lstrip('[') for p in line.split(']')]
        try:
            dt = parse (line_parts[0])
        except ValueError:
            return datadict
        datadict ['message'] = datadict ['message'].replace('[%s]' % line_parts[0],'',1).lstrip()
        datadict ['date']= dt
        datadict.setdefault('extra',{})['raw_datestring'] = line_parts[0]

        loglvl = line_parts[1].upper()
        if not loglvl.isdigit() and loglvl in self.levels:
            datadict.setdefault('data',{})['level'] = self.levels[loglvl]

        datadict['extra']['remote_ip'] = line_parts[2].split()[-1]
        return datadict