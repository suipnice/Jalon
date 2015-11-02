from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "Jalon" theme, this interface must be its layer
       (in theme/viewlets/configure.zcml).
    """