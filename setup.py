from setuptools import setup

setup(
    name='PyLogWatch',
    version='0.1.9-alpha',
    author='E. Filipov, MTR Design',
    author_email='pylogwatch@mtr-design.com',
    packages=['pylogwatch','pylogwatch.formatters'],
    scripts=['bin/pylog.py'],
    url='http://pypi.python.org/pypi/PyLogWatch/',
    license='LICENSE.txt',
    description='Python utility to parse log files and send them to a Sentry server.',
    long_description=open('README.txt').read(),
    install_requires=[
        "python-dateutil == 1.5",
        "raven >= 2.0",
    ],
)
