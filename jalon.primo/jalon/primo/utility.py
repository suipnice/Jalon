# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component import getUtility
from zope.interface import classProvides

from AccessControl import ClassSecurityInfo

from jalon.primo.interfaces.utility import IPrimo, IPrimoLayout

from OFS.SimpleItem import SimpleItem

# Imports
import re
import urllib
import urllib2
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Messages de debug :
from logging import getLogger
LOG = getLogger('[jalon.primo.utility]')
"""
# Log examples :
LOG.debug('debug message')
LOG.info('info message')
LOG.warn('warn message')
LOG.error('error message')
LOG.critical('critical message')
"""


def form_adapter(context):
    """Form Adapter"""
    return getUtility(IPrimo)


class Primo(SimpleItem):
    """Primo Utility"""
    implements(IPrimo)
    classProvides(IPrimoLayout,)

    security = ClassSecurityInfo()
    url_connexion = FieldProperty(IPrimoLayout['url_connexion'])
    url_catalogue = FieldProperty(IPrimoLayout['url_catalogue'])
    url_acquisition = FieldProperty(IPrimoLayout['url_acquisition'])
    login = FieldProperty(IPrimoLayout['login'])
    password = FieldProperty(IPrimoLayout['password'])

    def getPrimoProperty(self, key):
        return getattr(self, "%s" % key)

    def setProperties(self, form):
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "%s" % key, val.decode("utf-8"))

    security.declarePrivate('requete')
    def requete(self, webservice, params, xpath=None):
        data = urllib.urlencode(params)
        url_connexion = self.url_connexion
        url_catalogue = self.url_catalogue
        if url_connexion.endswith("/"):
            url_connexion = url_connexion[:-1]
        req = urllib2.Request("%s/%s?%s" % (url_connexion, webservice, data))
        try:
            handle = urllib2.urlopen(req)
            rep = handle.read()
            try:
                xml = ET.XML(rep)
            except:
                # Erreur XML
                return {"response": None, "error": sys.exc_info()}
        except:
            return req
        listeRES = []

        # a mettre en config admin
        listeNameSpace = ["{http://www.exlibrisgroup.com/xsd/primo/primo_nm_bib}", "{http://www.exlibrisgroup.com/xsd/jaguar/search}"]

        res = self.xpath(xml, "{1}JAGROOT/{1}RESULT/{1}DOCSET/{1}DOC".format(*listeNameSpace))
        if res:
            for record in res:
                recordid = str(record.findtext("{0}PrimoNMBib/{0}record/{0}control/{0}recordid".format(*listeNameSpace)))
                dico = {"type": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}type".format(*listeNameSpace)),
                        "title": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}title".format(*listeNameSpace)),
                        "creator": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}creator".format(*listeNameSpace)),
                        "publisher": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}publisher".format(*listeNameSpace)),
                        "creationdate": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}creationdate".format(*listeNameSpace)),
                        "format": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}format".format(*listeNameSpace)),
                        "recordid": recordid,  #identifiant document
                        "language": record.findtext("{0}PrimoNMBib/{0}record/{0}display/{0}language".format(*listeNameSpace)),
                        "subject": [],
                        "image": [],
                        "urlcatalogue": "".join([url_catalogue, "/primo_library/libweb/action/display.do?tabs=detailsTab&ct=display&fn=search&doc=", recordid, "&indx=1&recIds=", recordid, "&recIdxs=0&elementId=0&renderMode=poppedOut&displayMode=full&frbrVersion=&dscnt=1&vl%2814793452UI1%29=all_items&scp.scps=&frbg=&tab=default_tab&srt=rank&mode=Basic&dum=true&vl%289521613UI0%29=any&vid=", self.getGenerique("etablissement")])
                        }
                for subject in record.findall("{0}PrimoNMBib/{0}record/{0}display/{0}subject".format(*listeNameSpace)):
                    dico["subject"].append(subject.text)

                for image in record.findall("{1}LINKS/{1}thumbnail".format(*listeNameSpace)):
                    dico["image"].append(image.text)

                listeRES.append(dico)
        return listeRES

    security.declarePrivate('xpath')

    def xpath(self, xml, xpath):
        xpaths = xpath.split('/')
        xpathparent = '/'.join(xpaths[0:-1])
        if re.match(r"^@.*$", xpaths[-1]):
            parents = xml.findall(xpathparent)
            if len(parents) > 0:
                key = xpaths[-1][1:]
                if key in parents[0].attrib:
                    return parents[0].attrib[key]
        elif xpaths[-1] == "text()":
            parents = xml.findall(xpathparent)
            if len(parents) > 0:
                return parents[0].text
        elif re.match(r"^\[.*\]", xpaths[-1]):
            parents = xml.findall(xpathparent)
            if len(parents) > 0:
                return parents[int(xpaths[-1][1:-1])]
        else:
            return xml.findall(xpath)
        return None

    #plus d'info concernant un element
    def searchBUCatalog(self, termeRecherche):
        params = {"institution": self.getGenerique("etablissement"),
                    "onCampus": "false",
                    "query": "any,contains,%s" % termeRecherche,
                    "indx": "1",
                    "bulkSize": "10",
                    "dym": "true",
                    "lang": "fre"
                    }
        return self.requete("search/brief", params)

    #Ajoute un nouveau tag à la ressource
    def tagBU(self, ressource, tag, action):
        url_connexion = self.url_connexion
        detailRessource = ressource.split("-")
        url = "".join([url_connexion, "/tags/", action, "?value=", tag, "&userId=ecampus&docId=", detailRessource[2]])
        handle = urllib2.urlopen(url, timeout=50)
        rep = handle.read()
        #return rep
        return url

    #recupere les tags sur la ressource
    def recupTagBU(self, ressource):
        url_connexion = self.url_connexion
        detailRessource = ressource.split("-")
        url = "".join([url_connexion, "/tags/getTagsForRecord?docId=", detailRessource[2]])
        handle = urllib2.urlopen(url, timeout=50)
        rep = handle.read()
        dom = minidom.parseString(rep)
        retour = []
        for node in dom.getElementsByTagName('value'):
            retour.append(node.firstChild.data)
        return retour

    #renvoi sur le site de la BU
    def BUResult(self, termeRecherche):
        termeRecherche = self.supprimerAccent(termeRecherche)
        url_recherche = "".join([self.url_catalogue, "/primo_library/libweb/action/search.do?dscnt=0&vl%2814793452UI1%29=all_items&frbg=&scp.scps=&tab=default_tab&srt=rank&ct=search&mode=Basic&dum=true&indx=1&vl%289521613UI0%29=any&vl%28freeText0%29=", termeRecherche, "&fn=search&vid=", self.getGenerique("etablissement")])
        return url_recherche

    #Suggestions d’acquisitions
    def BUacquisition(self):
        url_acquisition = self.url_acquisition
        return url_acquisition

    def rechercherRecordById(self, recordid):
        params = {"institution": self.getGenerique("etablissement"),
                  "onCampus": "false",
                  "query": "rid,contains,%s" % recordid,
                  "indx": "1",
                  "bulkSize": "10",
                  "dym": "true",
                  "lang": "fre"}
        resultat = self.requete("search/brief", params)
        try:
            return resultat[0]
        except:
            return None

    #recupére differents éléments génériques defini par l'administrateur dans les configs Jalon
    def getGenerique(self, generique):
        return "UNS"
        portal_jalon_properties = self.portal_jalon_properties
        return portal_jalon_properties.getJalonProperty("etablissement")

    def supprimerAccent(self, ligne):
        """ supprime les accents du texte source """
        accents = {'a': ['à', 'ã', 'á', 'â'],
                   'e': ['é', 'è', 'ê', 'ë'],
                   'c': ['ç'],
                   'i': ['î', 'ï'],
                   'u': ['ù', 'ü', 'û'],
                   'o': ['ô', 'ö']}
        for (char, accented_chars) in accents.iteritems():
            for accented_char in accented_chars:
                ligne = ligne.replace(accented_char, char)
        return ligne