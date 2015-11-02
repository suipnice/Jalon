# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '2.2.5r1492'

setup(name='jalon.theme',
      version=version,
      description="An installable theme for Plone 3",
      long_description=open("README.txt").read() + "\n" + open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=["Framework :: Plone",
                   "Programming Language :: Python", ],
      keywords='',
      author='Jerome Navarro, Bordonado Christophe - Université Nice Sophia Antipolis (uns) Service TICE',
      author_email='tice@unice.fr',
      url='http://unice.fr',
      license='CECILL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jalon'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
