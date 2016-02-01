# -*- coding: utf-8 -*-
from zope.interface import implements
from OFS.SimpleItem import SimpleItem

from persistent.dict import PersistentDict

from interfaces import IJalonWowza
from jalon.content.content import jalon_utils

import time
import base64
import hashlib
from math import ceil
from DateTime import DateTime
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

# Messages de debug :
from logging import getLogger
LOG = getLogger('[JalonWowza]')


class JalonWowza(SimpleItem):

    implements(IJalonWowza)

    _wowza_server = "http://domainname.com"
    _wowza_application = "vod"
    _wowza_secret = ""
    _wowza_sha = "sha256"
    _wowza_token_prefix = "wowzatoken"
    _wowza_ticket_validation = "1"
    _wowza_admin_email = ""

    _pod_server = "http://domainname.com"
    _pod_user = "wowza"
    _pod_elasticsearch_port = 9200
    _pod_elasticsearch_index = "pod"

    _streaming_available = {}

    def __init__(self, *args, **kwargs):
        super(JalonWowza, self).__init__(*args, **kwargs)

    def getWowzaProperties(self):
        return {"wowza_server":             self._wowza_server,
                "wowza_application":        self._wowza_application,
                "wowza_secret":             self._wowza_secret,
                "wowza_sha":                self._wowza_sha,
                "wowza_token_prefix":       self._wowza_token_prefix,
                "wowza_ticket_validation":  self._wowza_ticket_validation,
                "wowza_admin_email":        self._wowza_admin_email,
                "pod_server":               self._pod_server,
                "pod_user":                 self._pod_user,
                "pod_elasticsearch_port":   self._pod_elasticsearch_port,
                "pod_elasticsearch_index":  self._pod_elasticsearch_index}

    def setWowzaProperties(self, wowzaProperties):
        for key in wowzaProperties.keys():
            val = wowzaProperties[key]
            setattr(self, "_%s" % key, val)

    def getExpirationDate(self, streaming_id):
        expiration_date = self.getStreamingAvailable(streaming_id)
        expiration_dico = {"css_class": "fa fa-video-camera success", "expiration_date": "Disponible jusqu'au %s" % jalon_utils.getLocaleDate(expiration_date, '%d %B %Y - %Hh%M')}
        if not expiration_date:
            expiration_dico = {"css_class": "fa fa-video-camera alert", "expiration_date": "Vidéo expirée"}
        else:
            now = DateTime(DateTime().strftime("%Y/%m/%d %H:%M"))
            expiration_date = DateTime(expiration_date)
            if expiration_date < now:
                expiration_dico = {"css_class": "fa fa-video-camera warning", "expiration_date": "Vidéo expirée"}
        return expiration_dico

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
                is_streaming = True if pod_id in streaming_available_ids else False
                expiration_date = self.getExpirationDate(pod_id)
                resultat["liste_videos"].append({"id":                  pod_id,
                                                 "full_url":            fiche["_source"]["full_url"],
                                                 "title":               fiche["_source"]["title"].encode("utf-8"),
                                                 "owner":               fiche["_source"]["owner"],
                                                 "owner_full_name":     fiche["_source"]["owner_full_name"].encode("utf-8"),
                                                 "thumbnail":           fiche["_source"]["thumbnail"].encode("utf-8"),
                                                 "text":                fiche["_source"]["description"].encode("utf-8"),
                                                 "is_streaming":        is_streaming,
                                                 "css_class":           expiration_date["css_class"],
                                                 "expiration_date":     expiration_date["expiration_date"]})

        return resultat

    def searchExtrait(self, streaming_id):
        #LOG.info("----- searchExtrait -----")
        #LOG.info(streaming_id)
        elasticsearch = Elasticsearch(hosts=["%s:%s/%s" % (self._pod_server, self._pod_elasticsearch_port, self._pod_elasticsearch_index)])
        body = {"query": {"match": {'id': {'query': streaming_id, 'operator': 'and'}}}}
        result = elasticsearch.search(body=body, size=12)
        if result:
            fiche = result["hits"]["hits"][0]
            return {"id":                  streaming_id,
                    "full_url":            fiche["_source"]["full_url"],
                    "title":               fiche["_source"]["title"].encode("utf-8"),
                    "owner":               fiche["_source"]["owner"],
                    "owner_full_name":     fiche["_source"]["owner_full_name"].encode("utf-8"),
                    "thumbnail":           fiche["_source"]["thumbnail"].encode("utf-8"),
                    "text":                fiche["_source"]["description"].encode("utf-8")}
        return None

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

    def isStreamingAuthorized(self, streaming_id, client_ip):
        if not self.isStreamingExpired(streaming_id):
            return False
        if not self.isGeoLoc(client_ip):
            return False
        return self.secureStreamingUrl(streaming_id, client_ip)

    def isStreamingExpired(self, streaming_id):
        expiration_date = self.getStreamingAvailable(streaming_id)
        if not expiration_date:
            return False
        else:
            now = DateTime(DateTime().strftime("%Y/%m/%d %H:%M"))
            expiration_date = DateTime(expiration_date)
            if expiration_date < now:
                return False
        return True

    def isGeoLoc(self, client_ip):
        #LOG.info("----- isGeoLoc -----")
        from geoip import geolite2
        match = geolite2.lookup(client_ip)
        #match = geolite2.lookup("134.59.205.212")
        if match is None:
            return False
        LOG.info(match.country)
        if match.country == "FR":
            return True
        return False

    def secureStreamingUrl(self, streaming_id, client_ip):
        #client_ip = "134.59.205.212"
        #LOG.info("----- secureStreamingUrl -----")
        wowza_content_path = "%s/%s.mp4" % (self._wowza_application, streaming_id)
        #LOG.info(wowza_content_path)
        now = datetime.now()
        add_one_week = now + timedelta(days=int(self._wowza_ticket_validation))

        wowzatoken_start_time = "%sstarttime=%s" % (self._wowza_token_prefix, str(int(time.mktime(now.timetuple()))))
        #LOG.info(wowzatoken_start_time)
        wowzatoken_end_time = "%sendtime=%s" % (self._wowza_token_prefix, str(int(time.mktime(add_one_week.timetuple()))))
        #LOG.info(wowzatoken_end_time)

        #LOG.info(self._wowza_secret)
        str_for_sha = "%s?%s&%s&%s&%s" % (wowza_content_path, client_ip, self._wowza_secret, wowzatoken_end_time, wowzatoken_start_time)
        #LOG.info(str_for_sha)
        str_sha = hashlib.new(self._wowza_sha)
        str_sha.update(str_for_sha)
        str_sha = str_sha.digest()
        #LOG.info(str_sha)
        str_sha_base64 = base64.b64encode(str_sha)
        #LOG.info(str_sha_base64)
        str_sha_base64 = str_sha_base64.replace("+", "-")
        str_sha_base64 = str_sha_base64.replace("/", "_")
        #LOG.info(str_sha_base64)
        secure_streaming_url = "%s/%s/%s.mp4?%s&%s&%shash=%s" % (self._wowza_server, self._wowza_application, streaming_id, wowzatoken_start_time, wowzatoken_end_time, self._wowza_token_prefix, str_sha_base64)
        #LOG.info(secure_streaming_url)
        return secure_streaming_url

    def askStreaming(self, streaming_id, member_id):
        #LOG.info("----- askStreaming -----")
        portal = self.portal_url.getPortalObject()
        member_infos = jalon_utils.getInfosMembre(member_id)
        send_to = self._wowza_admin_email
        if not send_to:
            send_to = portal.getProperty("email_from_address")
        streaming_infos = self.searchExtrait(streaming_id)
        message = "Bonjour\n\nUne demande d'autorisation de streaming vient d'être effectuée par \"%s\" pour la vidéo \"%s\" ayant pour identifiant \"%s\".\n\nCordialement,\n%s." % (member_infos["fullname"], streaming_infos["title"], streaming_id, portal.Title())
        #LOG.info({"send_to": member_infos["email"],
        #          "objet":   "Demande d'activation de Streaming",
        #          "message": message})
        jalon_utils.envoyerMail({"send_to": send_to,
                                 "objet":   "Demande d'activation de Streaming",
                                 "message": message})
