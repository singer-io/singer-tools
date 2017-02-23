#!/usr/bin/env python

from setuptools import setup

setup(name='singer-tools',
      version='0.0.1',
      description='Tools for working with Singer.io Taps and Targets',
      author='Stitch',
      url='http://singer.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      install_requires=[
          'singer-python>=0.1.0'
      ],
      entry_points='''
          [console_scripts]
          tap-freshdesk=tap_freshdesk:main
      '''
      include_package_data=True,
)
