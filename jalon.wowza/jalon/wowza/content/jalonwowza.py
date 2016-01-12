# -*- coding: utf-8 -*-
from zope.interface import implements
from OFS.SimpleItem import SimpleItem

#from Products.CMFCore.utils import getToolByName

from interfaces import IJalonWowza

# Messages de debug :
from logging import getLogger
LOG = getLogger('[JalonWowza]')


class JalonWowza(SimpleItem):

    implements(IJalonWowza)
    _wowza_server = "http://domainname.com/"
    _wowza_application = "vod"
    _wowza_secret = ""
    _wowza_sha = "512"

    def __init__(self, *args, **kwargs):
        super(JalonWowza, self).__init__(*args, **kwargs)

    def getWowzaProperties(self):
        return {"wowza_server":      self._wowza_server,
                "wowza_application": self._wowza_application,
                "wowza_secret":      self._wowza_secret,
                "wowza_sha":         self._wowza_sha}

    def setWowzaProperties(self, wowzaProperties):
        for key in wowzaProperties.keys():
            val = wowzaProperties[key]
            setattr(self, "_%s" % key, val)
