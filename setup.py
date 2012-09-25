# -*- coding: utf-8 -*-
# Copyright (c) 2002-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from setuptools import setup, find_packages
import os

version = '3.0c1'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='Products.SilvaDocument',
      version=version,
      description="Document content for Silva 2.x.",
      long_description=open(os.path.join("Products", "SilvaDocument", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "SilvaDocument", "HISTORY.txt")).read(),
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='silva cms document zope',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Products.ParsedXML',
        'Products.Silva',
        'Products.SilvaExternalSources',
        'Sprout',
        'five.grok',
        'lxml',
        'setuptools',
        'silva.core.conf',
        'silva.core.interfaces',
        'silva.core.layout',
        'silva.core.references',
        'silva.core.services',
        'silva.core.upgrade',
        'silva.core.views',
        'silva.translations',
        'zope.annotation',
        'zope.component',
        'zope.event',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.traversing',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      )
