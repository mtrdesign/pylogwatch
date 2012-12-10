==========
pylogwatch
==========
Log file parser, which sends the contents of log files to a centralized Sentry server. Meant for periodic execution via cron.

Config
==========
So far the config format is quite simple. It currently looks like this:
::
    DEBUG=True

    RAVEN = {
      'dsn':'<RAVEN_DSN_URL>',
    }

    # List of files to monitor and their associated formatters
    FILE_FORMATTERS = {
        '/var/log/syslog': ('formatters.base.SysLogDateFormatter',
                            'formatters.base.SysLogProcFormatter',),

        '/var/log/auth.log': ('formatters.base.SysLogDateFormatter',
                            'formatters.base.SysLogProcFormatter',),

        '/var/log/apache/error.log': ('formatters.web.ApacheErrorLogFormatter',),

    }


DB
==========
PyLogWatch will automaticall create a SQLite database in the folder where the Config File resides.

Execution
==========
To start pylogwatch simply use the '-c' switch to indicate the path to the configuration file:

    pylog.py -c /path/to/pylogconf.py

Caveats
==========
Keep in mind that PyLogWatch uses a regular Python file as a configuration. This means that giving write access
to the config file is equivalent to giving execuion privileges for custom Python code. Keep your configuration files
adequately protected
