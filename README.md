pylogwatch
==========
Log file parser, which sends the contents of log files to a centralized Sentry server. Meant for periodic execution via cron.

Config
==========
So far the config format is quite simple. It currently looks like this:
```
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

```

DB
==========
PyLogWatch will automaticall create a SQLite database in the folder where it resides.
