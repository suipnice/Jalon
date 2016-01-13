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

    _wowza_server = "http://domainname.com"
    _wowza_application = "vod"
    _wowza_secret = ""
    _wowza_sha = "512"

    _pod_server = "http://domainname.com"
    _pod_user = "wowza"
    _pod_elasticsearch_port = 9200
    _pod_elasticsearch_index = "pod"

    def __init__(self, *args, **kwargs):
        super(JalonWowza, self).__init__(*args, **kwargs)

    def getWowzaProperties(self):
        return {"wowza_server":            self._wowza_server,
                "wowza_application":       self._wowza_application,
                "wowza_secret":            self._wowza_secret,
                "wowza_sha":               self._wowza_sha,
                "pod_server":              self._pod_server,
                "pod_user":                self._pod_user,
                "pod_elasticsearch_port":  self._pod_elasticsearch_port,
                "pod_elasticsearch_index": self._pod_elasticsearch_index}

    def setWowzaProperties(self, wowzaProperties):
        for key in wowzaProperties.keys():
            val = wowzaProperties[key]
            setattr(self, "_%s" % key, val)
