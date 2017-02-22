# -*- coding: utf-8 -*-
"""Adobe Connect Connector for Jalon LMS."""
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component import getUtility
from zope.interface import classProvides

from AccessControl import ClassSecurityInfo

from jalon.connect.interfaces.utility import IConnect, IConnectLayout, IConnectModele

from OFS.SimpleItem import SimpleItem

# Imports
import re
import urllib
import urllib2
import sys

from xml.etree.ElementTree import XML
from DateTime import DateTime
from urlparse import urlparse
from time import strftime, gmtime

from zope.interface import Invalid

from logging import getLogger
LOG = getLogger('[Jalon.Connect]')


def form_adapter(context):
    """Form Adapter."""
    return getUtility(IConnect)


class Connect(SimpleItem):
    u"""
    Connect Utility.

    Fournit les fonctions necessaires pour interagir avec des réunions Adobe Connect.

    """

    implements(IConnect)
    classProvides(
        IConnectLayout,
        IConnectModele,
    )
    security = ClassSecurityInfo()

    # Parametres généraux
    url_connexion = FieldProperty(IConnectLayout['url_connexion'])
    login = FieldProperty(IConnectLayout['login'])
    password = FieldProperty(IConnectLayout['password'])
    version = FieldProperty(IConnectLayout['version'])
    etablissement = FieldProperty(IConnectLayout['etablissement'])
    num_serveur = FieldProperty(IConnectLayout['num_serveur'])

    dossiers = FieldProperty(IConnectModele['dossiers'])

    # debug = []
    # Parametres spécifiques
    session = None

    def getAttribut(self, param):
        """getAttribut renvoit l'attribut param["attribut"]."""
        return self.__getattribute__(param["attribut"])

    def getConnectProperty(self, key):
        """get Connect properties."""
        return getattr(self, "%s" % key)

    def setProperties(self, form):
        """set properties."""
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "%s" % key, val.decode("utf-8"))

    # ## METHODES PUBLIQUES ###########################################################

    def creerUser(self, params):
        """Cree un utilisateur connect.

        Arguments:
        params -- un dictionnaire contenant les attributs de l'utilisateur.

        """
        # print params
        # Création du compte Connect de l'utilisateur
        firstname, lastname = params["fullname"].split(" ", 1)
        rep = self.requete({'action': 'principal-update',
                            'first-name': firstname,
                            'last-name': lastname,
                            'email': params['email'],
                            'login': params['userid'],
                            'password': params['password'],
                            'type': 'user',
                            'send-email': 'false',
                            'has-children': '0',
                            }, "principal/[0]")

        if not rep["error"]:
            # Ajout de l'utilisateur au groupe "hotes de réunion" supprimé => inutile (les hotes de réunions peuvent créer de nouvelles réunions)

            # Recherche de l'ID de l'utilisateur
            idUser = rep["response"].attrib["principal-id"]

            # Recherche du groupe des hotes de réunions
            rep = self.requete({'action': 'principal-list', 'filter-type': 'live-admins'}, "principal-list/principal/[0]")
            idGroupe = rep["response"].attrib["principal-id"]

            # Ajout de l'utilisateur au groupe des hotes de réunions
            rep = self.requete({'action': 'group-membership-update', 'group-id': idGroupe, 'principal-id': idUser, 'is-member': 'true'})

        return rep["error"]

    def creerReunion(self, params):
        """creerReunion."""
        # print "creerReunion"
        # Recherche de l'id et du dossier de l'utilisateur
        idUser = self.rechercherIdUser(params["userid"])
        # print "idUser : %s" % str(idUser)
        idFolder = self.rechercherDossierUser(params["userid"], "user-meetings")
        # print "idFolder : %s" % str(idFolder)

        if idUser and idFolder:
            # Création des infos de la réunion
            titre = url = None
            if params["repertoire"] == "Webconference":
                titre = " ".join(["Réunion de", params["fullname"], "(%s)" % self.etablissement.encode('utf8')])
                url = params["userid"]
            if params["repertoire"] == "Sonorisation":
                titre = " ".join(["Sonorisation de", params["fullname"], "(%s)" % self.etablissement.encode('utf8')])
                url = params["userid"] + "sonorisation"

            # Supprime les caracteres non alpha-num
            url = url.replace("@", "")
            url = url.replace(".", "")
            url = url.replace("-", "")
            url = url.replace("_", "")

            # Création de la réunion
            rep = self.requete({
                'action': 'sco-update',
                'type': 'meeting',
                'name': titre,
                'url-path': url,
                'folder-id': idFolder,
                'source-sco-id': params["modele"],
            }, "sco/[0]")

            if not rep["error"]:
                # Ajout de l'utilisateur comme hôte de la réunion
                meeting = rep["response"]
                idReunion = meeting.attrib["sco-id"]
                urlReunion = self.xpath(meeting, "url-path/[0]").text
                titleReunion = self.xpath(meeting, "name/[0]").text.encode("utf-8")

                # print "@@@ AJOUT HOTE"
                # print idReunion
                rep = self.requete({'action': 'permissions-update',
                                    'principal-id': idUser,
                                    'acl-id': idReunion,
                                    'permission-id': 'host'})
                # print rep
                if not rep["error"]:
                    # print "@@@ NOUVELLE REUNION"
                    # print {"id" : idReunion, "title" : titleReunion, "url" : self.urlAbsolu(urlReunion) }
                    # Réunion publique
                    rep = self.requete({'action': 'permissions-update',
                                        'acl-id': idReunion,
                                        'principal-id': 'public-access',
                                        'permission-id': 'view-hidden'})
                    if not rep["error"]:
                        return {"id": idReunion,
                                "title": titleReunion,
                                "url": self.urlAbsolu(urlReunion)}
            else:
                raise Invalid(u"Connect creerReunion : %s " % str(rep["error"]))
        return None

    def majPasswordUser(self, params):
        """maj Password User."""
        # LOG.info("majPasswordUser")
        userid = self.rechercherIdUser(params["userid"])
        return self.requete({'action': 'user-update-pwd', 'user-id': userid, 'password': params["password"], 'password-verify': params["password"]}, 'status/code')

    def rechercherReunions(self, params):
        """rechercher Reunions."""
        # LOG.info("@@@ RECHERCHER REUNIONS")

        # Vérification des paramètres
        if "login" in params:
            login = params["login"]
            # pwd = params["pass"]

            # Connexion admin
            if self.connexion():
                # Recherche du dossier de l'utilisateur
                idFolder = self.rechercherDossierUser(login, "user-meetings")
                if not idFolder:
                    return None

                # Recherche des réunions dans le dossier de l'utilisateur
                meetings = self.requete({'action': 'sco-contents',
                                         'sco-id': idFolder,
                                         'filter-type': 'meeting'},
                                         'scos/sco')["response"]
                modeles = {}
                for meeting in meetings:
                    # Recherche du modèle
                    modele = meeting.attrib["source-sco-id"]
                    if modele not in modeles:
                        modeles[modele] = []
                        url = self.xpath(meeting, "url-path/[0]").text
                        modeles[modele].append({"id": meeting.attrib["sco-id"],
                                                "title": self.xpath(meeting, "name/[0]").text.encode("utf-8"),
                                                "url": self.urlAbsolu(url),
                                                })
                        # print "@@@ REUNION %s" % str({"id": meeting.attrib["sco-id"], "title": self.xpath(meeting, "name/[0]").text.encode("utf-8"),"url": self.urlAbsolu(url),})
                # print "@@@ REUNIONS"

                if params['modele'] in modeles:
                    # print modeles[params['modele']]
                    return modeles[params['modele']]
                else:
                    # print modeles
                    return None
        return None

    def rechercherEnregistrements(self, params):
        """recherche les enregistrements."""
        # LOG.info("rechercherEnregistrements")

        rep = self.requete({'action': 'sco-contents',
                            'sco-id': params['id'],
                            'filter-icon': 'archive',
                            'sort-date-created': 'desc'}, "scos/sco")
        if not rep["error"]:
            e = []
            # LOG.info("--Reponse de Connect : %s" % rep["response"])
            version = int(self.version)
            # LOG.info("--CONNECT version=%s" % version)
            for enregistrement in rep["response"]:
                url = self.xpath(enregistrement, "url-path/[0]").text
                # LOG.info(url)
                # Conversion de la durée
                if version < 9:
                    duree = self.xpath(enregistrement, "duration/[0]")
                    if duree is not None:
                        duree = duree.text
                else:
                    duree = enregistrement.attrib["duration"]

                # Exclut les enregistrements sans durée (en cours)
                if duree:
                    idEnregistrement = enregistrement.attrib["sco-id"]
                    if version < 9:
                        duree_f = self.convertirDuree(duree)
                    else:
                        duree_f = strftime('%Hh%Mm%Ss', gmtime(int(duree)))

                    # Enregistrement public
                    rep = self.requete({'action': 'permissions-update',
                                        'acl-id': idEnregistrement,
                                        'principal-id': 'public-access',
                                        'permission-id': 'view'})

                    # Conversion de la date de création
                    created = self.xpath(enregistrement, "date-created/[0]").text
                    created_f = self.convertirDate(created)
                    created_us = self.convertirDate(created, us=True)

                    e.append({"id": "%s-s%s" % (idEnregistrement, self.num_serveur),
                              "title": self.xpath(enregistrement, "name/[0]").text.encode("utf-8"),
                              "url": self.urlAbsolu(url),
                              "created": created_f,
                              "dateUS": created_us,
                              "duration": duree_f,
                              })
            return e
        # Quand la ressource "sco-id demandee n'existe pas, connect8 peut renvoyer <status code="no-access" subcode="denied"/>
        LOG.error("reunion : %s -- retour : %s " % (params['id'], rep["error"]))
        return []

    def genererSessionUser(self, params):
        """generer Session User."""
        # LOG.info("genererSessionUser")
        url = "%s?action=login&login=%s&password=%s" % (self.url_connexion, params["userid"], params["password"])
        req = urllib2.Request(url)
        handle = urllib2.urlopen(req)
        cookie = handle.info()["Set-Cookie"]
        tab = cookie.split(";")
        return tab[0].split("=")[1]

    # ## METHODES PRIVEES ###########################################################
    # security.declarePrivate('connexion')

    def connexion(self, param=None):
        """connexion."""
        # LOG.info("Jalon.Connect[connexion]")

        # Ré-init de la session
        self.session = None

        # Recherche du numéro de session
        rep = self.requete({"action": "common-info"})
        if not rep["error"]:
            # Connection admin
            rep = self.requete({'action': 'login',
                                'login': self.login,
                                'password': self.password})
            return not rep["error"]
        # Si erreur
        raise Invalid(u"Connexion Connect : %s " % str(rep))

    security.declarePrivate('rechercherIdUser')

    def rechercherIdUser(self, loginUser):
        """rechercher Id User."""
        rep = self.requete({'action': 'principal-list',
                            'filter-login': loginUser
                            }, "principal-list/principal/[0]")
        if not rep["error"]:
            return rep["response"].attrib["principal-id"]
        return None

    security.declarePrivate('rechercherShortcuts')

    def rechercherShortcuts(self, typesShortcuts):
        """Recherche des raccourcis des dossiers."""
        shortcuts = self.requete({'action': 'sco-shortcuts'}, "shortcuts/sco")
        s = []
        for typeShortcut in typesShortcuts:
            try:
                for shortcut in shortcuts["response"]:
                    # Recherche du dossier des reunions
                    if shortcut.attrib["type"] == typeShortcut:
                        s.append(shortcut.attrib["sco-id"])
            except:
                raise Invalid(u"shortcuts : %s" % str(shortcuts))
        return s

    security.declarePrivate('rechercherShortcuts')

    def rechercherDossierUser(self, login, shortcut):
        """rechercher Dossier User."""
        # Recherche du raccourci
        idShortcut = self.rechercherShortcuts([shortcut])[0]

        # Recherche du dossier de l'utilisateur
        folder = self.requete({'action': 'sco-contents',
                               'sco-id': idShortcut,
                               'filter-name': login},
                              "scos/sco/[0]")["response"]
        if folder is not None:
            return folder.attrib["sco-id"]
        return None

    security.declarePrivate('supprimerEnregistrement')

    def supprimerEnregistrement(self, params):
        """supprimer Enregistrement."""
        # print params["idEnregistrement"]
        rep = self.requete({'action': 'sco-delete', 'sco-id': params["idEnregistrement"]})
        return not rep["error"]

    # ## UTILITAIRES ###########################################################
    security.declarePrivate('requete')

    def requete(self, params, xpath=None):
        """requete."""
        # LOG.info("## requete ##")
        # Ajout du n° de session aux params
        if self.session is not None:
            params['session'] = self.session
            # LOG.info("--session = %s" % params['session'])
        # Requete au serveur
        data = urllib.urlencode(params)
        req = urllib2.Request("%s?%s" % (self.url_connexion, data))
        # LOG.info("REQUETE : %s?%s" % (self.url_connexion, data))
        try:
            handle = urllib2.urlopen(req)
            rep = handle.read()
        except:
            # Erreur HTTP
            raise Invalid(u"HTTP ; response : None ; error : %s" % str(sys.exc_info()))
        # LOG.info("REPONSE : %s" % rep)
        # Conversion XML
        try:
            xml = XML(rep)
        except:
            # Erreur XML
            raise Invalid(u"XML ; response : None ; error : %s" % str(sys.exc_info()))
        # Analyse de la réponse
        error = self.chercherErreur(xml)
        if not error:
            # print tostring(xml)
            self.analyserReponse(params, xml)
            # Extraction si necessaire
            if xpath:
                xml = self.xpath(xml, xpath)
                if xml is None:
                    error = "absence de resultat xpath"
            # Pas d'erreur, renvoie réponse
            return {"response": xml, "error": error}
        elif "error" in error:
            return {"response": xml, "error": error}
        else:
            # Si erreur, renvoie réponse+erreur
            raise Invalid(u"Erreur Connect; response : %s ; error : %s" % (rep, str(sys.exc_info())))

    security.declarePrivate('chercherErreur')

    def chercherErreur(self, xml):
        """chercher Erreur."""
        # LOG.info("[chercherErreur]")
        # Recherche du statut
        statut = self.xpath(xml, "status/@code")
        # LOG.info("-- STATUT : %s" % statut)

        if statut == "invalid":
            field = self.xpath(xml, "status/invalid/@field")
            subcode = self.xpath(xml, "status/invalid/@subcode")
            LOG.error("ERREUR Connect / %s : %s" % (field, subcode))
            return "%s : %s" % (field, subcode)
        elif statut == "no-access":
            subcode = self.xpath(xml, "status/@subcode")
            LOG.error("ERREUR Connect / %s : %s" % (statut, subcode))
            return {"error": "%s : %s" % (statut, subcode)}
        else:
            return None

    security.declarePrivate('analyserReponse')

    def analyserReponse(self, params, xml):
        """analyser Reponse."""
        # Recherche du n° de session
        if not self.session and params['action'] == 'common-info':
            self.session = self.xpath(xml, "common/cookie/text()")
            # print "--- SESSION : %s" % self.session

    security.declarePrivate('xpath')

    def xpath(self, xml, xpath):
        """xpath."""
        # Conversion en liste
        xpaths = xpath.split('/')
        xpathparent = '/'.join(xpaths[0:-1])
        # Recherche d'un attribut ( .../@attr )
        if re.match(r"^@.*$", xpaths[-1]):
            parents = xml.findall(xpathparent)
            if len(parents) > 0:
                key = xpaths[-1][1:]
                if key in parents[0].attrib:
                    return parents[0].attrib[key]
        # Recherche du contenu ( .../text() )
        elif xpaths[-1] == "text()":
            parents = xml.findall(xpathparent)
            if len(parents) > 0:
                return parents[0].text
        # Recherche du n-ieme node ( .../[n] )
        elif re.match(r"^\[.*\]", xpaths[-1]):
            parents = xml.findall(xpathparent)
            if len(parents) > 0:
                return parents[int(xpaths[-1][1:-1])]
        # Recherche d'une liste de nodes
        else:
            return xml.findall(xpath)
        return None

    security.declarePrivate('urlAbsolu')

    def urlAbsolu(self, url, session=None):
        """urlAbsolu."""
        o = urlparse(self.url_connexion)
        # return "%s://%s%s%s" % (o.scheme, o.netloc, url, "?session=%s" % self.session if session else "")
        return "%s://%s%s%s" % (o.scheme, o.netloc, url, "?session=%s" % session if session else "")
        # A faire : generer session user

    security.declarePrivate('convertirDate')

    def convertirDate(self, d, us=False):
        """convertirDate."""
        if not us:
            return DateTime(d).strftime("%d.%m.%Y - %Hh%M")
        else:
            return DateTime(d).strftime("%Y-%m")

    security.declarePrivate('convertirDuree')

    def convertirDuree(self, d):
        """convertirDuree."""
        if d:
            m = re.match(r"(\d{2}):(\d{2}):(\d{2})\.\d{3}", d)
            return "%sh%sm%ss" % m.groups()
        else:
            return "-"
