# -*- coding: utf-8 -*-

import os
import json
import time
import urllib

from DateTime import DateTime

from zope.interface import Invalid

from zope.schema import Text
from zope.component import adapts
from zope.site.hooks import getSite
from zope.formlib.form import FormFields
from zope.interface import Interface, implements

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel.form import ControlPanelForm

from jalon.content import contentMessageFactory as _


class IJalonImportControlPanel(Interface):
    """
    fields for jalon import control panel
    """
    chemin_repertoire = Text(title=_(u"title_chemin_repertoire", default=u"Chemin du répertoire à importer"),
                             description=_(u"description_chemin_repertoire", default=u"Exemple : /Plone/Members/"),
                             default=u"/Plone/Members/",
                             required=True)


class JalonImportControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IJalonImportControlPanel)

    def __init__(self, context):
        super(JalonImportControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.jiProps = pprop.jalonimport_properties

    def get_chemin_repertoire(self):
        return self.jiProps.getProperty('chemin_repertoire')

    def addRepertoireMembre(self, utilisateur):
        #print "------- addRepertoireMembre -------"
        portal = getSite()
        Members = getattr(portal, "Members")
        #Création du répertoire d'un utilisateur
        Members.invokeFactory(type_name='JalonFolder', id=utilisateur)
        print "addRepertoireMembre : %s" % utilisateur
        #Récupération du répertoire utilisateur créé
        home = getattr(Members, utilisateur)
        home.manage_setLocalRoles(utilisateur, ["Owner"])
        #Création des sous répertoires du répertoire utilisateur
        home.addSubJalonFolder(utilisateur)
        #Mise à jour des permissions pour les sous répertoires
        for sousRep in home.objectValues("JalonFolder"):
            sousRep.manage_setLocalRoles(utilisateur, ["Owner"])
        #Création du répertoire des cours
        Cours = getattr(portal, "cours")
        Cours.invokeFactory(type_name='JalonFolder', id=utilisateur)
        cours = getattr(Cours, utilisateur)
        #Mise à jour des permissions
        cours.manage_setLocalRoles(utilisateur, ["Owner"])
        #Mise à jour des informations
        cours.setTitle("Mes cours")
        cours.setPortlets()
        cours.reindexObject()

    ################
    # addExosWIMS()
    # Importation des exercices WIMS exportés depuis un serveur Jalon V2
    def addExosWIMS(self, dossier_membres, utilisateur):
        #print "------- addExosWIMS -------"
        # liste des etiquettes
        listeSubject = []

        #Recherche du dossier de l'utilisateur
        dossier_utilisateur = "%s/%s" % (dossier_membres, utilisateur)
        contenuDossier = os.listdir(dossier_utilisateur)

        #Vérification du fichier d'importation  "exportExercicesWims.json"
        if not "exportExercicesWims.json" in contenuDossier:
            return None

        #Chargement du fichier
        fichier_exercices = open('%s/exportExercicesWims.json' % (dossier_utilisateur), 'r')
        listeExercices = json.load(fichier_exercices)
        fichier_exercices.close()

        dossier_exercices = "%s/WIMS/" % dossier_utilisateur

        portal = getSite()
        home = getattr(getattr(portal.Members, utilisateur), "Wims")

        #liste_modeles = home.getListeModelesWims()

        # On demande la liste des exercices WIMS, ce qui aura pour conséquence la création du groupement si celui-ci n'existait pas.
        home.getContents(subject=None, typeR='JalonExerciceWims', authMember=utilisateur, repertoire=home.getId())
        groupement = home.getComplement()
        classe_id = "%s_1" % groupement
        #print "addExosWIMS Classe : %s" % classe_id

        """
        # Procedure liee aux images WIMS :
        # Travail en cours. pour le moemnt, l'operation reste manuelle. (plus rapide)
        # Si un dossier d'images a été exporté de WIMS, on stocke la liste des exercices concernés
        if "images_WIMS" in contenuDossier:
            liste_exos_images = []
            #on utilise un tableau de correspondances entre les modeles V2 et V4 ::
            dico_modeles = {"ClasserPropriete": "classerparpropriete", "Correspondance": "correspondance",
                     "equation": "equation", "MarquerPropriete": "marquerparpropriete",
                     "MarquerTexte": "marqueruntexte", "QCMSimple": "qcmsimple",
                     "QuestionTexte": "questiontextuelletolerante",
                     "Reordonner": "reordonner", "ProprieteTapee": "taperlemotassocie",
                     "Texte_a_Trou": "texteatrous", "Texte_a_Trous": "texteatrous",
                     "TexteATrousM": "texteatrousmultiples", "VraiFauxM": "vraifauxmultiples",
                     "Exo_Brut": "exercicelibre"
                     }
            chaine_userV2 = "_%s_" % utilisateur
            chaine_userV4 = "-%s-" % utilisateur

            dossier_images = "%s/images_WIMS" % dossier_utilisateur
            contenuDossier = os.listdir(dossier_images)

            for exo_id in contenuDossier:
                dossier = "%s/%s" % (dossier_images, exo_id)
                exo_id = exo_id.replace(chaine_userV2, chaine_userV4)
                modele = exo_id.split("-", 1)[0]

                if modele in dico_modeles:
                    new_modele = dico_modeles[modele]
                    new_id = exo_id.replace(modele, new_modele)
                else:
                    new_modele = "exercicelibre"
                    new_id = "%s%s%s" % (new_modele, chaine_userV4, exo_id)

                liste_exos_images.append(new_id)
                new_dossier = "%s/%s" % (dossier_images, new_id)
                if dossier != new_dossier:
                    os.rename(dossier, new_dossier)
                #print "On renomme '%s' en '%s'" % (dossier, new_dossier)
        """

        # Une fois le groupement existant, on peut alors y ajouter les exercices.
        num = 1
        for infosObj in listeExercices:
            #"""
            id_exo = infosObj["id"]
            fichier_exercice = open('%s/%s.oef' % (dossier_exercices, id_exo), 'r')
            data = fichier_exercice.read()
            dico = {"job": "addexo", "code": utilisateur, "data1": data, "qexo": id_exo, "qclass": classe_id}
            fichier_exercice.close()

            #####
            # ICI peut etre ajouter egalement les eventuelles images liées a l'exercice.
            #####

            # Ajout de l'exercice côté WIMS
            json.loads(home.wims("callJob", dico))

            # Ajout de l'exercice côté Jalon
            idObj = home.invokeFactory(type_name='JalonExerciceWims', id=infosObj["id"])
            #print "%s : addExosWIMS : %s" % (str(num), id_exo)
            num = num + 1

            #Récupération du jalonExerciceWims
            exercice = getattr(home, idObj)
            exercice.manage_setLocalRoles(utilisateur, ["Owner"])

            #Mise à jour des données
            exercice.setProperties({"Title": infosObj["titre"].encode("utf-8"),
                                    "Modele": infosObj["modele"]
                                   })

            home.setTagDefaut(exercice)
            subject = list(exercice.Subject())
            subject.append(urllib.quote(infosObj["etiquette"].encode("utf-8")))
            exercice.setSubject(list(subject))

            #Mise à jour des étiquettes du parents
            if not infosObj["etiquette"].encode("utf-8") in listeSubject:
                listeSubject.append(infosObj["etiquette"].encode("utf-8"))
            exercice.reindexObject()

        if listeSubject:
            home.setSubject(tuple(listeSubject))
        home.reindexObject()

    ################
    # addFichiers()
    # Importation des Fichiers exportés depuis un serveur Jalon V2
    def addFichiers(self, value, utilisateur):
        #print "------- addFichiers -------"
        #Recherche du dossier de l'utilisateur
        contenuDossier = os.listdir("%s/%s/" % (value, utilisateur))
        #Vérification du fichier d'importation de cours "exportCours.json"
        if not "exportFichiers.json" in contenuDossier:
            return None
        #Chargement du fichier
        try:
            listeObj = json.load(open('%s/%s/exportFichiers.json' % (value, utilisateur), 'r'))
        except:
            raise Invalid(_(u"addFichiers : %s " % utilisateur))
        portal = getSite()
        listeSubject = []
        dicoFichiers = {}
        num = 1
        home = getattr(getattr(portal.Members, utilisateur), "Fichiers")
        for infosObj in listeObj:
            image = False
            try:
                idFichier = os.listdir("%s/%s/Fichiers/%s/file/" % (value, utilisateur, infosObj["id"]))[-1]
            except:
                idFichier = None
            if idFichier:
                extension = idFichier.split(".")[-1]
                idObj = infosObj["id"].replace(".", "-")
                if extension in ["jpg", "jpeg", "gif", "png", "bmp"]:
                    #Création d'une image sous Plone
                    home.invokeFactory(type_name='Image', id=idObj)
                    image = True
                else:
                    #Création du fichier sous Plone
                    home.invokeFactory(type_name='File', id=idObj)
                #print "%s : addFichiers : %s" % (str(num), idObj)
                num = num + 1
                #Récupération du fichier
                fichier = getattr(home, idObj)
                fichier.manage_setLocalRoles(utilisateur, ["Owner"])
                #Mise à jour des données
                fichier.setTitle(infosObj["titre"].encode("utf-8"))
                home.setTagDefaut(fichier)
                subject = list(fichier.Subject())
                subject.append(urllib.quote(infosObj["etiquette"].encode("utf-8")))
                fichier.setSubject(list(subject))
                #Mise à jour des étiquettes du parents
                if not infosObj["etiquette"].encode("utf-8") in listeSubject:
                    listeSubject.append(infosObj["etiquette"].encode("utf-8"))
                #Mise à jour du fichier en uploadant le contenu du Filesystem
                if image:
                    fichier.setImage(open("%s/%s/Fichiers/%s/file/%s" % (value, utilisateur, infosObj["id"], idFichier), "r"))
                    dicoFichiers[idObj] = "Image"
                else:
                    print idFichier
                    fichier.setFile(open("%s/%s/Fichiers/%s/file/%s" % (value, utilisateur, infosObj["id"], idFichier), "r"))
                    dicoFichiers[idObj] = "File"
                fichier.setFilename(idFichier.encode("utf-8"))
                fichier.reindexObject()
        if listeSubject:
            home.setSubject(tuple(listeSubject))
        home.reindexObject()
        return dicoFichiers

    def addConnect(self, value, utilisateur):
        #print "------- addConnect -------"
        #Recherche du dossier de l'utilisateur
        contenuDossier = os.listdir("%s/%s/" % (value, utilisateur))
        #Vérification du fichier d'importation de cours "exportCours.json"
        if not "exportConnect.json" in contenuDossier:
            return None
        portal = getSite()
        try:
            motdepasse = open('%s/%s/exportConnect.json' % (value, utilisateur), 'r').read()
        except:
            raise Invalid(_(u"addConnect JSON : %s " % utilisateur))
        #Récupération des modèles
        home = getattr(getattr(portal.Members, utilisateur), "Webconference")
        home.connect('connexion', {})
        userConnect = home.connect('rechercherIdUser', utilisateur)
        if userConnect:
            dossiers = home.connect("getAttribut", {"attribut": "dossiers"})
            if dossiers:
                for ligne in dossiers.split("\n"):
                    repertoire, modele = ligne.split(":")
                    #Récupération du répertoire du membre en fonction du modele
                    home = getattr(getattr(portal.Members, utilisateur), repertoire)
                    #Sauvegarde du mot de pass
                    home.setComplement(motdepasse)
                    home.reindexObject()
                    session = home.getSessionConnect(utilisateur)
                    home.getContents("", "JalonConnect", utilisateur, repertoire)
                    try:
                        home.getContents("", "JalonConnect", utilisateur, repertoire)
                    except:
                        raise Invalid(_(u"addConnect : %s " % utilisateur))

    def addTermeGlossaire(self, value, utilisateur):
        #print "------- addTermeGlossaire -------"
        #Recherche du dossier de l'utilisateur
        contenuDossier = os.listdir("%s/%s/" % (value, utilisateur))
        #Vérification du fichier d'importation de cours "exportGlossaire.json"
        if not "exportGlossaire.json" in contenuDossier:
            return None
        #Chargement du fichier
        try:
            listeObj = json.load(open('%s/%s/exportGlossaire.json' % (value, utilisateur), 'r'))
        except:
            raise Invalid(_(u"addTermeGlossaire : %s " % utilisateur))
        portal = getSite()
        home = getattr(getattr(portal.Members, utilisateur), "Glossaire")
        num = 1
        for infosObj in listeObj:
            idobj = infosObj["id"].replace(".", "-")
            #Création d'une image sous Plone
            home.invokeFactory(type_name='JalonTermeGlossaire', id=idobj)
            #print "%s : addTermeGlossaire : %s" % (str(num), idobj)
            num = num + 1
            #Récupération de l'objet
            fichier = getattr(home, idobj)
            fichier.manage_setLocalRoles(utilisateur, ["Owner"])
            #Mise à jour des données
            fichier.setTitle(infosObj["titre"].encode("utf-8"))
            fichier.setDescription(infosObj["description"].encode("utf-8"))
            home.setTagDefaut(fichier)
            fichier.reindexObject()
        home.reindexObject()

    def addRessourceExterne(self, value, utilisateur):
        #print "------- addRessourceExterne -------"
        #Recherche du dossier de l'utilisateur
        contenuDossier = os.listdir("%s/%s/" % (value, utilisateur))
        #Vérification du fichier d'importation de cours "exportExternes.json"
        if not "exportExternes.json" in contenuDossier:
            return {}
        #Chargement du fichier
        dicoExternes = {}
        try:
            listeObj = json.load(open('%s/%s/exportExternes.json' % (value, utilisateur), 'r'))
        except:
            raise Invalid(_(u"addRessourceExterne : %s " % utilisateur))
        portal = getSite()
        dicoType = {u"Lien URL"                   : u"Lien web"
                   ,u"Lien Vidéo"                 : u"Lecteur exportable"
                   ,u"Référence Bibliographique"  : u"Ressource bibliographique"
                   ,u"Référence Bilbliographique" : u"Ressource bibliographique"}
        home = getattr(getattr(portal.Members, utilisateur), "Externes")
        num = 1
        for infosObj in listeObj:
            idobj = infosObj["id"].replace(".", "-")
            #Création d'une image sous Plone
            home.invokeFactory(type_name='JalonRessourceExterne', id=idobj)
            #print "%s : addRessourceExterne : %s" % (str(num), idobj)
            num = num + 1
            #Récupération de l'objet
            fichier = getattr(home, idobj)
            fichier.manage_setLocalRoles(utilisateur, ["Owner"])
            #Mise à jour des données
            fichier.setProperties({"Title"                : infosObj["titre"].encode("utf-8")
                                  ,"Description"          : infosObj["description"].encode("utf-8")
                                  ,"TypeRessourceExterne" : dicoType[infosObj["type"]]
                                  ,"Urlbiblio"            : infosObj["lien"]
                                  ,"Lecteur"              : infosObj["lien"]})
            home.setTagDefaut(fichier)
            fichier.reindexObject()
            dicoExternes[idobj] = dicoType[infosObj["type"]]
        home.reindexObject()
        return dicoExternes

    def genererExternes(self, value, utilisateur, dicoExternes):
        try:
            contenuDossier = os.listdir("%s/%s/" % (value, utilisateur))
        except:
            return dicoExternes
        #Vérification du fichier d'importation de cours "exportExternes.json"
        if not "exportExternes.json" in contenuDossier:
            return dicoExternes
        #Chargement du fichier
        try:
            listeObj = json.load(open('%s/%s/exportExternes.json' % (value, utilisateur), 'r'))
        except:
            raise Invalid(_(u"addRessourceExterne : %s " % utilisateur))
        dicoType = {u"Lien URL"                   : u"Lien web"
                   ,u"Lien Vidéo"                 : u"Lecteur exportable"
                   ,u"Référence Bibliographique"  : u"Ressource bibliographique"
                   ,u"Référence Bilbliographique" : u"Ressource bibliographique"}
        for infosObj in listeObj:
            idobj = infosObj["id"].replace(".", "-")
            dicoExternes[idobj] = dicoType[infosObj["type"]]
        return dicoExternes

    def genererFichiers(self, value, utilisateur, dicoFichiers):
        try:
            contenuDossier = os.listdir("%s/%s/" % (value, utilisateur))
        except:
            return dicoFichiers
        #Vérification du fichier d'importation de cours "exportCours.json"
        if not "exportFichiers.json" in contenuDossier:
            return dicoFichiers
        #Chargement du fichier
        try:
            listeObj = json.load(open('%s/%s/exportFichiers.json' % (value, utilisateur), 'r'))
        except:
            raise Invalid(_(u"addFichiers : %s " % utilisateur))
        for infosObj in listeObj:
            image = False
            try:
                idFichier = os.listdir("%s/%s/Fichiers/%s/file/" % (value, utilisateur, infosObj["id"]))[-1]
            except:
                idFichier = None
            if idFichier:
                extension = idFichier.split(".")[-1]
                idObj = infosObj["id"].replace(".", "-")
                if extension in ["jpg", "jpeg", "gif", "png", "bmp"]:
                    image = True
                if image:
                    dicoFichiers[idObj] = "Image"
                else:
                    dicoFichiers[idObj] = "File"
        return dicoFichiers

    def addCours(self, value, utilisateur):
        #print "------- addCours -------"
        #Recherche du dossier de l'utilisateur
        utilisateur = utilisateur.split(".json")[0][11:]
        contenuDossier = os.listdir("%s" % value)
        #Vérification du fichier d'importation de cours "exportCours.json"
        idExport = u"exportCours%s.json" % utilisateur
        if not idExport in contenuDossier:
            return None
        #Chargement du fichier
        try:
            dicoCours = json.load(open('%s/%s' % (value, idExport), 'r'))
        except:
            raise Invalid(_(u"addCours : %s " % utilisateur))
        dicoExternes = self.genererExternes("/home/zope/sites/jalon/jalonv2fait", utilisateur, {})
        dicoFichiers = self.genererFichiers("/home/zope/sites/jalon/jalonv2fait", utilisateur, {})
        portal = getSite()
        Cours = getattr(portal.cours, utilisateur)
        num = 1
        for infosCours in dicoCours:
            Cours.invokeFactory(type_name='JalonCours', id=infosCours["idcours"])
            #print "%s : addCours : %s " % (str(num), infosCours["idcours"])
            num = num + 1
            cours = getattr(Cours, infosCours["idcours"])
            #Mise à jour des permissions
            cours.manage_setLocalRoles(utilisateur, ["Owner"])
            #Mise à jour des informations
            cours.setTitle(infosCours["titre"].encode("utf-8"))
            cours.setAuteurs({"auteurs": "auteur", "username": utilisateur})
            if infosCours["coAuteurs"]:
                cours.setAuteurs({"auteurs": "coAuteurs", "username": infosCours["coAuteurs"]})
                for coAuteur in infosCours["coAuteurs"].split(","):
                    dicoExternes = self.genererExternes("/home/zope/sites/jalon/jalonv2fait", coAuteur, dicoExternes)
                    dicoFichiers = self.genererFichiers("/home/zope/sites/jalon/jalonv2fait", coAuteur, dicoFichiers)
            if infosCours["coLecteurs"]:
                cours.setAuteurs({"auteurs": "coLecteurs", "username": infosCours["coLecteurs"]})
            heure = str(time.clock()).replace(".", "")
            for composant in infosCours["plan"]:
                if composant["type"] in ["Titre", "TexteLibre"]:
                    now = DateTime()
                    idElement = "%s-%s-%s" % (composant["type"], utilisateur, ''.join([now.strftime('%Y%m%d'), str(heure)]))
                    cours.ajouterInfosElement(idElement.encode("utf-8"), composant["type"].encode("utf-8"), composant["titre"].encode("utf-8"), utilisateur.encode("utf-8"))
                    cours.ajouterElementPlan(idElement.encode("utf-8"))
                    #print "addCours Element : %s , %s" % (idElement.encode("utf-8"), composant["titre"].encode("utf-8"))
                    heure = int(heure) + 1
                else:
                    if composant["type"] == "Fichier":
                        try:
                            cours.ajouterElement(composant["id"].encode("utf-8"), dicoFichiers[composant["id"]].encode("utf-8"), composant["titre"].encode("utf-8"), composant["createur"].encode("utf-8"))
                        except:
                            print "addCours Element Fichier : %s , %s" % (composant["id"].encode("utf-8"), composant["titre"].encode("utf-8"))
                    if composant["type"] == "Ressources Externes":
                        try:
                            cours.ajouterElement(composant["id"].encode("utf-8"), dicoExternes[composant["id"]].encode("utf-8"), composant["titre"].encode("utf-8"), composant["createur"].encode("utf-8"))
                        except:
                            print "addCours Element Ressources Externes : %s , %s" % (composant["id"].encode("utf-8"), composant["titre"].encode("utf-8"))
                    if composant["type"] == "Webconference":
                        try:
                            cours.ajouterElement(composant["id"].encode("utf-8"), "Webconference".encode("utf-8"), composant["titre"].encode("utf-8"), composant["createur"].encode("utf-8"))
                        except:
                            print "addCours Element Webconference : %s , %s %s" % (composant["id"].encode("utf-8"), composant["titre"].encode("utf-8"), composant["createur"].encode("utf-8"))
                    if composant["type"] == "Presentation sonirisee":
                        try:
                            cours.ajouterElement(composant["id"].encode("utf-8"), "Presentations sonorisees".encode("utf-8"), composant["titre"].encode("utf-8"), composant["createur"].encode("utf-8"))
                        except:
                            print "addCours Element Presentation sonirisee : %s , %s %s" % (composant["id"].encode("utf-8"), composant["titre"].encode("utf-8"), composant["createur"].encode("utf-8"))
                    if composant["type"] == "Sujet de dicussion":
                        idactivite = cours.creerSousObjet("Forum".encode("utf-8"), composant["titre"].encode("utf-8"), composant["description"].encode("utf-8"), composant["createur"].encode("utf-8"), None, None)
                        cours.ajouterElement(idactivite.encode("utf-8"), "Forum".encode("utf-8"), composant["titre"].encode("utf-8"), composant["createur"].encode("utf-8"))
                        #print "addCours Element : %s , %s" % (composant["id"].encode("utf-8"), composant["titre"].encode("utf-8"))
                    if composant["type"] == "Bo&icirc;te de d&eacute;p&ocirc;ts":
                        idactivite = cours.creerSousObjet("BoiteDepot".encode("utf-8"), composant["titre"].encode("utf-8"), composant["description"].encode("utf-8"), composant["createur"].encode("utf-8"), None, None)
                        cours.ajouterElement(idactivite, "BoiteDepot".encode("utf-8"), composant["titre"].encode("utf-8"), composant["createur"].encode("utf-8"))
                        if composant["sujets"] != [] or composant["corrections"] != []:
                            boite = getattr(cours, idactivite)
                            for sujet in composant["sujets"]:
                                if sujet["typeElement"] == "Fichier":
                                    try:
                                        boite.ajouterElement("sujets".encode("utf-8"), sujet["id"].encode("utf-8"), dicoFichiers[sujet["id"]], sujet["titreElement"].encode("utf-8"), sujet["createurElement"].encode("utf-8"))
                                    except:
                                        print "add Element Boite Fichier : %s , %s %s" % (sujet["id"].encode("utf-8"), sujet["titreElement"].encode("utf-8"), sujet["createurElement"].encode("utf-8"))
                                if sujet["typeElement"] == "Ressources Externes":
                                    try:
                                        boite.ajouterElement("sujets".encode("utf-8"), sujet["id"].encode("utf-8"), dicoExternes[sujet["id"]], sujet["titreElement"].encode("utf-8"), sujet["createurElement"].encode("utf-8"))
                                    except:
                                        print "add Element Boite Ressources Externes : %s , %s %s" % (sujet["id"].encode("utf-8"), sujet["titreElement"].encode("utf-8"), sujet["createurElement"].encode("utf-8"))
                                if sujet["typeElement"] == "Webconference":
                                    try:
                                        boite.ajouterElement("sujets".encode("utf-8"), sujet["id"].encode("utf-8"), "Webconference".encode("utf-8"), sujet["titreElement"].encode("utf-8"), sujet["createurElement"].encode("utf-8"))
                                    except:
                                        print "add Element Boite Webconference : %s , %s %s" % (sujet["id"].encode("utf-8"), sujet["titreElement"].encode("utf-8"), sujet["createurElement"].encode("utf-8"))
                                if sujet["typeElement"] == "Presentation sonirisee":
                                    try:
                                        boite.ajouterElement("sujets".encode("utf-8"), sujet["id"].encode("utf-8"), "Presentations sonorisees".encode("utf-8"), sujet["titreElement"].encode("utf-8"), sujet["createurElement"].encode("utf-8"))
                                    except:
                                        print "add Element Boite Presentation sonirisee : %s , %s %s" % (sujet["id"].encode("utf-8"), sujet["titreElement"].encode("utf-8"), sujet["createurElement"].encode("utf-8"))
                            for correction in composant["corrections"]:
                                if correction["typeElement"] == "Fichier":
                                    try:
                                        boite.ajouterElement("corrections".encode("utf-8"), correction["id"].encode("utf-8"), dicoFichiers[correction["id"]].encode("utf-8"), correction["titreElement"].encode("utf-8"), correction["createurElement"].encode("utf-8"))
                                    except:
                                        print "add Element Boite Fichier : %s , %s %s" % (correction["id"], correction["titreElement"].encode("utf-8"), correction["createurElement"].encode("utf-8"))
                                if correction["typeElement"] == "Ressources Externes":
                                    try:
                                        boite.ajouterElement("corrections".encode("utf-8"), correction["id"].encode("utf-8"), dicoExternes[correction["id"]].encode("utf-8"), correction["titreElement"].encode("utf-8"), correction["createurElement"].encode("utf-8"))
                                    except:
                                        print "add Element Boite Ressources Externes : %s , %s %s" % (correction["id"], correction["titreElement"].encode("utf-8"), correction["createurElement"].encode("utf-8"))
                                if correction["typeElement"] == "Webconference":
                                    try:
                                        boite.ajouterElement("corrections".encode("utf-8"), correction["id"].encode("utf-8"), "Webconference".encode("utf-8"), correction["titreElement"].encode("utf-8"), correction["createurElement"].encode("utf-8"))
                                    except:
                                        print "add Element Boite Webconference : %s , %s %s" % (correction["id"].encode("utf-8"), correction["titreElement"].encode("utf-8"), correction["createurElement"].encode("utf-8"))
                                if correction["typeElement"] == "Presentation sonirisee":
                                    try:
                                        boite.ajouterElement("corrections".encode("utf-8"), correction["id"].encode("utf-8"), "Presentations sonorisees".encode("utf-8"), correction["titreElement"].encode("utf-8"), correction["createurElement"].encode("utf-8"))
                                    except:
                                        print "add Element Boite Presentation sonirisee : %s , %s %s" % (correction["id"].encode("utf-8"), correction["titreElement"].encode("utf-8"), correction["createurElement"].encode("utf-8"))
                        #print "addCours Element : %s , %s" % (composant["id"], composant["titre"].encode("utf-8"))
            cours.invokeFactory(type_name='Folder', id="annonce")
            cours.reindexObject()
        Cours.reindexObject()

    def set_chemin_repertoire(self, value):
        self.jiProps._updateProperty('chemin_repertoire', value)
        #print "--------- set_chemin_repertoire ---------"
        if value != '':
            #portal = getSite()
            #Members = getattr(portal, "Members")
            #listeMembre = Members.objectIds()
            listeDir = os.listdir(value)
            listeDir.sort()
            for utilisateur in listeDir:
                #Test d'un utilisateur déjà existant, on ignore les fichiers commençant par un .
                if not utilisateur.startswith("."):
                    #if not utilisateur in listeMembre and not utilisateur.startswith("."):
                    self.addRepertoireMembre(utilisateur)
                    self.addFichiers(value, utilisateur)
                    #self.addExosWIMS(value, utilisateur)
                    #self.addConnect(value, utilisateur)
                    #self.addTermeGlossaire(value, utilisateur)
                    #dicoExternes = self.addRessourceExterne(value, utilisateur)
                self.addCours(value, utilisateur)

    chemin_repertoire = property(get_chemin_repertoire, set_chemin_repertoire)


class JalonImportControlPanel(ControlPanelForm):
    label = _("Jalon Import settings")
    description = _("""Import les contenus de Jalon V2 depuis un dossier du filesystem""")
    form_name = _("Jalon Import settings")
    form_fields = FormFields(IJalonImportControlPanel)
