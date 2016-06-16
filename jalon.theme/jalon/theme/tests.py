u""" Test Case for jalon Theme.

__author__  = "Université Nice Sophia Antipolis - Service des pedagogies innovantes"
__credits__ = ["Christophe Bordonado", "Jerome Navarro", "Olivier Bado", "Philippe Pomedio"]
__license__ = "GPL"
__version__ = "1.0"
__email__   = "tice@unice.fr"
__status__  = "Production"

"""

import unittest
import jalon.theme

# from zope.testing import doctestunit
# from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()


class TestCase(ptc.PloneTestCase):

    """    TestCase Class.   """

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(jalon.theme)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    """    test_suite.    """
    return unittest.TestSuite(
        [
            # Unit tests
            # doctestunit.DocFileSuite(
            #    'README.txt', package='jalon.theme',
            #    setUp=testing.setUp, tearDown=testing.tearDown),

            # doctestunit.DocTestSuite(
            #    module='jalon.theme.mymodule',
            #    setUp=testing.setUp, tearDown=testing.tearDown),


            # Integration tests that use PloneTestCase
            # ztc.ZopeDocFileSuite(
            #    'README.txt', package='jalon.theme',
            #    test_class=TestCase),

            # ztc.FunctionalDocFileSuite(
            #    'browser.txt', package='jalon.theme',
            #    test_class=TestCase),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
