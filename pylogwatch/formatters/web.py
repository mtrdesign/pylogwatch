from pylogwatch.formatters.base import BaseFormatter
from dateutil.parser import parse

import logging

class ApacheErrorLogFormatter (BaseFormatter):
    """
    Relies on the following parts:
    [date] [severity] [client XXX] everything else
    """
    levels = logging._levelNames
    activate_on_fname_suffix = ('error.log','error_log')

    def format_line (self, line, datadict, paramdict):
        line_parts = [p.strip().lstrip('[') for p in line.split(']')]
        try:
            dt = parse (line_parts[0])
        except ValueError:
            return datadict
        # Add date as a param and event date
        datadict ['message'] = self.replace_param(line, datadict ['message'], '[%s]' % line_parts[0], paramdict)
        datadict ['date']= dt

        # Add remote IP as a param
        if len(line_parts)>1:
            datadict ['message'] = self.replace_param(line, datadict ['message'], line_parts[2].split()[-1], paramdict)

        # Add loglevel
        loglvl = line_parts[1].upper()
        if not loglvl.isdigit() and loglvl in self.levels:
            datadict.setdefault('data',{})['level'] = self.levels[loglvl]

        # set the Referer field as the culprit
        ref = line.split('referer: ')[-1]
        if ref!= line:
            datadict['culprit'] = ref.strip()
