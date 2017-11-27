# -*- coding: utf-8 -*-
"""WIMS Connector for Jalon LMS."""
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.component import getUtility
from zope.interface import classProvides

from AccessControl import ClassSecurityInfo

from jalon.wims.interfaces.utility import IWims, IWimsLayout, IWimsClasse
from jalon.content import contentMessageFactory as _

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

    # Parametres globaux
    expiration_date = u"30000101"
    min_login_len = 4
    max_login_len = 24

    modele_wims = {"qcmsimple":                  "Question simple",
                   "equation":                   "Equation",
                   "texteatrous":                "Texte a trous",
                   "marqueruntexte":             "Marquer un texte",
                   "marquerparpropriete":        "Marquer par propriete",
                   "questiontextuelletolerante": "Question textuelle tolerante",
                   "taperlemotassocie":          "Taper le mot associe",
                   "reordonner":                 "Reordonner",
                   "correspondance":             "Correspondance",
                   "classerparpropriete":        "Classer par propriete",
                   "vraifauxmultiples":          "Vrai / Faux multiples",
                   "texteatrousmultiples":       "Textes a trous multiples",
                   "exercicelibre":              "Exercice libre (mode brut)",
                   "qcmsuite":                   "QCM à la suite",
                   "externe":                    "Exercice de la base WIMS"}

    def getWimsProperty(self, key):
        u"""Obtient les propriétés."""
        return getattr(self, "%s" % key)

    def setProperties(self, form):
        u"""Modifie les propriétés."""
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "%s" % key, val.decode("utf-8"))

    def authUser(self, param):
        """Demande a Wims d'ouvrir une session pour un utilisateur."""
        # Cette fonction ne renvoit pas un json, car elle peux etre utilisée pour tester si un utilisateur existe.
        param["quser"] = self.validerUserID(param["quser"])
        param["job"] = "authUser"
        return self.callJob(param)

    security.declarePrivate('convertirDate')

    def convertirDate(self, d, us=False):
        """Convertit une date d au format us ou fr."""
        if not us:
            return DateTime(d).strftime("%d.%m.%Y - %Hh%M")
        else:
            return DateTime(d).strftime("%Y-%m-%d")

    def callJob(self, param):
        """Appel generique des jobs du module adm/raw de Wims."""
        param["module"] = "adm/raw"
        param["ident"] = self.login
        param["passwd"] = self.password
        param["rclass"] = self.classe_locale
        data = urllib.urlencode(param)
        # print "\nrequete WIMS envoyee : %s" % data
        try:
            req = urllib2.Request(self.url_connexion, data)
            handle = urllib2.urlopen(req, timeout=self.timeout)
            # geturl() fournit la véritable url obtenue, dans le cas d'une redirection par exemple.
            # get_url = handle.geturl()
            rep = handle.read()
            rep = rep.decode("iso-8859-1")
        except IOError, e:

            try:
                error_body = e.read()
                error_body = error_body.decode("iso-8859-1")
            except AttributeError:
                # Si l'exception ne peux etre lue, c'est probablement un timeout...
                # (AttributeError: 'timeout' object has no attribute 'read')
                error_body = str(e)
            error_body = self.string_for_json(error_body)

            asked_url = "%s?%s" % (self.url_connexion, data)
            rep = '{"status":"ERROR", "URL": "%s"' % asked_url

            if hasattr(e, 'code'):
                # -- HTTPError --
                # L'erreur HTTP 450 survient souvent lors de parentheses mal fermées detectées par WIMS
                # Mais elle peut également survenir quand la taille d'une variable a dépassé la limite de WIMS
                rep = '%s, "error_code": "%s"' % (rep, e.code)

            if hasattr(e, 'reason'):
                # -- URLError --
                # URLError peut survenir en cas de :
                #  * "Time out" Cela peut aussi bien provenir du client (modifier alors la valeur de timeout ci-dessus) que du serveur appelé.
                #  * ou lorsqu'on envoi des parentheses mal fermées. (reason = WIMS User Error)
                #  * ou lorsque le serveur WIMS est en maintenance. (reason = WIMS Interruption)
                #  * ou lorsque la taille des données envoyées à WIMS etait trop grosse et a été tronquée : WIMS indique donc que les parentheses sont mal fermées.
                rep = '%s, "message": "%s"' % (rep, e.reason)

            rep = '%s, "error_body": "%s"}' % (rep, error_body)
            # mail = rep.decode("iso-8859-1")
            # self.verifierRetourWims({"rep": mail.encode("utf-8"), "fonction": "jalon.wims/utility.py/callJob", "requete" : param})
        # print "--- REP Wims ---"
        # print rep
        # print "--- REP Wims (fin) ---"

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

        rep = self.callJob(params)

        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/cleanClass", "requete": params})
        if rep["status"] == "OK":
            cleaned = rep["suppressed_users"]
        else:
            cleaned = None
        return {"status": rep["status"], "cleaned": cleaned, "message": rep["message"]}

    def creerClasse(self, param):
        """Creation d'une classe ou d'un groupement de classes WIMS."""
        # LOG.info("---creerClasse---")
        if "titre_classe" not in param:
            param["titre_classe"] = "Classes de %s" % param["fullname"]
        # Il faut supprimer les éventuels parenthèses/accolades/crochets du titre de la classe :
        param["titre_classe"] = self.string_for_wims(param["titre_classe"])
        donnees_classe = self.donnees_classe % (param["titre_classe"].decode("utf-8"),
                                                self.nom_institution,
                                                param["fullname"].decode("utf-8"),
                                                param["auth_email"].decode("utf-8"),
                                                DateTime().strftime("%d%H%M%S"),
                                                param["type"].decode("utf-8"))

        firstname, lastname = param["fullname"].split(" ", 1)
        donnees_superviseur = self.donnees_superviseur % (lastname.decode("utf-8"),
                                                          firstname.decode("utf-8"),
                                                          DateTime().strftime("%d%H%M%S"))

        dico = {"job": "addclass",
                "code": param["authMember"],
                "data1": donnees_classe.encode("iso-8859-1", "replace"),
                "data2": donnees_superviseur.encode("iso-8859-1", "replace"),
                "qclass": param["qclass"]}

        rep = self.callJob(dico)

        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/creerClasse", "requete": dico})

        return rep

    def creerExercice(self, param):
        """Creation d'un exercice WIMS."""
        # Lorsque le parametre "sandbox" est activé, l'exercice n'est pas injecté
        # dans la classe, mais seulement dans un bac à sable pour compilation.
        # LOG.info("---- creerExercice ----")
        # data = self.getAttribut(param["modele"])
        result_dict = {"fonction": "jalon.wims/utility.py/creerExercice"}

        if param["qclass"] == "":
            result_dict["rep"] = '{"status":"ERROR"],"message":"Acune classe spécifiée pour ajouter un exercice"}'
            return self.verifierRetourWims(result_dict)

        if "sandbox" in param:
            job = "testexo"
            del param["sandbox"]
        else:
            job = "addexo"

        # LOG.info("[creerExercice] param[source]=\n%s" % param["source"])
        dico = {"job": job,
                "code": param["authMember"],
                "data1": param["source"],
                "qexo": param["qexo"],
                "qclass": param["qclass"]}
        if "option" in param:
            dico["option"] = param["option"]
        # try:
        result_dict["rep"] = self.callJob(dico)
        result_dict["requete"] = dico
        result = self.verifierRetourWims(result_dict)

        # if job == "testexo":
        #    del param["data_q"]

        # except:
        # result={"status" : "ERROR","type": "JSON_DECODING", "infos":sys.exc_info()[0]}
        return result

    def creerFeuille(self, param):
        u"""ajoute une feuille d'entrainement à une classe Wims."""
        if param["qclass"] and param["qclass"] is not None:
            donnees_feuille = self.formaterDonnees(param)
            # modele = "expiration=%s\ntitle=%s\ndescription=%s"
            # donnees_feuille = modele % (self.expiration_date, param["title"].decode("utf-8"), param["description"].decode("utf-8"))
            requete = {"job": "addsheet",
                       "code": param["authMember"],
                       "data1": donnees_feuille.encode("iso-8859-1", "replace"),
                       "qclass": param["qclass"]}
            rep = self.callJob(requete)
            rep = self.verifierRetourWims(
                {"rep": rep, "fonction": "jalon.wims/utility.py/creerFeuille", "requete": requete})
            return rep
        else:
            return None

    def creerExamen(self, param):
        """Ajoute un examen a une classe wims."""
        # modele = "expiration=%s\ntitle=%s\ndescription=%s\nduration=%s\nattempts=%s\ncut_hours=%s\n"
        # donnees = modele % (self.expiration_date, param["title"].decode("utf-8"), param["description"].decode("utf-8"),
        #                    param["duration"], param["attempts"], param["cut_hours"].decode("utf-8"))
        donnees = self.formaterDonnees(param)
        requete = {"job": "addexam",
                   "code": param["authMember"],
                   "data1": donnees.encode("iso-8859-1", "replace"),
                   "qclass": param["qclass"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims(
            {"rep": rep, "fonction": "jalon.wims/utility.py/creerExamen", "requete": requete})
        return rep

    def creerUser(self, param):
        """Ajoute un utilisateur a une classe wims."""
        quser = self.validerUserID(param["quser"])
        try:
            data = "lastname=%s\nfirstname=%s\npassword=%s\n" % (param["lastname"].encode("iso-8859-1"),
                                                                 param["firstname"].encode("iso-8859-1"),
                                                                 DateTime().strftime("%d%H%M%S"))
        except:
            data = "lastname=%s\nfirstname=%s\npassword=%s\n" % (
                param["lastname"], param["firstname"], DateTime().strftime("%d%H%M%S"))
        requete = {"job": "adduser", "qclass": param["qclass"], "quser": quser, "data1": data, "code": quser}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/creerUser", "requete": requete})
        return rep

    def getAttribut(self, attribut):
        u"""Renvoie l'attribut demandé."""
        return self.__getattribute__(attribut)

    def getURLWims(self):
        """Construit et renvoie l'url d'appel au module adm/raw de wims."""
        # ici il faudra remplacer "lang=fr" par la langue d'affichage de Jalon.
        return "%s?lang=fr&module=adm/raw&ident=%s&passwd=%s" % (self.url_connexion, self.login, self.password)

    def getExercicesWims(self, param):
        """Permet d'obtenir la liste des exercices d'une classe."""
        requete = {"job": "listExos", "code": param["authMember"], "qclass": param["qclass"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep,
                                       "fonction": "jalon.wims/utility.py/getExercicesWims",
                                       "requete": requete,
                                       "jalon_URL": param["jalon_URL"]
                                       })
        return rep

    def getNote(self, param):
        """Permet d'obtenir la liste des notes d'un utilisateur param["quser"]."""
        requete = {"job": "getscore", "code": param["quser"], "qclass": param["qclass"], "quser": param["quser"]}

        # Si param["qsheet"] est précisé, on filtre les notes pour n'afficher que la feuille "qsheet"
        if "qsheet" in param:
            requete["qsheet"] = param["qsheet"]
        rep_wims = self.callJob(requete)
        # print "\nrep : %s\n" % rep_wims
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
                # print "****\n  [Jalon.wims/utility] ERREUR WIMS : pas de notes pour la
                # feuille demandee. \n rep = %s \n****" % rep
        return retour

    def injecter_exercice(self, param):
        """Injecte tous les exercices d'une feuille dans un examen."""
        requete = {"job": "linksheet",
                   "code": param["authMember"],
                   "qclass": param["qclass"],
                   "qexam": param["qexam"],
                   "qsheet": param["qsheet"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims(
            {"rep": rep, "fonction": "jalon.wims/utility.py/injecter_exercice", "requete": requete})
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

        # intro_check="3" affiche la bonne réponse en cas d'erreur
        # (à utiliser dans le cas des entrainements uniquement)
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
                                                    param["title"],
                                                    "")
        requete = {"job": "putexo", "code": param["authMember"], "data1": donnees_exercice.encode("iso-8859-1", "ignore"),
                   "qclass": param["qclass"], "qsheet": param["qsheet"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims(
            {"rep": rep, "fonction": "jalon.wims/utility.py/lierExoFeuille", "requete": requete})
        return rep

    def modifierExoFeuille(self, param):
        """Modifie l'exercice d'une feuille."""
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
                                                    param["title"],
                                                    "")
        requete = {"job": "modexosheet", "code": param["authMember"], "data1": donnees_exercice.encode("iso-8859-1", "ignore"),
                   "qclass": param["qclass"], "qsheet": param["qsheet"], "qexo": param["qexo"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims(
            {"rep": rep, "fonction": "jalon.wims/utility.py/modifierExoFeuille", "requete": requete})
        return rep

    def retirerExoFeuille(self, param):
        u"""Retire l'exercice param["qexo"] de la feuille param["qsheet"]."""
        requete = {"job": "modexosheet", "code": param["authMember"], "option": "remove forced",
                   "qclass": param["qclass"], "qsheet": param["qsheet"], "qexo": param["qexo"]}
        # print "jalon.wims/retirerExoFeuille : Suppression de l'exercice %s" % param["qexo"]
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
        rep = self.verifierRetourWims(
            {"rep": rep, "fonction": "jalon.wims/utility.py/modifierExoFeuille", "requete": requete})
        return rep

    def formaterDonnees(self, param):
        u"""fournit la variable "data1" des propriétés d'une autoeval au bon format."""
        donnees = []

        # donnees Communes
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

        # donnees exclusives aux examens
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
        # LOG.info("---- modifierFeuille | param = %s----" % param)

        donnees_feuille = self.formaterDonnees(param)

        requete = {"job": "modsheet", "code": param["authMember"], "data1": donnees_feuille.encode("iso-8859-1", "replace"),
                   "qclass": param["qclass"], "qsheet": param["qsheet"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims(
            {"rep": rep, "fonction": "jalon.wims/utility.py/modifierFeuille", "requete": requete})
        # LOG.info("---- modifierFeuille | REP_WIMS = %s----" % rep)
        return rep

    def modifierExamen(self, param):
        """Modifie les parametres d'un examen."""
        donnees = self.formaterDonnees(param)

        requete = {"job": "modexam", "code": param["authMember"], "data1": donnees.encode("iso-8859-1", "replace"),
                   "qclass": param["qclass"], "qexam": param["qexam"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims(
            {"rep": rep, "fonction": "jalon.wims/utility.py/modifierExamen", "requete": requete})
        return rep

    def reordonnerFeuille(self, param):
        u"""Reordonne les exercices d'une feuille.

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

    def string_for_wims(self, chaine):
        """Supprime tous les caracteres indesirables d'une chaine pour l'integrer au format WIMS ( parentheses, accolades, crochets... )."""
        return chaine.replace('(', "").replace(')', "").replace("{", "").replace("}", "").replace("[", "").replace("]", "")

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

    def importHotPotatoes(self, folder, member_auth, import_file):
        u"""import d'exercices Hotpotatoes dans une activité WIMS d'un cours.."""
        # LOG.info("----- importHotPotatoes -----")

        h = HTMLParser.HTMLParser()

        # On s'assure que le curseur de lecture est au début du fichier.
        import_file.seek(0)

        tree = ET.parse(import_file)
        root = tree.getroot()
        # groupe_title = h.unescape(root.find('./data/title').text).encode("utf-8")
        questions = root.find('./data/questions')
        questions_list = []

        if not questions:
            message = _(u"Votre fichier n'est pas dans un format .jqz valide. Assurez-vous de sélectionner un fichier « .jqz », généré depuis HotPotatoes V6 ou plus.")
            self.plone_utils.addPortalMessage(message, type='error')
            return questions_list

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

            obj_id = folder.invokeFactory(type_name='JalonExerciceWims', id="%s-%s-%s-%s" %
                                          ("qcmsimple", member_auth, DateTime().strftime("%Y%m%d%H%M%S"), i))
            question_dict["id_jalon"] = obj_id
            questions_list.append(question_dict)
            obj = getattr(folder, obj_id)
            ennonce = question_record.find('question').text
            # if "#x2019;" in ennonce:
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
                # self.plone_log("unknown_model")
            else:
                # L'appel à WIMS s'est bien passé, on applique les modifications à l'objet Jalon
                if wims_response["status"] == "OK":
                    obj.setProperties({"Title": question_dict["title"],
                                       "Modele": "qcmsimple",
                                       })
            if i > 63:
                message = _(u"Attention : une activité WIMS ne peut contenir plus de 64 exercices. Certaines questions n'ont pas été importées.")
                self.plone_utils.addPortalMessage(message, type='warning')
                return questions_list

        return questions_list

    def importMoodleQuizXML(self, params):
        u"""Import d'exercices Moodle (quiz) dans une activité WIMS d'un cours."""
        # See "https://docs.moodle.org/3x/fr/Format_XML_Moodle"
        # params must be : {folder, member_auth, import_file}
        import re
        LOG.info("----- importMoodleQuizXML -----")

        # from Products.CMFCore.utils import getToolByName
        # putils = getToolByName(object, 'plone_utils')

        folder = params["folder"]
        member_auth = params["member_auth"]
        import_file = params["file"]

        h = HTMLParser.HTMLParser()
        max_exos = 64

        # On s'assure que le curseur de lecture est au début du fichier.
        import_file.seek(0)

        tree = ET.parse(import_file)
        root = tree.getroot()
        # groupe_title = h.unescape(root.find('./data/title').text).encode("utf-8")

        questions_list = []

        if not root.tag == "quiz":
            message = _(u"Votre fichier n'est pas dans un format XML Moodle valide. Assurez-vous de sélectionner un fichier « .xml », généré depuis des Quiz Moodle V? ou plus.")
            folder.plone_utils.addPortalMessage(message, type='error')
            return questions_list

        # On charge la liste des etiquettes existantes pour le dossier WIMS
        folder_subjects = folder.getSubjectsDict()

        nb_exos = 1

        # liste des nouvelles etiquettes, avec leur id
        new_tags = {}
        # Liste d'exercice non reconnus (qui ne seront pas importés)
        unrecognized_list = {}

        last_question = len(root)

        if params["model_filter"] == "all":
            # params["model_filter"] = ["cloze", "multichoice", "matching"]
            params["model_filter"] = ["cloze"]

        for qnum, question in enumerate(root):
            param_wims = None
            question_type = question.get('type')

            if question_type == "category":
                # liste des id des etiquettes à ajouter a l'exo courant
                tags_list = []
                cat_structure = question.find('category').find('text').text.strip()
                # On s'assure que les accents sont bien en unicode.
                cat_structure = cat_structure.encode("utf-8")
                cat_structure = cat_structure.split('/')
                for tag_title in cat_structure:
                    # si on a pas encore créé cette catégorie
                    if tag_title not in new_tags:
                        # Si l'etiquette existe deja, on demande son ID
                        if tag_title in folder_subjects.values():
                            for subj_key in folder_subjects:
                                if folder_subjects[subj_key] == tag_title:
                                    tag_id = subj_key
                                    break
                        # Si elle n'existe pas, on l'ajoute aux etiquettes du jalonfolder
                        else:
                            tag_id = "%s" % params["context"].getNewTagId()
                            folder_subjects[tag_id] = tag_title

                            LOG.info("On ajoute l'etiquette #%s : %s" % (tag_id, tag_title))
                            folder.setSubjectsDict(folder_subjects)
                            tags = list(folder.Subject())
                            tags.append(tag_id)
                            folder.setSubject(tuple(tags))
                        new_tags[tag_title] = tag_id

                    # On l'ajoute aux tags du prochain exercice si elle n'y est pas déjà.
                    if new_tags[tag_title] not in tags_list:
                        tags_list.append(new_tags[tag_title])
            # Si le type de question fait partie des modeles à importer
            elif question_type in params["model_filter"]:
                # TODO : ici il faudrait s'assurer que le titre ne dépasse pas 40 chars...
                question_dict = {"title": question.find('name').find('text').text.strip()}

                if question_type == "cloze":
                    # LOG.info("----- Nouvelle question de type 'cloze' (%s) -----" % question_dict["title"])
                    modele_wims = "texteatrous"

                    donnees = question.find('questiontext').find('text').text

                    # Il faut maintenant parser les donnees à la recherches de codes du style :
                    # {1:MULTICHOICE:BAD_REP1~%100%GOOD_REP1~BAD_REP2~BAD_REP3}

                    pattern_trous = r"{(.+?)}"
                    pattern_percent = re.compile(r"%([0-9]*?)%")
                    matches = re.finditer(pattern_trous, donnees)
                    for match in matches:
                        trou = match.group(1)
                        good_reps = []
                        bad_reps = []
                        if trou.startswith("1:MULTICHOICE:"):
                            trou = trou.replace("1:MULTICHOICE:", "")
                            trou = trou.split("~")
                            for rep in trou:
                                fraction = pattern_percent.search(rep)
                                if fraction is not None:
                                    fraction = fraction.group(1)
                                    if fraction != "100":
                                        LOG.info("----- ATTENTION : cloze with fraction != 100 !! (%s) -----" % fraction)
                                    rep = pattern_percent.sub('', rep)
                                    good_reps.append(rep)
                                else:
                                    bad_reps.append(rep)
                                    # LOG.info("----- Mauvaise -----(%s)" % rep)
                            good_rep = ",".join(good_reps)
                            if len(good_reps) > 1:
                                # On utilise les accolades aléatoires (une des bonnes réponses sera piochée au hasard)
                                good_rep = "{%s}" % (good_rep)

                            bad_reps = ",".join(bad_reps)
                            trou = "%s,%s" % (good_rep, bad_reps)

                        elif trou.startswith("1:SHORTANSWER:="):
                            trou = trou.replace("1:SHORTANSWER:=", "")
                        else:
                            LOG.info("----- ATTENTION : cloze with no unrecognized TYPE!! (%s) -----" % trou)
                            message = _(u"----- ATTENTION : cloze with unrecognized TYPE! (%s) -----" % trou)
                            folder.plone_utils.addPortalMessage(message, type='warning')
                        donnees = donnees.replace(match.group(), "??%s??" % trou)

                    feedbacks = {}
                    for feedback_type in ['generalfeedback', 'correctfeedback', 'incorrectfeedback', 'partiallycorrectfeedback']:
                        match = question.find(feedback_type)
                        if match is not None:
                            # ici tester si match.format = 'html' ?
                            # moodle formats : html (default), moodle_auto_format, plain_text et markdown
                            feedbacks[feedback_type] = match.find('text').text
                        else:
                            feedbacks[feedback_type] = ""

                    # Todo : partiallycorrectfeedback

                    list_order = int(question.find('shuffleanswers').text) + 1

                    param_wims = {"title": question_dict["title"].encode("utf-8"),
                                  "type_rep"     : "atext",
                                  "donnees"      : donnees.encode("utf-8"),
                                  "feedback_general": feedbacks['generalfeedback'].encode("utf-8"),
                                  "feedback_bon"    : feedbacks['correctfeedback'].encode("utf-8"),
                                  "feedback_mauvais": feedbacks['incorrectfeedback'].encode("utf-8"),
                                  "credits"         : "",
                                  "accolade"        : "1",
                                  "list_order"      : "%s" % list_order
                                  }

                elif question_type == "multichoice":
                    # TODO : preliminary DRAFT only
                    LOG.info("----- Nouvelle question de type 'multichoice' -----")
                    modele_wims = "qcmsimple"
                    question_dict = {"good_rep": [],
                                     "bad_rep":  []}
                    for answer in question.find('answers'):
                        answer_text = answer.find('text').text
                        if answer_text:
                            answer_text = answer_text.replace("&#x2019;", "'")
                            if int(answer.find("correct").text):
                                question_dict["good_rep"].append(h.unescape(answer_text).encode("utf-8"))
                            else:
                                question_dict["bad_rep"].append(h.unescape(answer_text).encode("utf-8"))

                    enonce = question.find('questiontext').find('text').text
                    # test the questiontext format ? html ?

                    # if "#x2019;" in enonce:
                    #    print enonce
                    enonce = enonce.replace("&#x2019;", "'")

                    param_wims = {"title":            question_dict["title"],
                                  "enonce":           h.unescape(enonce).encode("utf-8"),
                                  "bonnesrep":        "\n".join(question_dict["good_rep"]),
                                  "mauvaisesrep":     "\n".join(question_dict["bad_rep"]),
                                  "tot":              "5",
                                  "givetrue":         "2",
                                  "minfalse":         "0",
                                  "options":          ["checkbox", "split"],
                                  "feedback_general": "",
                                  "feedback_bon":     "",
                                  "feedback_mauvais": ""
                                  }

                elif question_type == "matching":
                    # TODO : preliminary DRAFT only
                    LOG.info("----- Nouvelle question de type 'matching' -----")
                else:
                    # other Moodle question types : truefalse|shortanswer|matching|essay|numerical|description
                    if question_type not in unrecognized_list :
                        unrecognized_list[question_type] = 1
                    else:
                        unrecognized_list[question_type] = unrecognized_list[question_type] + 1

                if param_wims is not None:

                    obj_id = folder.invokeFactory(type_name='JalonExerciceWims', id="%s-%s-%s-%s" %
                                                  (modele_wims, member_auth, DateTime().strftime("%Y%m%d%H%M%S"), nb_exos))
                    question_dict["id_jalon"] = obj_id
                    questions_list.append(question_dict)
                    obj_created = getattr(folder, obj_id)

                    # With "no_compile", import is much more faster !
                    param_wims["option"] = "no_compile"
                    wims_response = obj_created.addExoWims(obj_id, param_wims["title"], member_auth, modele_wims, param_wims)

                    if not("status" in wims_response):
                        # La creation a planté (Cause : modele inconnu ?)
                        folder.manage_delObjects(ids=[obj_id])
                        # self.plone_log("unknown_model")
                    else:
                        # L'appel à WIMS s'est bien passé, on applique les modifications à l'objet Jalon
                        if wims_response["status"] == "OK":
                            LOG.info("qnum = %s | last = %s)" % (qnum, last_question))
                            nb_exos = nb_exos + 1
                            LOG.info("nb_exos = %s | max_exos = %s)" % (nb_exos, max_exos))
                            obj_created.setProperties({"Title": question_dict["title"],
                                                       "Modele": modele_wims,
                                                       })

                            # On etiquette cet exercice :
                            if len(tags_list) > 0:
                                obj_created.setSubject(tuple(tags_list))
                                obj_created.reindexObject()
                                LOG.info("On etiquette cet exercice (%s)" % tags_list)
                    if nb_exos > max_exos:
                        message = _(u"Attention : vous ne pouvez importer plus de %s exercices dans un seul fichier. Certaines questions n'ont pas été importées." % max_exos)
                        folder.plone_utils.addPortalMessage(message, type='warning')
                        break

        if nb_exos > 0:
            # Etant donné que les exos ont tous été ajoutés sans compilation,
            # on lance une compilation globale :
            folder.compilExosWIMS(member_auth)

        if len(unrecognized_list.keys()) > 0:
            message = _(u"Attention : Certaines questions utilisaient un modèle non reconnu et n'ont pas été importées. (%s)" % unrecognized_list)
            folder.plone_utils.addPortalMessage(message, type='warning')

        return questions_list

    def verifierRetourWims(self, params):
        """verifie le bon retour d'un appel WIMS, et envoie un mail d'erreur si besoin."""
        # params["rep"] doit etre une chaine de caracteres au format json.
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
            rep = {"status": "ERROR",
                   "message": "No JSON object could be decoded : %s" % e,
                   "error_type": "Exception Raised (ValueError)"}
        except TypeError, e:
            # A priori si on tombe dans ce cas, c'est une erreur d'appel de "verifierRetourWims",
            # a qui on a donné un JSON au lieu d'une string.
            message = "<p>%s</p><p>Reponse originale de WIMS : %s</p>" % (message, rep)
            rep = {"status": "ERROR", "message": "Type Error : %s" % e, "error_type": "Exception Raised (TypeError)"}

        if rep["status"] == "ERROR":
            if "message" not in rep:
                rep["message"] = "aucun"
            if message == "":
                message = "aucune info supplémentaire"
            mail_erreur["message"] = "<h1>Retour d'erreur de WIMS</h1>"

            if "jalon_URL" in params:
                mail_erreur["message"] = "%s <h2>Objet Jalon concern&eacute;&nbsp;:</h2><p>%s<br/><em>nb : la page de l'erreur peut etre diff&eacute;rente. Voir le REQUEST complet pour plus d'infos.</em></p>" % (mail_erreur["message"],
                                                                                                                                                                                                                    params["jalon_URL"])
            mail_erreur["message"] = "%s <h2>Fonction appelante :</h2><p>%s</p>" % (mail_erreur["message"], fonction)

            if requete != "":
                mail_erreur["message"] = '%s <h2>Requ&ecirc;te effectu&eacute;e :</h2><pre>%s</pre>' % (mail_erreur["message"], requete)

            if "error_code" in rep:
                mail_erreur["message"] = "%s <h2>Code d'erreur : <code>%s</code></h2>" % (mail_erreur["message"], rep["error_code"])

            mail_erreur["message"] = "%s <h2>Message d'erreur :</h2><pre>%s</pre>" % (mail_erreur["message"], rep["message"])
            mail_erreur["message"] = "%s <h2>Informations sur l'erreur</h2><pre>%s</pre>" % (mail_erreur["message"], message.decode("utf-8"))

            if "error_body" in rep:
                mail_erreur["message"] = "%s <h2>Page d'erreur :</h2><div style='border-left:2px orange;padding-left:2em'>%s</div>" % (mail_erreur["message"], rep["error_body"])

            mail_erreur["message"] = "%s <h2>R&eacute;ponse WIMS :</h2><div><pre>%s</pre></div>" % (mail_erreur["message"], rep)

            if "jalon_request" in params:
                mail_erreur["message"] = "%s <hr/><h2>REQUEST Jalon :</h2><div>%s</div>" % (mail_erreur["message"], params["jalon_request"])

            jalon_utils.envoyerMailErreur(mail_erreur)
            # print "@@@@@@ ==> envoi d'un mail d'erreur WIMS "

            # NB : dans le cas ou fonction == "creerExercice" and "error_code" in rep and rep["error_code"]=="450",
            #   on pourrait ne pas envoyer de mail : c'est en general une parenthese mal fermée

        return rep
