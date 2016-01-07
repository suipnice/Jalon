# -*- coding: utf-8 -*-
from zope.interface import implements
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import getToolByName

from interfaces import IJalonElasticsearch

from math import ceil
from elasticsearch import Elasticsearch

# Messages de debug :
from logging import getLogger
LOG = getLogger('[JalonElasticsearch]')


class JalonElasticsearch(SimpleItem):

    implements(IJalonElasticsearch)
    _url_connexion = "http://domainname.com/"
    _port_connexion = "9200"
    _index = "pod"
    _name_serveur = "Pod"

    def __init__(self, *args, **kwargs):
        super(JalonElasticsearch, self).__init__(*args, **kwargs)

    def getPropertiesElasticsearch(self):
        return {"url_connexion":  self._url_connexion,
                "port_connexion": self._port_connexion,
                "index":          self._index,
                "name_serveur":   self._name_serveur}

    def setPropertiesElasticsearch(self, propertiesElasticsearch):
        for key in propertiesElasticsearch.keys():
            val = propertiesElasticsearch[key]
            setattr(self, "_%s" % key, val)

    def searchElasticsearch(self, type_search=None, term_search=None, page=1):
        start = (page - 1) * 12
        #LOG.info("%s:%s/%s" % (self._url_connexion, self._port_connexion, self._index))
        elasticsearch = Elasticsearch(hosts=["%s:%s/%s" % (self._url_connexion, self._port_connexion, self._index)])
        if not type_search or type_search == "mes_videos":
            portal_membership = getToolByName(self, 'portal_membership')
            authMember = portal_membership.getAuthenticatedMember()
            body = {"from": start, "size": 12, "sort": [{"date_added": "desc"}], "query": {"filtered": {"filter": {"term": {"owner": authMember.getId()}}}}}
            if term_search:
                body["query"]["filtered"]["query"] = {"match": {"title": term_search}}
            result = elasticsearch.search(body=body, size=12)
        if type_search == "toutes_videos":
            body = {"from": start, "size": 12, "sort": [{"date_added": "desc"}], "query": {"multi_match": {"query": term_search, "fields": ["title", "owner", "owner_full_name", "description", "discipline", "tags", "channel"], "type": "phrase_prefix"}}}
            result = elasticsearch.search(body=body, size=12)
        if type_search == "video":
            body = {"query": {"match": {'id': {'query': term_search, 'operator': 'and'}}}}
            result = elasticsearch.search(body=body)
            if result:
                fiche = result["hits"]["hits"][0]
                return {"id":                  fiche["_source"]["id"],
                        "full_url":            fiche["_source"]["full_url"],
                        "title":               fiche["_source"]["title"].encode("utf-8"),
                        "owner":               fiche["_source"]["owner"],
                        "owner_full_name":     fiche["_source"]["owner_full_name"].encode("utf-8"),
                        "iframe":              '<iframe src="%s?is_iframe=true&size=240" width="640" height="360" style="padding: 0; margin: 0; border:0" allowfullscreen ></iframe>' % fiche["_source"]["full_url"].encode("utf-8"),
                        "thumbnail":           fiche["_source"]["thumbnail"].encode("utf-8"),
                        "text":                fiche["_source"]["description"].encode("utf-8")}
            return None
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
            for fiche in result["hits"]["hits"]:
                resultat["liste_videos"].append({"id":                  fiche["_source"]["id"],
                                                 "full_url":            fiche["_source"]["full_url"],
                                                 "title":               fiche["_source"]["title"].encode("utf-8"),
                                                 "owner":               fiche["_source"]["owner"],
                                                 "owner_full_name":     fiche["_source"]["owner_full_name"].encode("utf-8"),
                                                 "thumbnail":           fiche["_source"]["thumbnail"].encode("utf-8"),
                                                 "text":                fiche["_source"]["description"].encode("utf-8")})

        return resultat
