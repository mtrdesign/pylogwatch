from pylogwatch.formatters.base import BaseFormatter
from dateutil.parser import parse

class GitoliteLogFormatter(BaseFormatter):
    """
    Relies on the following parserts:
    <date>\t<log_block_number>\t<command|empty>\t<details>

    We log only if command == die    
    """

    def format_line (self, line, datadict, paramdict):
        line_parts = line.split('\t')

        if len(line_parts) < 3:
            return datadict

        if line_parts[2] != 'die':
            datadict['do_not_send'] = True
            return

        try:
            # date is 2012-12-14.15:25:46
            dt = parse (line_parts[0].replace('.', ' '))
        except ValueError:
            return datadict

        # Add date as a param and event date
        datadict['message'] = self.replace_param(line, datadict ['message'], '%s' % line_parts[0], paramdict)
        datadict['date'] = dt

        # log block number as a param
        datadict['message'] = self.replace_param(line, datadict ['message'], '%s' % line_parts[1], paramdict)

        # good value?
        datadict['culprit'] = 'gitolite'