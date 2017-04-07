#!/usr/bin/env python

from setuptools import setup

setup(name='singer-tools',
      version='0.2.0',
      description='Tools for working with Singer.io Taps and Targets',
      author='Stitch',
      url='http://singer.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      install_requires=[
          'singer-python>=0.2.1',
          'attrs==16.3.0',
          'terminaltables==3.1.0'
      ],
      packages=['singertools'],
      entry_points='''
          [console_scripts]
          singer-infer-schema=singertools.infer_schema:main
          singer-check-tap=singertools.check_tap:main
          singer-release=singertools.release:main
      ''',
      include_package_data=True,
)
