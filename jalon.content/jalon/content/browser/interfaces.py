from zope.interface import Interface


class IPersonalBar(Interface):
    """ """
    def getColumnsClass():
        """ Returns the CSS class based on columns presence. """


class IJalonProperties(Interface):
    """This interface defines the jalon properties."""
