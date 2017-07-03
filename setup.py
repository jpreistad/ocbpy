#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Copyright (C) 2017, AGB & GC
# Full license can be found in License.md
#-----------------------------------------------------------------------------

from os import path
from setuptools import setup, find_packages

# Define a read function for using README for long_description

def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

# Define a test suite

def ocb_test_suite():
    import unittest

    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(path.join(path.dirname(__file__),
                                                '/ocbpy/tests'),
                                      pattern='test_*.py')
    return test_suite

# Run setup

setup(name='ocbpy',
      version='0.1a1',
      url='github.com/aburrell/ocbpy',
      author='Angeline G. Burrell',
      author_email='agb073000@utdallas.edu',
      description='Location relative to open/closed field line boundary',
      long_description=read('README.md'),
      packages=find_packages(),
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Topic :: Scientific/Engineering :: Physics",
          "Intended Audience :: Science/Research",
          "License :: BSD",
          "Natural Language :: English",
          "Programming Language :: Python :: 2.7",
          "Operating System :: MacOS :: MacOS X",
      ],
      include_package_data=True,
      zip_safe=False,
      test_suite='setup.ocb_test_suite',
)

print "ocbpy setup complete"
