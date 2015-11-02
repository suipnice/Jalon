from zope.interface import implements
from Products.Five.browser import BrowserView
#from Acquisition import aq_inner
from Products.TinyMCE.adapters.interfaces.Upload import IUpload
from Products.TinyMCE.adapters.interfaces.Save import ISave

from .interfaces.browser import IWimsBrowserView


class WimsBrowserView(BrowserView):
    """Wims Browser View"""
    implements(IWimsBrowserView)

    def upload(self):
        """Upload a file to the zodb"""

        #context = aq_inner(self.context)
        object = IUpload(self.context)
        return object.upload()

    def save(self, text, fieldname):
        """Saves the specified richedit field"""

        #context = aq_inner(self.context)
        object = ISave(self.context)
        return object.save(text, fieldname)
