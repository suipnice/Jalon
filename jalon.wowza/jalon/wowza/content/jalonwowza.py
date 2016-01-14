# -*- coding: utf-8 -*-
from zope.interface import implements
from OFS.SimpleItem import SimpleItem

from persistent.dict import PersistentDict

from interfaces import IJalonWowza
from jalon.content.content import jalon_utils

from math import ceil
from elasticsearch import Elasticsearch

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

    _streaming_available = {}

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

    def searchExtraits(self, page, term_search=None):
        start = (page - 1) * 12
        elasticsearch = Elasticsearch(hosts=["%s:%s/%s" % (self._pod_server, self._pod_elasticsearch_port, self._pod_elasticsearch_index)])

        body = {"from": start, "size": 12, "sort": [{"date_added": "desc"}], "query": {"filtered": {"filter": {"term": {"owner": self._pod_user}}}}}
        if term_search:
            body["query"]["filtered"]["query"] = {"multi_match": {"query": term_search, "fields": ["title", "owner", "owner_full_name", "description", "discipline", "tags", "channel"], "type": "phrase_prefix"}}
        result = elasticsearch.search(body=body, size=12)

        resultat = {"count": 0, "first": 0, "last": 0, "nb_pages": 0, "liste_videos": []}
        for key in ["from", "size", "sort"]:
            if key in body:
                del body[key]
        count = elasticsearch.count(body=body)
        resultat["count"] = count["count"]
        resultat["first"] = start + 1
        resultat["last"] = start + len(result["hits"]["hits"])
        nb_pages = float(count["count"] / 12.0)
        resultat["nb_pages"] = int(ceil(nb_pages))
        if result:
            streaming_available_ids = self.getKeyStreamingAvailable()
            for fiche in result["hits"]["hits"]:
                pod_id = str(fiche["_source"]["id"])
                is_streaming = False
                streaming_available = "fa fa-video-camera alert right"
                expiration_date = "Streaming interdit"
                if pod_id in streaming_available_ids:
                    is_streaming = True
                    streaming_available = "fa fa-video-camera success right"
                    expiration_date = "Streaming autorisé jusqu'au %s" % jalon_utils.getLocaleDate(self.getStreamingAvailable(pod_id), '%d %B %Y - %Hh%M')
                resultat["liste_videos"].append({"id":                  pod_id,
                                                 "full_url":            fiche["_source"]["full_url"],
                                                 "title":               fiche["_source"]["title"].encode("utf-8"),
                                                 "owner":               fiche["_source"]["owner"],
                                                 "owner_full_name":     fiche["_source"]["owner_full_name"].encode("utf-8"),
                                                 "thumbnail":           fiche["_source"]["thumbnail"].encode("utf-8"),
                                                 "text":                fiche["_source"]["description"].encode("utf-8"),
                                                 "is_streaming":        is_streaming,
                                                 "streaming_available": streaming_available,
                                                 "expiration_date":     expiration_date})

        return resultat

    def getStreamingAvailable(self, key=None):
        if key:
            return self._streaming_available.get(key, None)
        return self._streaming_available

    def getKeyStreamingAvailable(self):
        return self._streaming_available.keys()

    def setStreamingAvailable(self, streaming_available):
        if type(self._streaming_available).__name__ != "PersistentMapping":
            self._streaming_available = PersistentDict(streaming_available)
        else:
            self._streaming_available = streaming_available

    def modifyStreaming(self, pod, expiration_date=None):
        streaming_available = self.getStreamingAvailable()
        if expiration_date:
            streaming_available[pod] = expiration_date
        else:
            del streaming_available[pod]
        self.setStreamingAvailable(streaming_available)
