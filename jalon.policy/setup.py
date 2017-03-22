# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '3.1'

setup(name='jalon.policy',
      version=version,
      description="Configuration de jalon",
      long_description=open("README.txt").read() + "\n" + open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=["Framework :: Plone",
                   "Programming Language :: Python", ],
      keywords='',
      author='Bordonado Christophe - Université Nice Sophia Antipolis (uns) Service TICE',
      author_email='tice@unice.fr',
      url='http://unice.fr',
      license='CECILL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jalon'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'jalon.content',
          'jalon.theme',
          'jalon.bdd',
          'jalon.pas.bdd',
          'jalon.elasticsearch',
          'jalon.wims',
          'jalon.connect',
          'jalon.primo',
          'jalon.elasticsearch',
          'jalon.wowza',
          'collective.quickupload',
          'collective.js.jqueryui',
          'anz.casclient',
          'plone.app.ldap',
          'python-dateutil',
          'SQLAlchemy',
          'Products.Ploneboard',
          'twython',
          'pycrypto',
          'xlwt'
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
