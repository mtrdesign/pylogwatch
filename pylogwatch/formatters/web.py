from pylogwatch.formatters.base import BaseFormatter
from dateutil.parser import parse

import logging

class NginxErrorLogFormatter (BaseFormatter):
    """
    Relies on the following parserts:
    <year/month/day hour:minute:sec> [<severity>] <cryptic_numbers> <error_description> client: <client>, 
        server: <client>, request: <request>, host: <host>
    """
    levels = logging._levelNames
    activate_on_fname_suffix = ('error.log','error_log')

    def format_line (self, line, datadict, paramdict):
        try:
            dt = parse (line[:19])
        except ValueError:
            return datadict
        # Add date as a param and event date
        datadict['message'] = self.replace_param(line, datadict ['message'], '%s' % line[0:19], paramdict)
        datadict['date'] = dt

        # Add remote IP as a param
        client_split = line.split('client: ')
        if len(client_split) > 1:
            client = client_split[1].split(',')[0]
            datadict ['message'] = self.replace_param(line, datadict ['message'], client, paramdict)

        severity = [p.strip().lstrip('[') for p in line[20:].split(']')][0]
        # Add loglevel
        loglvl = severity.upper()
        if not loglvl.isdigit() and loglvl in self.levels:
            datadict.setdefault('data',{})['level'] = self.levels[loglvl]

        # Add "cryptic numbers" as parameters for better grouping
        space_parts = line.split(' ')
        if space_parts[4].startswith('*'):
            cryptic_numbers = (' ').join(space_parts[3:5])
        else:
            cryptic_numbers = (' ').join(space_parts[3:4])
        if cryptic_numbers:
            datadict ['message'] = self.replace_param(line, datadict ['message'], cryptic_numbers, paramdict)

        # set the Referer field as the culprit
        ref = line.split('referrer: ')[-1]
        if ref != line:
            datadict['culprit'] = ref.strip().strip('"')

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
