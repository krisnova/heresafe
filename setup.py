from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='heresafe',
    version='1.0.2',
    description='heresafe is a Python utility that will send an arbitrary text message to a configured number when a script runs and detects you are connected to a certain SSID.',
    long_description=long_description,
    url='https://github.com/kris-nova/heresafe',
    author='Kris Nova',
    author_email='kris@nivenly.com',
    license='APACHE',
    packages=['heresafe', ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Environment :: MacOS X',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'pygooglevoice',
    ],
    keywords='heresafe, text, message, ssid, network, wifi, arrive',
    entry_points={
        'console_scripts': ['heresafe=heresafe.heresafe:main', ],
    },
)
