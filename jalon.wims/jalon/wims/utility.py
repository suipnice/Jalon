# -*- coding: utf-8 -*-

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
LOG = getLogger( '[jalon.wims.utility]' )
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
    return getUtility(IWims)


class Wims(SimpleItem):
    """Wims Utility"""
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
        return getattr(self, "%s" % key)

    def setProperties(self, form):
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "%s" % key, val.decode("utf-8"))

    # authUser demande a wims d'ouvrir une session pour un utilisateur
    # Cette fonction ne renvoit pas un json, car elle peux etre utilisée pour tester si un utilisateur existe.
    def authUser(self, param):
        param["quser"] = self.validerUserID(param["quser"])
        param["job"] = "authUser"
        return self.callJob(param)

    security.declarePrivate('convertirDate')

    # convertirDate : convertit une date d au format us ou fr
    def convertirDate(self, d, us=False):
        if not us:
            return DateTime(d).strftime("%d.%m.%Y - %Hh%M")
        else:
            return DateTime(d).strftime("%Y-%m-%d")

    # callJob : fonction d'appel generique des jobs du module adm/raw de Wims
    def callJob(self, param):
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

    #checkIdent : verification de la validité des identifiants
    def checkIdent(self, param):
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

    #cleanClass : purge les activités de la classe param[qclass]
    # en entreee : params = {"qclass": class_id, "code": authMember}
    def cleanClass(self, params):
        params["job"] = "cleanclass"
        params["rclass"] = self.classe_locale

        rep = self.callJob(params)

        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/cleanClass", "requete": params})
        if rep["status"] == "OK":
            cleaned = rep["suppressed_users"]
        else:
            cleaned = None
        return {"status": rep["status"], "cleaned": cleaned, "message": rep["message"]}

    #creerClasse : creation d'une classe ou d'un groupement de classes WIMS
    def creerClasse(self, param):
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

    #creerExercice : creation d'un exercice WIMS
    # Lorsque le parametre "sandbox" est activé, l'exercice n'est pas injecté
    # dans la classe, mais seulement dans un bac à sable pour compilation.
    def creerExercice(self, param):
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

    # creerFeuille : ajoute une feuille d'entrainement à une classe Wims
    def creerFeuille(self, param):
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

    # creerExamen : ajoute un examen a une classe wims
    def creerExamen(self, param):
        #modele = "expiration=%s\ntitle=%s\ndescription=%s\nduration=%s\nattempts=%s\ncut_hours=%s\n"
        #donnees = modele % (self.expiration_date, param["title"].decode("utf-8"), param["description"].decode("utf-8"),
        #                    param["duration"], param["attempts"], param["cut_hours"].decode("utf-8"))
        donnees = self.formaterDonnees(param)
        requete = {"job": "addexam", "code": param["authMember"], "data1": donnees.encode("iso-8859-1", "replace"), "qclass": param["qclass"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/creerExamen", "requete": requete})
        return rep

    # creerUser : Ajoute un utilisateur a une classe wims
    def creerUser(self, param):
        quser = self.validerUserID(param["quser"])
        try:
            data = "lastname=%s\nfirstname=%s\npassword=%s\n" % (param["lastname"].encode("iso-8859-1"), param["firstname"].encode("iso-8859-1"), DateTime().strftime("%d%H%M%S"))
        except:
            data = "lastname=%s\nfirstname=%s\npassword=%s\n" % (param["lastname"], param["firstname"], DateTime().strftime("%d%H%M%S"))
        requete = {"job": "adduser", "qclass": param["qclass"], "quser": quser, "data1": data, "code": quser}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/creerUser", "requete": requete})
        return rep

    # getAttribut : renvoie l'attribut demandé
    def getAttribut(self, attribut):
        return self.__getattribute__(attribut)

    # getURLWims : construit et renvoie l'url d'appel au module adm/raw de wims
    def getURLWims(self):
        # ici il faudra remplacer "lang=fr" par la langue d'affichage de Jalon.
        return "%s?lang=fr&module=adm/raw&ident=%s&passwd=%s" % (self.url_connexion, self.login, self.password)

    #getExercicesWims permet d'obtenir la liste des exercices d'une classe
    def getExercicesWims(self, param):
        requete = {"job": "listExos", "code": param["authMember"], "qclass": param["qclass"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep,
                                       "fonction": "jalon.wims/utility.py/getExercicesWims",
                                       "requete": requete,
                                       "jalon_URL": param["jalon_URL"]
                                      })
        return rep

    # getNote permet d'obtenir la liste des notes d'un utilisateur param["quser"]
    def getNote(self, param):
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

    """
    Fonction remplacée par getVariablesDefaut de JalonExerciceWims
    
    # getVariablesDefaut permet d'obtenir les variables par défaut d'un modele. (plus utilis)
    def getVariablesDefaut(self, modele):
        #getVariablesDefaut permet de lister les valeurs par defaut a definir en fonction du modele d'exercice.
        variables_defaut = {"qcmsimple":
                                {"enonce": "Cochez la(les) bonne(s) réponse(s).",
                                 "bonnesrep": "bon choix n°1\nbon choix n°2",
                                 "mauvaisesrep": "mauvais choix n°1\nmauvais choix n°2",
                                 "tot": "5",
                                 "givetrue": "2",
                                 "minfalse": "0",
                                 "feedback_general": "",
                                 "feedback_bon": "",
                                 "feedback_mauvais": "",
                                 "options_checkbox": "checkbox",
                                 "options_split": "split"
                                 },
                            "equation":
                                {"precision": "100",
                                 "param_a": "randint(1..20)",
                                 "param_b": "randint(1..5)",
                                 "param_c": "0",
                                 "param_d": "0",
                                 "equation": "\\a * \\b",
                                 "enonce": "Je vend \\a chaussette(s) au prix de \\b euros chacune. Quel est le montant de ma vente ?",
                                 "texte_reponse": "Ma réponse"
                                 },
                            "texteatrous":
                                {"type_rep": "atext",
                                 "donnees": "Le texte ci-dessous est incomplet. Remplissez les trous.\n<br/>\nL'Université de Nice fut officiellement instituée par décret du 23 octobre ??1965??.\nNéanmoins, ses racines historiques remontent au XVIIéme siècle, avec le fameux ??Collegium jurisconsultorum niciensium, Collegius niciensius?? crée en ??1639?? par les Princes de Savoie ; il comprenait un important corps de jurisconsultes et sa notoriété dura jusqu'au rattachement de Nice à la France, en ??1860,1870,1850,1840??.\nÀu XVIIème siècle, une Ecole de ??Médecine, Couture, Danse, Chimie?? dispensa des enseignements appréciés dans toute l'Europe.\n"
                                 },
                            "marqueruntexte":
                                {"minmark": "1",
                                 "maxmark": "8",
                                 "data": "{Jack,Jean,Louis,Michel,Pierre}  ??et,est?? forain, il \n??{tien,tiens} ,tient?? ??un,une?? baraque de tir ??a,à?? la noix de coco.\n??Ont,On?? ??trouvent,trouve?? des ??Baraque,Baraques?? Noix de Coco dans \n??tous,toutes?? les foires. Les ??,gens?? ??arrive,arrivent??,\n??donne,donnent?? des ??,sous??\n??est,et?? ??envoie,envoient?? des ??,boules?? sur une noix de coco \n??{poser,posé} ,posée?? en haut d'une ??,colonne??.\nCeux qui ??fait,font??\n??{dégringolé,dégringolée} ,dégringoler?? une noix de coco \n??{peu,peut,peux} ,peuvent?? ??{le,les} ,la??\n??{gardée,gardé} ,garder??.\n;\n??{Quel,Quels,Quelles} ,Quelle??\nidée ??est-je,ai-je??\n??{d'acheté,d'achetée,d'achetés} ,d'acheter?? ??{cept,cette,ces,ce} ,cet??\noiseau ? L'oiselier me dit : '??{S'est,Cet} ,C'est?? un ??{mal,malle} ,mâle??.\n??Attender,Attendez?? une ??,semaine?? qu'il \n??{s'abitue,s'abituent,s'habituent} ,s'habitue??, ??est,et?? il chantera'.\n??Hors,Or??, l'oiseau ??sobstine,s'obstine?? ??a,à?? ??ce,se?? \n??tait,taire?? et il ??fais,fait?? ??tous,tout?? de ??{traver,travert} ,travers??.\n;\nLes ??désert,déserts?? de ??sables,sable?? ??occupe,occupent?? de\n??large,larges?? parties {de la planète,du monde,de la Terre} .\nIl n'y ??{pleu,pleus,pleuvent} ,pleut??\npresque ??,pas??. Très ??peut,peu?? de plantes et ??,d'animaux?? y\n??vit,vivent??. Les ??,dunes?? ??son,sont?? des collines de\n??,sable?? que le vent ??à,a??\n??{construit,construits,construite} ,construites??. Les \n??grains,graines?? de ??{certain,certaine,certains} ,certaines??\nplantes ??reste,restent?? sous le ??sole,sol?? du désert pendant\ndes années. ??{Ils,Elle} ,Elles?? ??ce,se?? ??met,mettent??\n??a,à?? ??{poussées,poussée,poussés} ,pousser?? dès qu'il y a\n??une,un?? orage.\n;",
                                 "pre": "Marquez les fautes d'orthographe dans la phrase ci-dessous.",
                                 "post": "",
                                 "options": "split"
                                 },
                            "marquerparpropriete":
                                {"explain": "Parmi les joueurs de football ci-dessous, marquez ceux qui sont dans l'équipe \prop.",
                                 "prop": "française, italienne, allemande",
                                 "data": "Fabien Barthez , francaise\nLilian Thuram , francaise\nClaude Makélélé , francaise\nZinedine Zidane , francaise\nFranck Ribéry , francaise\nThierry Henry , francaise\nDavid Trézéguet , francaise\nGianluigi Buffon , italienne\nMorgan De Sanctis , italienne\nAngelo Peruzzi , italienne\nChristian Abbiati , italienne\nMarco Amelia , italienne\nJens Lehmann , allemande\nOliver Kahn , allemande\nTimo Hildebrand , allemande\nPhilipp Lahm , allemande\nArne Friedrich , allemande\n",
                                 "tot": "12",
                                 "mingood": "1",
                                 "minbad": "4",
                                 "options": "split",
                                 "presentation": "liste"
                                 },
                            "questiontextuelletolerante":
                                {"len": "20",
                                 "data": "l'intensité est : ??ampère??;\nla tension est : ??volt??;\nla résistance est : ??ohm??;\nla capacité d'un condensateur est : ??farad??. Son symbole est : ??F??;\nl'inductance d'un solénoïde est : ??henri??;\nla puissance dissipée sur une composante est : ??watt??;\nla fréquence est : ??hertz??. Son symbole est : ??Hz??;",
                                 "atype": "atext",
                                 "include_good": "oui",
                                 "words": "electricite electrique circuit composante intensite courant tension charge resistor resistance diode transistor condensateur capacite solenoide inductance puissance frequence",
                                 "pre": "En électricité, l'unité de base pour mesurer ",
                                 "post": "."
                                 },
                            "taperlemotassocie":
                                {"size": "20",
                                 "words": "bambou,bambous\nbijou,bijoux\ncadeau,cadeaux\ncaillou,cailloux\ncheval,chevaux\nchou,choux\nciel,cieux\nclou,clous",
                                 "type_rep": "atext",
                                 "explain": "Tapez le pluriel du nom \\name :",
                                 },
                            "reordonner":
                                {"tot": "6",
                                 "size": "80x50",
                                 "data": "Mercure, Vénus, Terre, Mars, Jupiter, Saturne, Uranus, Neptune",
                                 "explain": "Mettre les planètes suivantes du système solaire dans le bon ordre, avec la plus proche du Soleil en premier."
                                 },
                            "correspondance":
                                {"tot": "6",
                                 "sizev": "50",
                                 "sizer": "250",
                                 "sizel": "250",
                                 "feedback_general": "",
                                 "data": "L'Allemagne, Berlin\nL'Australie, Canberra\nLe Canada, Ottawa\nLa Chine, Beijing\nL'Espagne, Madrid\nLes Etats-Unis, Washington\nLa France, Paris\nLa Grande Bretagne, Londres\nL'Inde, New Delhi\nL'Indonésie, Jakarta\nL'Italie, Rome\nLe Japon, Tokyo\nLa Russie, Moscou",
                                 "explain": "Établissez la correspondance entre les pays et leurs capitales."
                                 },
                            "classerparpropriete":
                                {"tot": "8",
                                 "max1": "4",
                                 "size1": "120x120",
                                 "prop": "Oiseau,Mammifère",
                                 "data": "L'aigle,Oiseau\nL'albatros,Oiseau\nL'alouette,Oiseau\nLe canard,Oiseau\nLe corbeau,Oiseau\nLe faucon,Oiseau\nLe goéland,Oiseau\n\nLe lion,Mammifère\nL'éléphant,Mammifère\nLe chat <img src='http://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Black_hills_cat-tochichi.jpg/120px-Black_hills_cat-tochichi.jpg' alt='photo d'un chat'/>,Mammifère\nLe cheval,Mammifère\nLe chien,Mammifère\nLe cochon,Mammifère\nLa vache,Mammifère",
                                 "shuffle": "shuffle",
                                 "explain": "Classez les animaux ci-dessous selon leurs catégories.",
                                 "post": "",
                                 "estun": "est un",
                                 "noclass": "n'appartient à aucune catégorie",
                                 "feedback_general": ""
                                 },
                            "vraifauxmultiples":
                                {"tot": "4",
                                 "mintrue": "1",
                                 "minfalse": "1",
                                 "datatrue": "À tension égale, le courant passant par un résistor est inversement proportionnel à sa résistance.\nÀ courant égal, la tension sur un résistor est proportionnelle à sa résistance.\nLe courant passant par un résistor est proportionnel à la tension appliquée.\nLa puissance dissipée par un résistor est proportionnelle au carré de la tension appliquée.\nLa puissance dissipée par un résistor est proportionnelle au carré du courant.",
                                 "datafalse": "À tension alternative égale, le courant passant par un condensateur est inversement proportionnel à la capacité.\nÀ tension alternative égale, le courant passant par un condensateur est indépendant de la capacité.\nÀ tension alternative égale, le courant passant par un solénoïde est proportionnel à l'inductance.\nÀ tension continue égale, le courant passant par un condensateur est proportionnel à la capacité.\nÀ tension égale, le courant passant par un résistor est proportionnel à sa résistance.\nÀ tension égale, le courant passant par un résistor est indépendant de sa résistance.\nLe courant passant par une diode est proportionnel à la tension appliquée.\nLa puissance dissipée par un résistor est proportionnelle à la tension appliquée.\nLa puissance dissipée par un résistor est proportionnelle au courant.\nLa puissance dissipée par un condensateur est proportionnelle {à,au carré de} la tension appliquée.\nLa puissance dissipée par un condensateur est proportionnelle {au,au carré du} courant.\nLa puissance dissipée par un solénoïde idéal est proportionnelle {à,au carré de} la tension appliquée.\nLa puissance dissipée par un solénoïde idéal est proportionnelle {au,au carré du} courant.",
                                 "options": "split",
                                 "explain": "Parmi les affirmations suivantes, lesquelles sont vraies ? Marquez-les.",
                                 "feedback_general": ""
                                 },
                            "texteatrousmultiples":
                                {"data": "Le début officiel de la Seconde Guerre Mondiale est marqué par\n??la déclaration de guerre,l'offensive?? de\n??la Grande Bretagne et la France,la France,la Grande Bretagne,l'Allemagne,l'Union Soviétique??\ncontre ??l'Allemagne,la Pologne,l'Union Soviétique,la France??.\n;\nLa Seconde Guerre Mondiale s'est déroulée entre ??1939?? et ??1945??.\n;\n??La Grande Bretagne et la France ont,La France a,La Grande Bretagne a,Les États-Unis ont,L'Union Soviétique a?? \ndéclaré la guerre contre l'Allemagne en ??1939?? à la suite de l'envahissement de ??la Pologne?? par cette dernière.\n;\nPendant la Seconde Guerre Mondiale, l'Espagne sous ??Francisco Franco|[F.|Francisco|] Franco?? est un pays\n??neutre,axe,allié,envahi??.\n;\n??Après avoir battu,Avant d'attaquer?? la France,\n{l'Allemagne,Hitler,l'Allemagne Nazie} a lancé une attaque surprise contre l'URSS en\n??décembre,{novembre,octobre},{septembre,août,juillet},{juin,mai,avril},{mars,février,janvier}??\n??1940??, sous le nom {du plan,de l'opération} ??Barbarossa??.",
                                 "pre": "Completez le texte suivant :",
                                 "post": "",
                                 "feedback_general": "",
                                 "type_rep": "atext"
                                 },
                            "exercicelibre": {}
                            }
        if modele in variables_defaut:
            return variables_defaut[modele]
        else:
            return None
    """
    # injecter_exercice : injecte les exercice d'une feuille dans un examen
    def injecter_exercice(self, param):
        requete = {"job": "linksheet", "code": param["authMember"], "qclass": param["qclass"], "qexam": param["qexam"], "qsheet": param["qsheet"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/injecter_exercice", "requete": requete})
        return rep

    # lierExoFeuille : ajoute un exercice à une feuille
    def lierExoFeuille(self, param):
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
        intro_check="1,2,4"

        #intro_check="3" affiche la bonne réponse en cas d'erreur ( à utiliser dans le cas des entrainements uniquement)
        if "afficher_reponses" in param and param["afficher_reponses"]==True:
            intro_check="1,2,3,4"

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

    # modifierExoFeuille : modifie l'exercice d'une feuille
    def modifierExoFeuille(self, param):
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

    # retirerExoFeuille : Retire l'exercice param["qexo"] de la feuille param["qsheet"]
    def retirerExoFeuille(self, param):
        requete = {"job": "modexosheet", "code": param["authMember"], "option": "remove forced",
                   "qclass": param["qclass"], "qsheet": param["qsheet"], "qexo": param["qexo"]}
        #print "jalon.wims/retirerExoFeuille : Suppression de l'exercice %s" % param["qexo"]
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/retirerExoFeuille", "requete": requete})
        return rep

    # monterExoFeuille : Change l'ordre des exercices de la feuille param["qsheet"], en remontant l'exercice param["qexo"] d'un cran
    # pour l'instant, cette fonction n'est pas utilisée.
    def monterExoFeuille(self, param):
        requete = {"job": "modexosheet", "code": param["authMember"], "option": "moveup",
                   "qclass": param["qclass"], "qsheet": param["qsheet"], "qexo": param["qexo"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/modifierExoFeuille", "requete": requete})
        return rep

    # FormaterDonnees : fournit la variable "data1" des propriétés d'une autoeval au bon format
    def formaterDonnees(self, param):
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

    # modifierFeuille : modifie les parametres d'une feuille
    def modifierFeuille(self, param):

        donnees_feuille = self.formaterDonnees(param)

        requete = {"job": "modsheet", "code": param["authMember"], "data1": donnees_feuille.encode("iso-8859-1", "replace"),
                   "qclass": param["qclass"], "qsheet": param["qsheet"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/modifierFeuille", "requete": requete})
        return rep

    # modifierExamen : modifie les parametres d'un examen
    def modifierExamen(self, param):

        donnees = self.formaterDonnees(param)

        requete = {"job": "modexam", "code": param["authMember"], "data1": donnees.encode("iso-8859-1", "replace"),
                   "qclass": param["qclass"], "qexam": param["qexam"]}
        rep = self.callJob(requete)
        rep = self.verifierRetourWims({"rep": rep, "fonction": "jalon.wims/utility.py/modifierExamen", "requete": requete})
        return rep

    # reordonnerFeuille :  reordonne les exercices d'une feuille
    # TODO : Le plus simple sera surement de procéder ainsi :
    #  1. stockge des infos des exos de la feuille
    #  2. suppression des exos de la feuille
    #  3. ajouter les exos de la feuille dans le nouvel ordre
    def reordonnerFeuille(self, param):
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

    # string_for_json : Supprime tous les caracteres indesirables d'une chaine pour l'integrer au format JSON (quotes, retour chariot, barre oblique )
    def string_for_json(self, chaine):
        return chaine.replace('\"', "'").replace('\n', "").replace("\\", "").replace("\t", "\\t")

    #validerUserID : verification de conformité de l'id d'un utilisateur WIMS
    # Il doit avoir une taille mini et maxi et ne contenir aucun caractere interdit
    def validerUserID(self, user_ID):
        if user_ID == None:
            return None
        else:
            retour = user_ID.strip()

            # on prend du premier au "taille max" caractere
            retour = retour[:self.max_login_len]

            if len(retour) < self.min_login_len:
                retour = "%s@__@" % retour

        return retour

    def importerHotPotatoes(self, folder, member_auth, import_file):
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
        

    # verifierRetourWims : verifie le bon retour d'un appel Wims, et envoie un mail d'erreur si besoin.
    # rep doit etre une chaine de caracteres au format json.
    def verifierRetourWims(self, params):

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
