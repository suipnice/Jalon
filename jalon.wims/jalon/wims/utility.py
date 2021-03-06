# -*- coding: utf-8 -*-
""" WIMS Connector for Jalon LMS."""
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component import getUtility
from zope.interface import classProvides

from AccessControl import ClassSecurityInfo

from jalon.wims.interfaces.utility import IWims, IWimsLayout, IWimsClasse, IWimsModele

from OFS.SimpleItem import SimpleItem

# Imports
import urllib
import urllib2
import json
import xml.etree.ElementTree as ET
import HTMLParser

from jalon.content.content import jalon_utils
from DateTime import DateTime

# import pour l'envoi de mail :
from Products.CMFPlone.interfaces import IPloneSiteRoot


# Messages de debug :
from logging import getLogger
LOG = getLogger('[jalon.wims.utility]')
"""
# Log examples :
LOG.debug('debug message')
LOG.info('info message')
LOG.warn('warn message')
LOG.error('error message')
LOG.critical('critical message')
"""


def form_adapter(context):
    """Form Adapter."""
    return getUtility(IWims)


class Wims(SimpleItem):

    """Wims Utility."""

    implements(IWims)
    classProvides(
        IWimsLayout,
        IWimsClasse,
        IWimsModele,
    )
    security = ClassSecurityInfo()

    """
     ICI il serait interressant d'ajouter le parametre "timeout"
     aux propriétés du plug Wims pour pouvoir le regler en fonction
     de la reactivité du serveur WIMS, sans avoir à redémarrer.
    """

    # Parametres généraux
    timeout = 50
    url_connexion = FieldProperty(IWimsLayout['url_connexion'])
    login = FieldProperty(IWimsLayout['login'])
    password = FieldProperty(IWimsLayout['password'])
    classe_locale = FieldProperty(IWimsLayout['classe_locale'])
    nom_institution = FieldProperty(IWimsLayout['nom_institution'])

    donnees_classe = FieldProperty(IWimsClasse['donnees_classe'])
    donnees_superviseur = FieldProperty(IWimsClasse['donnees_superviseur'])
    donnees_exercice = FieldProperty(IWimsClasse['donnees_exercice'])

    qcmsimple = FieldProperty(IWimsModele['qcmsimple'])
    equation = FieldProperty(IWimsModele['equation'])
    texteatrous = FieldProperty(IWimsModele['texteatrous'])
    marqueruntexte = FieldProperty(IWimsModele['marqueruntexte'])
    marquerparpropriete = FieldProperty(IWimsModele['marquerparpropriete'])
    questiontextuelletolerante = FieldProperty(IWimsModele['questiontextuelletolerante'])
    taperlemotassocie = FieldProperty(IWimsModele['taperlemotassocie'])
    reordonner = FieldProperty(IWimsModele['reordonner'])
    correspondance = FieldProperty(IWimsModele['correspondance'])
    classerparpropriete = FieldProperty(IWimsModele['classerparpropriete'])
    vraifauxmultiples = FieldProperty(IWimsModele['vraifauxmultiples'])
    texteatrousmultiples = FieldProperty(IWimsModele['texteatrousmultiples'])
    qcmsuite = FieldProperty(IWimsModele['qcmsuite'])
    exercicelibre = FieldProperty(IWimsModele['exercicelibre'])

    #debug = []

    # Parametres globaux
    # session = None
    expiration_date = u"30000101"
    min_login_len = 4
    max_login_len = 24

    def getWimsProperty(self, key):
        u""" obtient les propriétés."""
        return getattr(self, "%s" % key)

    def setProperties(self, form):
        u""" modifie les propriétés."""
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "%s" % key, val.decode("utf-8"))

    def authUser(self, param):
        """demande a Wims d'ouvrir une session pour un utilisateur."""
        # Cette fonction ne renvoit pas un json, car elle peux etre utilisée pour tester si un utilisateur existe.
        param["quser"] = self.validerUserID(param["quser"])
        param["job"] = "authUser"
        return self.callJob(param)

    security.declarePrivate('convertirDate')

    def convertirDate(self, d, us=False):
        """convertit une date d au format us ou fr."""
        if not us:
            return DateTime(d).strftime("%d.%m.%Y - %Hh%M")
        else:
            return DateTime(d).strftime("%Y-%m-%d")

    def callJob(self, param):
        """fonction d'appel generique des jobs du module adm/raw de Wims."""
        param["module"] = "adm/raw"
        param["ident"] = self.login
        param["passwd"] = self.password
        param["rclass"] = self.classe_locale
        data = urllib.urlencode(param)
        #print "\nrequete WIMS envoyee : %s" % data
        try:
            req = urllib2.Request(self.url_connexion, data)
            handle = urllib2.urlopen(req, timeout=self.timeout)
            rep = handle.read()
        except IOError, e:
            rep = '{"status":"ERROR"'
            #--- Erreur HTTP ---
            #urllib2.URLError
            if hasattr(e, 'reason'):
                #print 'URLError ', e.reason
                # URLError peut survenir en cas de "Time out" Cela peut aussi bien provenir du client (modifier alors la valeur de timeout ci-dessus) que du serveur appelé.
                # Mais cela peux aussi survenir lorsqu'on envoi des parentheses mal fermées.
                rep = '%s,"type":"URLError","message":"%s","URL":"%s?%s"}' % (rep, e.reason, self.url_connexion, data)
            elif hasattr(e, 'code'):
                #-- HTTPError --
                # L'erreur HTTP 450 survient souvent lors de parenthese mal fermées detectées par WIMS
                rep = '%s,"type":"HTTPError","message":"%s","error_code":"%s"}' % (rep, self.string_for_json(e.read()), e.code)
            else:
                try:
                    message = e.read()
                except:
                    # Si l'exception ne peux etre lue, c'est probablement un timeout... (AttributeError: 'timeout' object has no attribute 'read')
                    message = str(e)
                rep = '%s,"type":"Unknown IOError","message":"%s"}' % (rep, self.string_for_json(message))
            #mail = rep.decode("iso-8859-1")
            #self.verifierRetourWims({"rep": mail.encode("utf-8"), "fonction": "jalon.wims/utility.py/callJob", "requete" : param})
        #print "--- REP Wims ---"
        #print rep
        #print "--- REP Wims (fin) ---"
        rep = rep.decode("iso-8859-1")
        return rep.encode("utf-8")

    def checkIdent(self, param):
        u"""verification de la validité des identifiants du plugin."""
        param['job'] = 'checkident'
        data = urllib.urlencode(param)
        retour = "OK"
        try:
            req = urllib2.Request("%s?%s" % (self.getURLWims(), data))
            handle = urllib2.urlopen(req)
            handle.read()
        except:
            retour = "Erreur HTTP"
        return retour

    def cleanClass(self, params):
        u"""Purge les activités de la classe param[qclass]."""
        # en entree : params = {"qclass": class_id, "code": authMember}
        params["job"] = "cleanclass"
        params["rclass"] = self.classe_locale

        rep = self.callJob(params)

        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/cleanClass", "requete": params})
        if rep["status"] == "OK":
            cleaned = rep["suppressed_users"]
        else:
            cleaned = None
        return {"status": rep["status"], "cleaned": cleaned, "message": rep["message"]}

    def creerClasse(self, param):
        """Creation d'une classe ou d'un groupement de classes WIMS."""
        #LOG.debug("** param[fullname] = %s" % param["fullname"])
        if not "titre_classe" in param:
            param["titre_classe"] = "Classes de %s" % param["fullname"]
        donnees_classe = self.donnees_classe % (param["titre_classe"].decode("utf-8"),
                                                self.nom_institution,
                                                param["fullname"].decode("utf-8"),
                                                param["auth_email"].decode("utf-8"),
                                                DateTime().strftime("%d%H%M%S"),
                                                param["type"].decode("utf-8"))

        firstname, lastname = param["fullname"].split(" ", 1)
        donnees_superviseur = self.donnees_superviseur % (lastname.decode("utf-8"), firstname.decode("utf-8"), DateTime().strftime("%d%H%M%S"))

        dico = {"job": "addclass", "code": param["authMember"], "data1": donnees_classe.encode("iso-8859-1", "replace"), "data2": donnees_superviseur.encode("iso-8859-1", "replace"), "qclass": param["qclass"]}

        rep = self.callJob(dico)

        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/creerClasse", "requete": dico})

        return rep

    def creerExercice(self, param):
        """Creation d'un exercice WIMS."""
        # Lorsque le parametre "sandbox" est activé, l'exercice n'est pas injecté
        # dans la classe, mais seulement dans un bac à sable pour compilation.

        #data = self.getAttribut(param["modele"])

        if "sandbox" in param:
            job = "testexo"
            del param["sandbox"]
        else:
            job = "addexo"

        #LOG.info("[creerExercice] param[source]=\n%s"%param["source"])
        dico = {"job": job, "code": param["authMember"], "data1": param["source"], "qexo": param["qexo"], "qclass": param["qclass"]}
        if "option" in param:
            dico["option"] = param["option"]
        #try:
        result = self.verifierRetourWims({"rep": self.callJob(dico), "fonction": "jalon.wims/utility.py/creerExercice", "requete": dico})
        #if job == "testexo":
        #    del param["data_q"]

        #except:
        #result={"status" : "ERROR","type": "JSON_DECODING", "infos":sys.exc_info()[0]}
        return result

    def creerFeuille(self, param):
        u"""ajoute une feuille d'entrainement à une classe Wims."""
        if param["qclass"] and param["qclass"] is not None:
            donnees_feuille = self.formaterDonnees(param)
            #modele = "expiration=%s\ntitle=%s\ndescription=%s"
            #donnees_feuille = modele % (self.expiration_date, param["title"].decode("utf-8"), param["description"].decode("utf-8"))
            requete = {"job": "addsheet", "code": param["authMember"], "data1": donnees_feuille.encode("iso-8859-1", "replace"), "qclass": param["qclass"]}
            rep = self.callJob(requete)
            rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/creerFeuille", "requete": requete})
            return rep
        else:
            return None

    def creerExamen(self, param):
        """Ajoute un examen a une classe wims."""
        #modele = "expiration=%s\ntitle=%s\ndescription=%s\nduration=%s\nattempts=%s\ncut_hours=%s\n"
        #donnees = modele % (self.expiration_date, param["title"].decode("utf-8"), param["description"].decode("utf-8"),
        #                    param["duration"], param["attempts"], param["cut_hours"].decode("utf-8"))
        donnees = self.formaterDonnees(param)
        requete = {"job": "addexam", "code": param["authMember"], "data1": donnees.encode("iso-8859-1", "replace"), "qclass": param["qclass"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/creerExamen", "requete": requete})
        return rep

    def creerUser(self, param):
        """Ajoute un utilisateur a une classe wims."""
        quser = self.validerUserID(param["quser"])
        try:
            data = "lastname=%s\nfirstname=%s\npassword=%s\n" % (param["lastname"].encode("iso-8859-1"), param["firstname"].encode("iso-8859-1"), DateTime().strftime("%d%H%M%S"))
        except:
            data = "lastname=%s\nfirstname=%s\npassword=%s\n" % (param["lastname"], param["firstname"], DateTime().strftime("%d%H%M%S"))
        requete = {"job": "adduser", "qclass": param["qclass"], "quser": quser, "data1": data, "code": quser}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/creerUser", "requete": requete})
        return rep

    def getAttribut(self, attribut):
        u"""renvoie l'attribut demandé."""
        return self.__getattribute__(attribut)

    def getURLWims(self):
        """construit et renvoie l'url d'appel au module adm/raw de wims."""
        # ici il faudra remplacer "lang=fr" par la langue d'affichage de Jalon.
        return "%s?lang=fr&module=adm/raw&ident=%s&passwd=%s" % (self.url_connexion, self.login, self.password)

    def getExercicesWims(self, param):
        """permet d'obtenir la liste des exercices d'une classe."""
        requete = {"job": "listExos", "code": param["authMember"], "qclass": param["qclass"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep,
                                       "fonction": "jalon.wims/utility.py/getExercicesWims",
                                       "requete": requete,
                                       "jalon_URL": param["jalon_URL"]
                                       })
        return rep

    def getNote(self, param):
        """permet d'obtenir la liste des notes d'un utilisateur param["quser"]."""
        requete = {"job": "getscore", "code": param["quser"], "qclass": param["qclass"], "quser": param["quser"]}

        # Si param["qsheet"] est précisé, on filtre les notes pour n'afficher que la feuille "qsheet"
        if "qsheet" in param:
            requete["qsheet"] = param["qsheet"]
        rep_wims = self.callJob(requete)
        #print "\nrep : %s\n" % rep_wims
        retour = json.loads(rep_wims)

        if retour["status"] != "OK":
                # Tant que l'etudiant n'a pas répondu à un exercice donné par le prof, WIMS donnera une erreur "user not present"
                # et Tant que l'etudiant n'aura pas répondu à un exercice de cette classe, WIMS donnera une erreur "does not participates..."
                # on n'enverra donc pas de message d'erreur dans ces 2 cas.
                if not ("not present in superclass" in retour["message"] or "does not participates to this subclass" in retour["message"]):
                    self.verifierRetourWims({"rep": rep_wims,
                                             "fonction": "jalon.wims/utility.py/getNote",
                                             "requete": requete,
                                             "jalon_request": param["jalon_request"]
                                             })
                    # Attention, il peut y avoir un decalage si une des feuilles precedente n'a pas ete activées...
                    # print "****\n  [Jalon.wims/utility] ERREUR WIMS : pas de notes pour la feuille demandee. \n rep = %s \n****" % rep
        return retour

    def injecter_exercice(self, param):
        """injecte tous les exercices d'une feuille dans un examen."""
        requete = {"job": "linksheet", "code": param["authMember"], "qclass": param["qclass"], "qexam": param["qexam"], "qsheet": param["qsheet"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/injecter_exercice", "requete": requete})
        return rep

    def lierExoFeuille(self, param):
        u"""Ajoute un exercice à une feuille."""
        listeExos = "&exo=".join(param["listeExos"])
        """
        Par défaut :
        donnees_exercice = module="classes/fr",
                           params=exo=listeExos,
                           &qnum=param["qnum"],
                           &qcmlevel="1",
                           &intro_qcmpresent="4",
                           &intro_presentsol="1",
                           &intro_check="1,2,4",
                           &intro_expert="yes",
                           &scoredelay="0",
                           points="10",
                           weight="1",
                           title=param["title"].decode("utf-8"),
                           description="")
        """
        intro_check = "1,2,4"

        #intro_check="3" affiche la bonne réponse en cas d'erreur ( à utiliser dans le cas des entrainements uniquement)
        if "afficher_reponses" in param and param["afficher_reponses"] is True:
            intro_check = "1,2,3,4"

        donnees_exercice = self.donnees_exercice % (u"classes/fr",
                                                    listeExos,
                                                    param["qnum"],
                                                    "1",
                                                    "4",
                                                    "1",
                                                    intro_check,
                                                    "yes",
                                                    "0",
                                                    "10",
                                                    "1",
                                                    param["title"].decode("utf-8"),
                                                    "")
        requete = {"job": "putexo", "code": param["authMember"], "data1": donnees_exercice.encode("iso-8859-1", "ignore"),
                   "qclass": param["qclass"], "qsheet": param["qsheet"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/lierExoFeuille", "requete": requete})
        return rep

    def modifierExoFeuille(self, param):
        """modifie l'exercice d'une feuille."""
        donnees_exercice = self.donnees_exercice % ("",
                                                    "",
                                                    "",
                                                    "",
                                                    "",
                                                    "",
                                                    "",
                                                    "",
                                                    "",
                                                    "",
                                                    param["weight"],
                                                    param["title"].decode("utf-8"),
                                                    "")
        requete = {"job": "modexosheet", "code": param["authMember"], "data1": donnees_exercice.encode("iso-8859-1", "ignore"),
                   "qclass": param["qclass"], "qsheet": param["qsheet"], "qexo": param["qexo"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/modifierExoFeuille", "requete": requete})
        return rep

    def retirerExoFeuille(self, param):
        u""" Retire l'exercice param["qexo"] de la feuille param["qsheet"]."""
        requete = {"job": "modexosheet", "code": param["authMember"], "option": "remove forced",
                   "qclass": param["qclass"], "qsheet": param["qsheet"], "qexo": param["qexo"]}
        #print "jalon.wims/retirerExoFeuille : Suppression de l'exercice %s" % param["qexo"]
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep,
                                       "fonction": "jalon.wims/utility.py/retirerExoFeuille",
                                       "requete": requete,
                                       "jalon_URL": param["jalon_URL"]
                                       })
        return rep

    def monterExoFeuille(self, param):
        """Change l'ordre des exercices de la feuille param["qsheet"], en remontant l'exercice param["qexo"] d'un cran."""
        # pour l'instant, cette fonction n'est pas utilisée.
        requete = {"job": "modexosheet", "code": param["authMember"], "option": "moveup",
                   "qclass": param["qclass"], "qsheet": param["qsheet"], "qexo": param["qexo"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/modifierExoFeuille", "requete": requete})
        return rep

    def formaterDonnees(self, param):
        u"""fournit la variable "data1" des propriétés d'une autoeval au bon format."""
        donnees = []

        #donnees Communes
        if "status" in param:
            donnees.append("status=%s" % param["status"])

        if "description" in param:
            description = param["description"].replace('\r', ' ')
            description = description.strip()
            description = " <br/>".join(description.split("\n"))
            donnees.append(u"description=%s" % description.decode("utf-8"))

        if "title" in param:
            title = param["title"].replace('\n', ' ').replace('\r', ' ')
            title = title.strip()
            donnees.append(u"title=%s" % title.decode("utf-8"))

        #donnees exclusives aux examens
        if "duration" in param:
            # dans modexam, duration_and_attempts sont dans une seule variable, alors que dans addexam ils sont séparés.
            # on envoit donc les 2 pour être sûr.
            donnees.append(u"duration=%s" % param["duration"])
            donnees.append(u"attempts=%s" % param["attempts"])
            donnees.append(u"duration_and_attempts=%s %s" % (param["duration"], param["attempts"]))
            donnees.append(u"cut_hours=%s" % param["cut_hours"].decode("utf-8"))

        donnees.append("expiration=%s" % self.expiration_date)
        return u"\n".join(donnees)

    def modifierFeuille(self, param):
        """Modifie les parametres d'une feuille."""
        donnees_feuille = self.formaterDonnees(param)

        requete = {"job": "modsheet", "code": param["authMember"], "data1": donnees_feuille.encode("iso-8859-1", "replace"),
                   "qclass": param["qclass"], "qsheet": param["qsheet"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/modifierFeuille", "requete": requete})
        return rep

    def modifierExamen(self, param):
        """Modifie les parametres d'un examen."""
        donnees = self.formaterDonnees(param)

        requete = {"job": "modexam", "code": param["authMember"], "data1": donnees.encode("iso-8859-1", "replace"),
                   "qclass": param["qclass"], "qexam": param["qexam"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/modifierExamen", "requete": requete})
        return rep

    def reordonnerFeuille(self, param):
        u""" reordonnerFeuille :  reordonne les exercices d'une feuille.

        # TODO : Le plus simple sera surement de procéder ainsi :
        #  1. stockge des infos des exos de la feuille
        #  2. suppression des exos de la feuille
        #  3. ajouter les exos de la feuille dans le nouvel ordre

        """
        #  1. stockge des infos des exos de la feuille
        infos_feuille = "liste des infos des exos de la feuille"
        nbexos = len(infos_feuille)
        #  2. suppression des exos de la feuille
        for exo_id in range(nbexos):
            param["qexo"] = exo_id + 1
            self.retirerExoFeuille(param)

        #  3. ajout des exos de la feuille dans le nouvel ordre
        for exo_id in range(nbexos):

            param = infos_feuille[exo_id]
            self.lierExoFeuille(param)

    def string_for_json(self, chaine):
        """Supprime tous les caracteres indesirables d'une chaine pour l'integrer au format JSON (quotes, retour chariot, barre oblique )."""
        return chaine.replace('\"', "'").replace('\n', "").replace("\\", "").replace("\t", "\\t")

    def validerUserID(self, user_ID):
        u"""Verification de conformité de l'id d'un utilisateur WIMS."""
        # Il doit avoir une taille mini et maxi et ne contenir aucun caractere interdit
        if user_ID is None:
            return None
        else:
            retour = user_ID.strip()

            # on prend du premier au "taille max" caractere
            retour = retour[:self.max_login_len]

            if len(retour) < self.min_login_len:
                retour = "%s@__@" % retour

        return retour

    def importerHotPotatoes(self, folder, member_auth, import_file):
        u"""import d'exercices Hotpotatoes dans une activité WIMS d'un cours.."""
        h = HTMLParser.HTMLParser()
        tree = ET.parse(import_file)
        root = tree.getroot()
        #groupe_title = h.unescape(root.find('./data/title').text).encode("utf-8")
        questions = root.find('./data/questions')
        questions_list = []
        i = 1
        for question_record in questions:
            question_dict = {"good_rep": [],
                             "bad_rep":  []}
            question_dict["title"] = "%s : %s" % (import_file.filename[:-4], str(i))
            for answer in question_record.find('answers'):
                answer_text = answer.find('text').text
                if answer_text:
                    answer_text = answer_text.replace("&#x2019;", "'")
                    if int(answer.find("correct").text):
                        question_dict["good_rep"].append(h.unescape(answer_text).encode("utf-8"))
                    else:
                        question_dict["bad_rep"].append(h.unescape(answer_text).encode("utf-8"))

            obj_id = folder.invokeFactory(type_name='JalonExerciceWims', id="%s-%s-%s-%s" % ("qcmsimple", member_auth, DateTime().strftime("%Y%m%d%H%M%S"), i))
            question_dict["id_jalon"] = obj_id
            questions_list.append(question_dict)
            obj = getattr(folder, obj_id)
            ennonce = question_record.find('question').text
            #if "#x2019;" in ennonce:
            #    print ennonce
            ennonce = ennonce.replace("&#x2019;", "'")

            param_wims = {"title":            question_dict["title"],
                          "enonce":           h.unescape(ennonce).encode("utf-8"),
                          "bonnesrep":        "\n".join(question_dict["good_rep"]),
                          "mauvaisesrep":     "\n".join(question_dict["bad_rep"]),
                          "tot":              "5",
                          "givetrue":         "2",
                          "minfalse":         "0",
                          "options":          ["checkbox", "split"],
                          "feedback_general": "",
                          "feedback_bon":     "",
                          "feedback_mauvais": ""}
            wims_response = obj.addExoWims(obj_id, param_wims["title"], member_auth, "qcmsimple", param_wims)
            i = i + 1

            if not("status" in wims_response):
                # La creation a planté (Cause : modele inconnu ?)
                folder.manage_delObjects(ids=[obj_id])
                #self.plone_log("unknown_model")
            else:
                #L'appel à WIMS s'est bien passé, on applique les modifications à l'objet Jalon
                if wims_response["status"] == "OK":
                    obj.setProperties({"Title": question_dict["title"],
                                       "Modele": "qcmsimple",
                                       })
        #self.plone_log(questions_list)
        return questions_list

    def verifierRetourWims(self, params):
        """verifie le bon retour d'un appel Wims, et envoie un mail d'erreur si besoin."""
        # rep doit etre une chaine de caracteres au format json.
        if "fonction" in params:
            fonction = params["fonction"]
        else:
            fonction = ""

        if "message" in params:
            message = params["message"]
        else:
            message = ""

        if "requete" in params:
            requete = params["requete"]
            if "passwd" in requete:
                requete['passwd'] = "******"
        else:
            requete = ""

        if "jalon_URL" in params:
            jalon_URL = params["jalon_URL"]
        else:
            jalon_URL = ""

        if "jalon_request" in params:
            jalon_request = params["jalon_request"]
        else:
            jalon_request = ""

        rep = params["rep"]

        portal = getUtility(IPloneSiteRoot)
        serveur = portal.getProperty("title")
        mail_erreur = {"objet": "[%s] Erreur WIMS (%s)" % (serveur, fonction)}
        try:
            rep = json.loads(rep)
        except ValueError, e:
            # ValueError : No JSON object could be decoded
            # cas ou WIMS n'as pas repondu un json correct.
            # mail_erreur["message"] = "<h2>Reponse WIMS :</h2><pre>%s \n</pre>\n<hr/> <h4>ValueError Exception : </h4> <pre>%s</pre> " % (rep,e)
            # jalon_utils.envoyerMailErreur(mail_erreur)
            # print "@@@@@@ ==> envoi d'un mail d'erreur WIMS a %s" % mail_erreur["a"]
            message = "<p>%s</p><p>Reponse originale de WIMS : %s</p>" % (message, rep)
            rep = {"status": "ERROR", "message": "No JSON object could be decoded : %s" % e, "error_type": "Exception Raised (ValueError)"}
        except TypeError, e:
            # A priori si on tombe dans ce cas, c'est une erreur d'appel de "verifierRetourWims", a qui on a donné un json au lieu d'une string.
            message = "<p>%s</p><p>Reponse originale de WIMS : %s</p>" % (message, rep)
            rep = {"status": "ERROR", "message": "Type Error : %s" % e, "error_type": "Exception Raised (TypeError)"}

        if rep["status"] == "ERROR":
            if not "message" in rep:
                rep["message"] = "aucun"
            if message == "":
                message = "aucune info supplémentaire"
            mail_erreur["message"] = "<h1>Retour d'erreur de WIMS</h1>"
            if jalon_URL != "":
                mail_erreur["message"] = "%s <h2>Objet Jalon concern&eacute;&nbsp;:</h2><p>%s<br/><em>nb : la page de l'erreur peut etre diff&eacute;rente. Voir le REQUEST complet pour plus d'infos.</em></p>" % (mail_erreur["message"], jalon_URL)
            mail_erreur["message"] = "%s <h2>Fonction appelante :</h2><p>%s</p>" % (mail_erreur["message"], fonction)
            mail_erreur["message"] = '%s <h2>Requ&ecirc;te effectu&eacute;e :</h2><pre>%s</pre>' % (mail_erreur["message"], requete)
            mail_erreur["message"] = "%s <h2>Message d'erreur :</h2><pre>%s</pre>" % (mail_erreur["message"], rep["message"])
            mail_erreur["message"] = "%s <h2>Informations sur l'erreur</h2><pre>%s</pre>" % (mail_erreur["message"], message.decode("utf-8"))
            mail_erreur["message"] = "%s <h2>R&eacute;ponse WIMS :</h2><div><pre>%s</pre></div>" % (mail_erreur["message"], rep)

            if jalon_request != "":
                mail_erreur["message"] = "%s <hr/><h2>REQUEST Jalon :</h2><div>%s</div>" % (mail_erreur["message"], jalon_request)

            jalon_utils.envoyerMailErreur(mail_erreur)
            # print "@@@@@@ ==> envoi d'un mail d'erreur WIMS "

            # NB : dans le cas ou fonction == "creerExercice" and "error_code" in rep and rep["error_code"]=="450",
            #   on pourrait ne pas envoyer de mail : c'est en general une parenthese mal fermée

        return rep
