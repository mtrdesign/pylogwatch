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
    def _init__ (self, *args, **kwargs):
        super(SysLogDateFormatter, self).__init(*args, **kwargs)
        if self.active:
            self.year = datetime.now().year

    def format_line (self, line, datadict):
        parts = line.split()
        datestr = ' '.join (parts[:3]) + ' %d' % self.year
        timestruct = time.strptime(datestr, "%b %d %H:%M:%S %Y")
        self.dt = datetime.fromtimestamp(time.mktime(timestruct))
        kwargs ['date']=self.dt
 
