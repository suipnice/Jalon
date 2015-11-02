from zope.interface import Interface

class IWimsBrowserView(Interface):
    """Wims Browser View"""

    def upload(self):
        """Upload a file to the zodb"""
