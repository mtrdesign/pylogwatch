from distutils.core import setup

setup(
    name='PyLogWatch',
    version='0.1.0',
    author='E. Filipov, MTR Design',
    author_email='pylogwatch@mtr-design.com',
    packages=['pylogwatch'],
    scripts=['bin/pylogwatch.py'],
    url='http://pypi.python.org/pypi/PyLogWatch/',
    license='LICENSE.txt',
    description='Python utility to parse log files and send them to a Sentry server.',
    long_description=open('README.txt').read(),
)
