# -*- coding: utf-8 -*-
"""
This module contains the tool of jalon.content
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '3.1.1'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read(os.path.join("docs", 'CHANGES.txt'))
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('jalon', 'content', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read(os.path.join("docs", 'CONTRIBUTORS.txt'))
    + '\n' +
    'Download\n'
    '********\n')

tests_require = ['zope.testing']

setup(name='jalon.content',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Framework :: Plone',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   ],
      keywords='',
      author='Bordonado Christophe, Jerome Navarro, Olivier Bado - Université Nice Sophia Antipolis (uns) Service TICE / Jean Bado - Université Versaille Saint-Quentin(UVSQ)',
      author_email='tice@unice.fr',
      url='http://unice.fr',
      license='CECILL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jalon', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='jalon.content.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
