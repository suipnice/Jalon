# -*- coding: utf-8 -*-
from zope.interface import implements
from OFS.SimpleItem import SimpleItem

from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot

from sqlite3 import dbapi2 as sqlite

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from interfaces import IJalonBDD
from jalon.bdd import contentMessageFactory as _
from jalon.content.content import jalon_utils

import jalonsqlite
import os
import os.path
import sqlite3
import json

from DateTime import DateTime


class JalonBDD(SimpleItem):

    implements(IJalonBDD)
    _urlConnexion = "/home/zope/sites/bdd_jalon/"
    _typeBDD = "sqlite"
    _typeBDDActif = ""
    Session = sessionmaker()

    _activer_stockage_connexion = 1
    _activer_stockage_consultation = 1

    #mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>
    _use_mysql      = 1   
    _host_mysql     = "192.168.56.30"
    _user_mysql     = "zope"
    _password_mysql = "azerty"
    _port_mysql     = 3306
    _db_name_mysql   = "jalon"

    def __init__(self, *args, **kwargs):
        super(JalonBDD, self).__init__(*args, **kwargs)

    #-------------------------------------#
    # Gestion des variables du connecteur #
    #-------------------------------------#
    def getUrlConnexion(self):
        return self._urlConnexion

    def setUrlConnexion(self, urlConnexion):
        self._urlConnexion = urlConnexion

    def getTypeBDD(self):
        return self._typeBDD

    def setTypeBDD(self, typeBDD):
        self._typeBDD = typeBDD

    def getVariablesBDD(self):
        return {"typeBDD"                      : self._typeBDD,
                "urlConnexion"                 : self._urlConnexion,
                "activerStockageConnexion"     : self._activer_stockage_connexion,
                "activerStockageConsultation"  : self._activer_stockage_consultation,
                "host_mysql"                   : self._host_mysql,
                "user_mysql"                   : self._user_mysql,
                "password_mysql"               : self._password_mysql,
                "port_mysql"                   : self._port_mysql,
                "db_name_mysql"                : self._db_name_mysql}

    def setVariablesBDD(self, variablesBDD):
        # s'il n'y a aucun type renseigné ou alors aucune url de connexion
        retour = 1
        if (variablesBDD["typeBDD"] == '' or variablesBDD["urlConnexion"] == ''):
            return 0
        if variablesBDD["typeBDD"] == "sqlite" and (not os.path.exists(variablesBDD["urlConnexion"])):
            # si sqlite et le chemin filesystem n'est pas valide
            return 2
        else:
            # si le chemin filesystem est valide mais le fichier jalonBDD.db n'existe pas
            liste_export = os.listdir(variablesBDD["urlConnexion"])
            if not "jalonBDD.db" in liste_export:
                self.creerBDD(variablesBDD)
                retour = 3
        for key in variablesBDD.keys():
            val = variablesBDD[key]
            if key.startswith("activer"):
                val = int(val)
            setattr(self, "_%s" % key, val)
        #self._typeBDD = variablesBDD["typeBDD"]
        #self._urlConnexion = variablesBDD["urlConnexion"]
        self._typeBDDActif = ""
        return retour

    def creerBDD(self, variablesBDD=None):
        if variablesBDD:
            chemin = variablesBDD["urlConnexion"]
        else:
            chemin = self._urlConnexion

        #print "-------------- création et connexion jalonBDD.db --------------"
        conn = sqlite3.connect('%s/jalonBDD.db' % chemin)
        c = conn.cursor()

        #creation tables
        c.execute('''CREATE TABLE individu_lite
                        (SESAME_ETU TEXT PRIMARY KEY, DATE_NAI_IND TEXT, LIB_NOM_PAT_IND TEXT, LIB_NOM_USU_IND TEXT, LIB_PR1_IND TEXT, TYPE_IND TEXT, COD_ETU INTEGER, EMAIL_ETU TEXT, ADR1_IND TEXT, ADR2_IND TEXT, COD_POST_IND TEXT, VIL_IND TEXT, UNIV_IND TEXT, PROMO_IND TEXT, STATUS_IND TEXT)''')
        c.execute('''CREATE TABLE element_pedagogi_lite
                        (COD_ELP TEXT PRIMARY KEY, LIB_ELP TEXT, ETU_ELP INTEGER, ENS_ELP INTEGER, TYP_ELP TEXT, COD_GPE TEXT, DATE_CREATION TEXT, DATE_MODIF TEXT)''')
        c.execute('''CREATE TABLE etp_regroupe_elp_lite
                        (PKEY INTEGER PRIMARY KEY AUTOINCREMENT, COD_ELP_PERE TEXT, COD_ELP_FILS TEXT, TYP_ELP TEXT,
                        FOREIGN KEY(COD_ELP_PERE) REFERENCES element_pedagogi_lite(COD_ELP),
                        FOREIGN KEY(COD_ELP_FILS) REFERENCES element_pedagogi_lite(COD_ELP))''')
        c.execute('''CREATE TABLE ind_contrat_elp_lite
                        (SESAME_ETU TEXT, COD_ELP TEXT, TYPE_ELP TEXT, COD_ELP_PERE TEXT, RESPONSABLE BOOLEAN, PRIMARY KEY (SESAME_ETU, COD_ELP, COD_ELP_PERE))''')
        c.execute('''CREATE TABLE actualites_cours
                        (ID_COURS TEXT, TYPE_IND TEXT, COD_ELP TEXT, TITRE_COURS TEXT, ACTU_COURS TEXT, PRIMARY KEY (ID_COURS, TYPE_IND))''')
        c.execute('''CREATE TABLE connexion
                        (NUM_CONN INTEGER PRIMARY KEY AUTOINCREMENT, SESAME_ETU TEXT, DATE_CONN TEXT, FOREIGN KEY(SESAME_ETU) REFERENCES individu_lite(SESAME_ETU))''')
        c.execute('''CREATE TABLE consultationCours
                        (NUM_CONN INTEGER PRIMARY KEY AUTOINCREMENT, SESAME_ETU TEXT, DATE_CONS TEXT, ID_COURS TEXT, TYPE_CONS TEXT, ID_CONS TEXT, FOREIGN KEY(SESAME_ETU) REFERENCES individu_lite(SESAME_ETU))''')
        conn.commit()

        if self._use_mysql:
            import MySQLdb
            db = MySQLdb.connect(host=self._host_mysql, port=self._port_mysql, passwd=self._password_mysql, db=self._db_name_mysql)
            c = db.cursor()
            c.execute('''CREATE TABLE individu
                            (SESAME_ETU TEXT PRIMARY KEY, LIB_NOM_PAT_IND TEXT, LIB_NOM_USU_IND TEXT, LIB_PR1_IND TEXT, TYPE_IND TEXT, COD_ETU INTEGER, EMAIL_ETU TEXT)''')
            c.execute('''CREATE TABLE connexion
                            (NUM_CONN INTEGER PRIMARY KEY AUTOINCREMENT, SESAME_ETU TEXT, DATE_CONN TEXT, FOREIGN KEY(SESAME_ETU) REFERENCES individu(SESAME_ETU))''')
            c.execute('''CREATE TABLE consultationCours
                            (NUM_CONN INTEGER PRIMARY KEY AUTOINCREMENT, SESAME_ETU TEXT, DATE_CONS TEXT, ID_COURS TEXT, TYPE_CONS TEXT, ID_CONS TEXT, FOREIGN KEY(SESAME_ETU) REFERENCES individu(SESAME_ETU))''')
            c.commit()

    #----------------------------#
    # Utilitaire base de données #
    #----------------------------#
    def getSession(self):
        #print "----------- getSession -----------"
        try:
            self.Session().get_bind()
            #print self.Session()
        except:
            #print "except Session"
            self._typeBDDActif = None
        if (not self._typeBDDActif) or (self._typeBDDActif != self._typeBDD):
            #print "initialiser session"
            try:
                self.Session().close()
            except:
                pass
            if self._typeBDD == "sqlite":
                #print "sqlite:///%s/jalonBDD.db" % self._urlConnexion
                engine = create_engine("sqlite:///%s/jalonBDD.db" % self._urlConnexion, module=sqlite, echo=False, poolclass=NullPool)
            if self._typeBDD == "apogee":
                engine = create_engine("apogee:///%s/jalonBDD.db" % self._urlConnexion, echo=False, poolclass=NullPool)
            #print "ouverture connexion"
            self.Session.configure(bind=engine)
            self._typeBDDActif = self._typeBDD
        return self.Session()

    #-------------------------------------#
    # Interrogation de la base de données #
    #-------------------------------------#
    def getIndividuLITE(self, sesame):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            result = jalonsqlite.getIndividuLITE(session, sesame)
            if result:
                return result[0]
            else:
                return None

    def getTousIndividuLITE(self, page):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getTousIndividuLITE(session, int(page))

    def getNbPagesInd(self):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getNbPagesInd(session)

    def getUtilisateursNonInscrits(self, COD_ELP, TYPE_IND):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getUtilisateursNonInscrits(session, COD_ELP, TYPE_IND)

    def getIndividus(self, listeSesames):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getIndividus(session, listeSesames)

    def getInfosELP(self, COD_ELP):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getInfosELP(session, COD_ELP)

    def getInfosToutesELP(self, page):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getInfosToutesELP(session, int(page))

    def getInfosElpParType(self, TYP_ELP=None, page=None):
        if not TYP_ELP:
            return []
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getInfosElpParType(session, TYP_ELP, page)

    def getInfosToutesELPorRecherche(self, page, typeRecherche, termeRecherche):
        if typeRecherche or termeRecherche:
            if termeRecherche:
                termeRecherche.strip()
                termeRecherche = "%" + termeRecherche + "%"
                termeRecherche = termeRecherche.replace(" ", "% %")
                listeRecherche = termeRecherche.split(" ")
            else:
                listeRecherche = ["%"]

            resultat = None
            if not typeRecherche:
                resultat = self.rechercherAll(listeRecherche)
            else:
                if typeRecherche == "etape":
                    resultat = self.rechercherEtape(listeRecherche)
                if typeRecherche == "ue":
                    resultat = self.rechercherELP(listeRecherche, 0)
                if typeRecherche == "uel":
                    resultat = self.rechercherELP(listeRecherche, 1)
                if typeRecherche == "groupe":
                    resultat = self.rechercherGPE(listeRecherche)
            if resultat:
                return self.ajouterResponsable(resultat)
            return None
        else:
            return self.getInfosToutesELP(page)

    def getToutesInfosELP(self, COD_ELP):
        session = self.getSession()
        #if self._typeBDD == "sqlite":
        infosElp = jalonsqlite.getInfosELP(session, COD_ELP)
        infosElp =  self.ajouterResponsable([infosElp])[0]
        infosElp["etape"] = len(self.getElpAttach(COD_ELP, "etape", infosElp["TYP_ELP"]))
        infosElp["ue"] = len(self.getElpAttach(COD_ELP, "ue", infosElp["TYP_ELP"]))
        infosElp["uel"] = len(self.getElpAttach(COD_ELP, "uel", infosElp["TYP_ELP"]))
        infosElp["groupe"] = len(self.getElpAttach(COD_ELP, "groupe", infosElp["TYP_ELP"]))
        return infosElp

    def ajouterResponsable(self, listeElp):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.ajouterResponsable(session, listeElp)

    def getNbPagesELP(self):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getNbPagesELP(session)

    def getNbPagesELPByType(self, TYP_ELP):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getNbPagesELPByType(session, TYP_ELP)

    def getInfosEtape(self, COD_ETP):
        session = self.getSession()
        return jalonsqlite.getInfosEtape(session, COD_ETP)

    def getInfosGPE(self, COD_GPE):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getInfosGPE(session, COD_GPE)

    def getInfosELP2(self, COD_ELP):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getInfosELP2(session, COD_ELP)

    def getInscriptionPedago(self, COD_ETU, COD_ELP):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getInscriptionPedago(session, COD_ETU, COD_ELP)
        if self._typeBDD == "apogee":
            COD_ETP, COD_VRS_VET = COD_ELP.rsplit("-", 1)
            return jalonsqlite.getInscriptionPedago(session, COD_ETU, COD_ETP, int(COD_VRS_VET))

    def getInscriptionIND(self, SESAME_ETU, TYP_ELP_SELECT):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getInscriptionIND(session, SESAME_ETU, TYP_ELP_SELECT)

    def getGroupesEtudiant(self, COD_ETU):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getGroupesEtudiant(session, COD_ETU)

    def getUeEtape(self, COD_ELP, COD_VRS_VET=None, TYP_ELP_SELECT="ue"):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getUeEtape(session, COD_ELP, TYP_ELP_SELECT=TYP_ELP_SELECT)
        if self._typeBDD == "apogee":
            COD_ETP, COD_VRS_VET = COD_ELP.rsplit("-", 1)
            return jalonsqlite.getUeEtape(session, COD_ELP, int(COD_VRS_VET), TYP_ELP_SELECT)

    def getEnfantELP(self, COD_ELP, TYP_ELP_SELECT=None):
        session = self.getSession()
        return jalonsqlite.getEnfantELP(session, COD_ELP, TYP_ELP_SELECT)

    def getVersionEtape(self, COD_ELP, COD_VRS_VET=None):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getVersionEtape(session, COD_ELP)
        if self._typeBDD == "apogee":
            COD_ETP, COD_VRS_VET = COD_ELP.rsplit("-", 1)
            return jalonsqlite.getVersionEtape(session, COD_ETP, int(COD_VRS_VET))

    def getElpAttach(self, COD_ELP, TYP_ELP_SELECT, TYP_ELP):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getElpAttach(session, COD_ELP, TYP_ELP_SELECT, TYP_ELP)

    def rechercherAll(self, listeRecherche):
        session = self.getSession()
        #if self._typeBDD == "sqlite":
        return jalonsqlite.rechercherAll(session, listeRecherche)

    def rechercherEtape(self, listeRecherche):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.rechercherEtape(session, listeRecherche)

    def rechercherELP(self, listeRecherche, uel):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.rechercherELP(session, listeRecherche, uel)

    def rechercherGPE(self, listeRecherche):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.rechercherGPE(session, listeRecherche)

    def rechercherEtudiantXLS(self, COD_ELP):
        session = self.getSession()
        return jalonsqlite.rechercherEtudiantXLS(session, COD_ELP, "Etudiant")

    def rechercherUtilisateurs(self, COD_ELP, TYPE_IND, inscrit=None, listeEtu=None, Resp=None):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.rechercherUtilisateurs(session, COD_ELP, TYPE_IND, inscrit, listeEtu, Resp)

    def rechercheApogee(self, typeRecherche, termeRecherche):
        if not termeRecherche:
            return None
        termeRecherche.strip()
        termeRecherche = "%" + termeRecherche + "%"
        termeRecherche = termeRecherche.replace(" ", "% %")
        listeRecherche = termeRecherche.split(" ")

        if typeRecherche == "etape":
            return self.rechercherEtape(listeRecherche)
        if typeRecherche == "ue":
            return self.rechercherELP(listeRecherche, 0)
        if typeRecherche == "uel":
            return self.rechercherELP(listeRecherche, 1)
        if typeRecherche == "groupe":
            return self.rechercherGPE(listeRecherche)
        return None

    def rechercherUtilisateursByName(self, termeRecherche, typeUser, isJson=False):
        if not termeRecherche:
            return None
        termeRecherche.strip()
        termeRecherche = "%" + termeRecherche + "%"
        termeRecherche = termeRecherche.replace(" ", "% %")
        listeRecherche = termeRecherche.split(" ")
        session = self.getSession()
        if self._typeBDD == "sqlite":
            resultat = jalonsqlite.rechercherUtilisateursByName(session, listeRecherche, typeUser)
            if resultat:
                if isJson:
                    return json.dumps(resultat)
                else:
                    return resultat
            else:
                return []

    def rechercherUtilisateursByNameOrType(self, termeRecherche, typeUser, page=None):
        listeRecherche = []
        if termeRecherche:
            termeRecherche.strip()
            termeRecherche = "%" + termeRecherche + "%"
            termeRecherche = termeRecherche.replace(" ", "% %")
            listeRecherche = termeRecherche.split(" ")

        session = self.getSession()
        if self._typeBDD == "sqlite":
            resultat = jalonsqlite.rechercherUtilisateursByNameOrType(session, listeRecherche, typeUser, page)
            if resultat:
                return resultat
            else:
                return []

    def rechercherEnseignantResp(self, code):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            resultat = jalonsqlite.rechercherEnseignantResp(session, code)
            if resultat:
                return resultat[0]

    def isUtilisateurNotActif(self, SESAME_ETU):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            resultat = jalonsqlite.isINDActif(session, SESAME_ETU)
            if resultat and (resultat[0]["STATUS_IND"] == "closed"):
                return True
        return False

    #-------------------------------------#
    # Modification de la base de données  #
    #-------------------------------------#
    def addConnexionUtilisateur(self, SESAME_ETU, DATE_CONN):
        if self._activerStockageConnexion:
            session = self.getSession()
            if self._typeBDD == "sqlite":
                return jalonsqlite.addConnexionIND(session, SESAME_ETU, DATE_CONN)

    def setInfosELP(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.setInfosELP(session, param)

    def insererELP(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.insererELP(session, param)

    def supprimerELP(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.supprimerELP(session, param)

    def creerUtilisateurTest(self, param):
        session = self.getSession()
        jalonsqlite.creerUtilisateur(session, param)

    def creerUtilisateur(self, param):
        retour = 0
        session = self.getSession()
        if self._typeBDD == "sqlite":
            retour = jalonsqlite.creerUtilisateur(session, param)

        if retour:
            sesame = param["SESAME_ETU"].replace(" ", "")
            portal_membership = getToolByName(self, 'portal_membership')
            #if not portal_membership.getMemberById(param["SESAME_ETU"]):
            portal_registration = getToolByName(self, 'portal_registration')
            if not "PASSWORD" in param:
                param["PASSWORD"] = portal_registration.generatePassword()
            #fullname = "%s %s" % (param["LIB_NOM_PAT_IND"].capitalize(), param["LIB_PR1_IND"].capitalize())
            roles = (param["TYPE_IND"], "Member",)
            if param["TYPE_IND"] == "Secretaire":
                roles = ("Personnel", "Secretaire", "Member",)
            #portal_membership.addMember(sesame, param["PASSWORD"], roles, "", {"fullname": fullname, "email": param["EMAIL_ETU"]})
            portal_membership.addMember(sesame, param["PASSWORD"], roles, "")
            #try:
            #    portal_registration.registeredNotify(sesame)
            #except:
            #    pass

    def setInfosUtilisateurs(self, param):
        session = self.getSession()
        jalonsqlite.setInfosUtilisateurs(session, param)
        portal = self.aq_parent
        modMember = portal.portal_membership.getMemberById(param["SESAME_ETU"])
        modMember.fullname = "%s %s" % (param["LIB_NOM_PAT_IND"], param["LIB_PR1_IND"])
        modMember.email = param["EMAIL_ETU"]
        if "password" in param:
            portal.acl_users.source_users.updateUserPassword(param["SESAME_ETU"], param["password"])
            authMember = portal.portal_membership.getAuthenticatedMember()
            infos = jalon_utils.getInfosMembre(authMember.getId())
            message = 'Bonjour\n\nVotre mot de passe a été changé par "%s". Pour vous connecter à %s (%s) vous devez utiliser :\n\nNom d\'utilisateur : %s\nMot de passe : %s\n\nVous pouvez changer ce mot de passe en cliquant sur le lien suivant : %s/mail_password_form?userid=%s\n\nCordialement,\nL\'équipe %s.' % (infos["fullname"], portal.Title(), portal.absolute_url(), param["SESAME_ETU"].encode("UTF-8"), param["password"].encode("UTF-8"), portal.absolute_url(), param["SESAME_ETU"].encode("UTF-8"), portal.Title())
            jalon_utils.envoyerMail({"a"      : param["EMAIL_ETU"],
                                     "objet"  : "Nouveau mot de passe",
                                     "message": message})

    def attacherELP(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.attacherELP(session, param)

    def sattacherAELP(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.sattacherAELP(session, param)

    def detacherToutesELP(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.detacherToutesELP(session, param)

    def seDetacherToutesELP(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.seDetacherToutesELP(session, param)

    def detacherELP(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.detacherELP(session, param)

    def seDetacherDeELP(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.seDetacherDeELP(session, param)

    def inscrireEnsResp(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.inscrireEnsResp(session, param)

    def inscrireEnseignant(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.inscrireEnseignant(session, param)

    def inscrireEtudiant(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.inscrireEtudiant(session, param)

    def inscrireINDELP(self, SESAME_ETU, TYPE_ELP, LISTE_ELP):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.inscrireINDELP(session, SESAME_ETU, TYPE_ELP, LISTE_ELP)

    # suppression LISTE_ELP
    def desinscrireINDELP(self, SESAME_ETU, TYPE_ELP):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            # suppression LISTE_ELP
            return jalonsqlite.desinscrireINDELP(session, SESAME_ETU, TYPE_ELP)

    def desinscrireEnseignant(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.desinscrireEnseignant(session, param)

    def desinscrireEtudiant(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.desinscrireEtudiant(session, param)

    def supprUtilisateur(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.supprUtilisateur(session, param)

    def bloquerIndividu(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.bloquerIND(session, param)

    def activerIndividu(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.activerIND(session, param)

    def ajouterActuCours(self, param):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.ajouterActuCours(session, param)

    #------------------------#
    # Fonctions Statistiques #
    #------------------------#
    def updateTableConnexion(self):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.updateTableConnexion(session)

    def getIndByElp(self, COD_ELP):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getIndByElp(session, COD_ELP)

    def getConnexionCouranteByELP(self, COD_ELP):
        session = self.getSession()
        month = str(DateTime().month())
        if int(month) < 10:
            month = "0%s" % month
        year = str(DateTime().year())

        listeInds = self.getIndByElp(COD_ELP)
        if not listeInds:
            return {"mois" : "Aucun inscrit dans cet élément pédagigique",
                    "annee": "Aucun inscrit dans cet élément pédagigique"}
        coMois = jalonsqlite.getConnexionELPByMonth(session, COD_ELP, month, year, listeInds)
        coAnnee = jalonsqlite.getConnexionELPByYear(session, COD_ELP, year, listeInds)

        detailMois = ({"label" : "Janvier",   "nb" : 0},
                      {"label" : "Février",   "nb" : 0},
                      {"label" : "Mars",      "nb" : 0},
                      {"label" : "Avril",     "nb" : 0},
                      {"label" : "Mai",       "nb" : 0},
                      {"label" : "Juin",      "nb" : 0},
                      {"label" : "Juillet",   "nb" : 0},
                      {"label" : "Août",      "nb" : 0},
                      {"label" : "Septembre", "nb" : 0},
                      {"label" : "Octobre",   "nb" : 0},
                      {"label" : "Novembre",  "nb" : 0},
                      {"label" : "Décembre",  "nb" : 0})
        for connexion in coAnnee:
            month = DateTime(connexion[1]).month()
            detailMois[month - 1]["nb"] = detailMois[month - 1]["nb"] + 1

        return {"etu"  :      len(listeInds),
                "mois" :      coMois,
                "annee":      coAnnee.count(),
                "detailMois": detailMois,
                "graph"     : self.genererGraphConnexionCourante(detailMois)}

    def getConnexionELPByMonth(self, COD_ELP, month=None, year="%", listeInds=None):
        session = self.getSession()
        return jalonsqlite.getConnexionELPByMonth(session, COD_ELP, month, year, listeInds)

    def getConnexionELPByYear(self, COD_ELP, year=None, listeInds=None):
        session = self.getSession()
        return jalonsqlite.getConnexionELPByYear(session, COD_ELP, year, listeInds)

    def genererGraphConnexionCourante(self, listeMois):
        graph = ['<script type="text/javascript">']
        graph.append("var chartData = [")
        for mois in listeMois:
            graph.append("{")
            graph.append('  "month": "%s",' % mois["label"])
            graph.append('  "visits": %s' % mois["nb"])
            graph.append('},')
        graph.append('];')

        graph.append('''
        AmCharts.ready(function() {
            var chart = new AmCharts.AmSerialChart();
            chart.dataProvider = chartData;
            chart.categoryField = "month";

            var categoryAxis = chart.categoryAxis;
            categoryAxis.labelRotation = 65;

            var graph = new AmCharts.AmGraph();
            graph.valueField = "visits";
            graph.type = "column";
            graph.fillAlphas = 0.8;
            chart.addGraph(graph);

            chart.write("chartdiv");
        });
        </script>''')
        return "\n".join(graph)

    def getIndAndNameByElp(self, COD_ELP):
        session = self.getSession()
        return jalonsqlite.getIndAndNameByElp(session, COD_ELP)

    def getConnexionByDateByELPByIND(self, COD_ELP, month, year):
        session = self.getSession()

        if not month or month == '0':
            month = DateTime().month()

        if not year or year == '0':
            year = DateTime().year()

        monthPrec = month - 1
        if monthPrec == 0:
            monthPrec = "12"
            yearPrec = year - 1
        else:
            yearPrec = year

        if int(month) < 10:
            month = "0%s" % str(month)
        else:
            month = str(month)
        year = str(year)

        if int(monthPrec) < 10:
            monthPrec = "0%s" % str(monthPrec)
        else:
            monthPrec = str(monthPrec)
        yearPrec = str(yearPrec)

        listeInds = self.getIndAndNameByElp(COD_ELP)
        if not listeInds:
            return {"etu" : []}

        listeSesames = self.getIndByElp(COD_ELP)

        dicoMoisInd = {}
        coMois = jalonsqlite.getConnexionELPByMonthByIND(session, COD_ELP, month, year, listeSesames)
        for ligne in coMois:
            dicoMoisInd[ligne[0]] = ligne[1]

        dicoMoisPrecInd = {}
        coMoisPrec = jalonsqlite.getConnexionELPByMonthByIND(session, COD_ELP, monthPrec, yearPrec, listeSesames)
        for ligne in coMoisPrec:
            dicoMoisPrecInd[ligne[0]] = ligne[1]

        dicoAnneeInd = {}
        coAnnee = jalonsqlite.getConnexionELPByYearByIND(session, COD_ELP, year, listeSesames)
        for ligne in coAnnee:
            dicoAnneeInd[ligne[0]] = ligne[1]

        return {"etu"  :    listeInds,
                "mois" :    dicoMoisInd,
                "moisPrec": dicoMoisPrecInd,
                "annee":    dicoAnneeInd}

    def getConnexionByIND(self, SESAME_ETU):
        session = self.getSession()
        dicoRetour = {}
        listeRetour = []

        dicoLabel = {1  : u"Janvier",
                     2  : u"Février",
                     3  : u"Mars",
                     4  : u"Avril",
                     5  : u"Mai",
                     6  : u"Juin",
                     7  : u"Juillet",
                     8  : u"Août",
                     9  : u"Septembre",
                     10 : u"Octobre",
                     11 : u"Novembre",
                     12 : u"Décembre"}

        listeConnexion = jalonsqlite.getConnexionByIND(session, SESAME_ETU)

        if listeConnexion:
            dicoRetour["first"] = jalon_utils.getLocaleDate(listeConnexion.first()[0], "%d/%m/%Y à %Hh%M")
            dicoRetour["last"] = jalon_utils.getLocaleDate(listeConnexion.all()[-1][0], "%d/%m/%Y à %Hh%M")
            dicoRetour["total"] = listeConnexion.count()

            i = 0
            monthP = 0
            for connexion in listeConnexion:
                year = connexion[0].split("/")[0]
                month = connexion[0].split("/")[1]
                if i == 0:
                    dico = {"label" : "%s %s" % (dicoLabel[int(month)], year),
                            "tri"   : "%s/%s" % (year, month),
                            "year"  : year,
                            "month" : month,
                            "nb"    : 1}
                elif monthP != 0 and month != monthP:
                    listeRetour.append(dico)
                    dico = {"label" : "%s %s" % (dicoLabel[int(month)], year),
                            "tri"   : "%s/%s" % (year, month),
                            "year"  : year,
                            "month" : month,
                            "nb"    : 1}
                else:
                    dico["nb"] = dico["nb"] + 1
                monthP = month
                i = i + 1
            listeRetour.append(dico)
            dicoRetour["detail"] = listeRetour
            dicoRetour["graph"] = self.genererGraphConnexionInd(listeRetour)
            return dicoRetour
        return None

    def genererGraphConnexionInd(self, listeMois):
        dicoLabel = {1  : u"Janvier",
                     2  : u"Février",
                     3  : u"Mars",
                     4  : u"Avril",
                     5  : u"Mai",
                     6  : u"Juin",
                     7  : u"Juillet",
                     8  : u"Août",
                     9  : u"Septembre",
                     10 : u"Octobre",
                     11 : u"Novembre",
                     12 : u"Décembre"}

        graph = ['<script type="text/javascript">']
        graph.append("var chartData = [")

        monthP = 0
        for mois in listeMois:
            month = int(mois["month"])
            if monthP == 0:
                graph.append("{")
                graph.append('  "month": "%s",' % mois["label"])
                graph.append('  "visits": %s' % mois["nb"])
                graph.append('},')
                monthP = int(mois["month"])
            elif (month - monthP) != 1:
                if monthP == 12 and month != 1:
                    monthP = 0
                for i in range((month - monthP - 1)):
                    graph.append("{")
                    graph.append('  "month": "%s %s",' % (dicoLabel[monthP + 1], mois["year"]))
                    graph.append('  "visits": 0')
                    graph.append('},')
                    monthP = monthP + 1
                graph.append("{")
                graph.append('  "month": "%s",' % mois["label"])
                graph.append('  "visits": %s' % mois["nb"])
                graph.append('},')
                monthP = int(mois["month"])
            else:
                graph.append("{")
                graph.append('  "month": "%s",' % mois["label"])
                graph.append('  "visits": %s' % mois["nb"])
                graph.append('},')
                monthP = int(mois["month"])
        graph.append('];')

        graph.append('''
        AmCharts.ready(function() {
            var chart = new AmCharts.AmSerialChart();
            chart.dataProvider = chartData;
            chart.categoryField = "month";

            var categoryAxis = chart.categoryAxis;
            categoryAxis.labelRotation = 65;

            var graph = new AmCharts.AmGraph();
            graph.valueField = "visits";
            graph.type = "column";
            graph.fillAlphas = 0.8;
            chart.addGraph(graph);

            chart.write("chartdiv");
        });
        </script>''')
        return "\n".join(graph)

    def getConsultationCoursByDate(self, COD_ELP, TYP_ELP, SESAME_ETU, month, year):
        session = self.getSession()

        if SESAME_ETU == "tous":
            SESAME_ETU = None

        portal = getUtility(IPloneSiteRoot)
        portal_catalog = getToolByName(portal, "portal_catalog")

        listeAcces = ["%s*-*%s" % (TYP_ELP, COD_ELP)]
        enfants_elp = self.getEnfantELP(COD_ELP)
        for elp in enfants_elp:
            if elp["TYP_ELP"] == "groupe":
                listeAcces.append("%s*-*%s" % (elp["TYP_ELP"], elp["COD_GPE"]))
            else:
                listeAcces.append("%s*-*%s" % (elp["TYP_ELP"], elp["COD_ELP"]))

        query = {'query': listeAcces, 'operator': 'or'}
        rechercheCours = list(portal_catalog.searchResults(portal_type="JalonCours", getRechercheAcces=query))

        listeCours = []
        dicoCours = {}
        if rechercheCours:
            for cours in rechercheCours:
                dicoCours[cours.getId] = {"id"      : cours.getId,
                                          "Title"   : cours.Title,
                                          "Creator" : cours.Creator,
                                          "NbPrec"  : 0,
                                          "NbCour"  : 0,
                                          "NbAnnee" : 0}

        if not month or month == '0':
            month = DateTime().month()
        monthPrec = month - 1
        if not year or year == '0':
            year = DateTime().year()

        if monthPrec == 0:
            monthPrec = "12"
            yearPrec = year - 1
        else:
            yearPrec = year

        if int(month) < 10:
            month = "0%s" % month
        year = str(DateTime().year())

        if int(monthPrec) < 10:
            monthPrec = "0%s" % str(monthPrec)
        else:
            monthPrec = str(monthPrec)
        yearPrec = str(yearPrec)

        consultationCoursPrec = jalonsqlite.getConsultationCoursByMonth(session, monthPrec, yearPrec, dicoCours.keys(), SESAME_ETU)
        for ligne in consultationCoursPrec.all():
            try:
                dicoCours[ligne[0]]["NbPrec"] = ligne[1]
            except:
                pass

        consultationCours = jalonsqlite.getConsultationCoursByMonth(session, month, year, dicoCours.keys(), SESAME_ETU)
        for ligne in consultationCours.all():
            try:
                dicoCours[ligne[0]]["NbCour"] = ligne[1]
            except:
                pass

        consultationCours = jalonsqlite.getConsultationCoursByYear(session, year, dicoCours.keys(), SESAME_ETU)
        for ligne in consultationCours.all():
            try:
                dicoCours[ligne[0]]["NbAnnee"] = ligne[1]
                if not dicoCours[ligne[0]] in listeCours:
                    listeCours.append(dicoCours[ligne[0]])
            except:
                pass

        listeCours.sort(lambda x,y: cmp(x["Title"], y["Title"]))
        return listeCours

    def getMinMaxYearByELP(self, COD_ELP):
        session = self.getSession()
        return jalonsqlite.getMinMaxYearByELP(session, COD_ELP)

    #-----------------------#
    # Fonctions utilitaires #
    #-----------------------#
    def getTypeAttachementELP(self, type="tous"):
        dico = {"etape":  [{"type":    "ue",
                            "libelle": _(u"Unité d'enseignement")},
                           {"type":    "uel",
                            "libelle": _(u"Unité d'enseignement libre")},
                           {"type":    "groupe",
                            "libelle": _(u"Groupe")}],
                "ue":     [{"type":    "etape",
                            "libelle": _(u"Diplôme")},
                           {"type":    "groupe",
                            "libelle": _(u"Groupe")}],
                "uel":    [{"type":    "etape",
                            "libelle": _(u"Diplôme")},
                           {"type":    "groupe",
                            "libelle": _(u"Groupe")}],
                "groupe": [{"type":    "etape",
                            "libelle": _(u"Diplôme")},
                           {"type":    "ue",
                            "libelle": _(u"Unité d'enseignement")},
                           {"type":    "uel",
                            "libelle": _(u"Unité d'enseignement libre")}],
                "tous":  [{"type":    "etape",
                            "libelle": _(u"Diplôme")},
                           {"type":    "ue",
                            "libelle": _(u"Unité d'enseignement")},
                           {"type":    "uel",
                            "libelle": _(u"Unité d'enseignement libre")},
                           {"type":    "groupe",
                            "libelle": _(u"Groupe")}]}
        return dico[type]

    def isBDD(self):
        if not self._urlConnexion:
            return 0
        liste_export = os.listdir(self._urlConnexion)
        if not "jalonBDD.db" in liste_export:
            return 0
        return 1

    def envoyerMail(self, idSuppression, idDemande):
        form = {}
        form["objet"] = "Demande de suppression d'un utilisateur"
        utilisateurSuppr = self.getIndividuLITE(idSuppression)
        utilisateurDem = self.getIndividuLITE(idDemande)
        message = [u"Bonjour"]
        message.append(u"")
        message.append(u"L'utilisateur %s %s (identifiant : %s , role :%s) demande la suppression de l'utilisateur :" % (utilisateurDem["LIB_NOM_PAT_IND"].decode("utf-8"), utilisateurDem["LIB_PR1_IND"].decode("utf-8"), utilisateurDem["SESAME_ETU"], utilisateurDem["TYPE_IND"]))
        message.append(u"")
        message.append(u"%s %s (identifiant : %s , role :%s)" % (utilisateurSuppr["LIB_NOM_PAT_IND"], utilisateurSuppr["LIB_PR1_IND"], utilisateurSuppr["SESAME_ETU"], utilisateurSuppr["TYPE_IND"]))
        message.append(u"")
        message.append(u"")
        message.append(u"Cordialement,")
        message.append(u"%s" % self.portal_url.getPortalObject().Title())
        form["message"] = "\n".join(message).encode("utf-8")
        jalon_utils.envoyerMail(form)

    def traductions_fil(self, key):
        textes = {"bdd":          _(u"Offre de formation"),
                  "configsite":   _(u"Configuration du site"),
                  "mon_espace":   _(u"Mon Espace"),
                  "gestion_util": _(u"Gestion des Utilisateurs")}
        if key in textes:
            return textes[key]
        else:
            return key

    def test(self, condition, valeurVrai, valeurFaux):
        return valeurVrai if condition else valeurFaux

    def encodeUTF8(self, itemAEncoder):
        return [str(encoder).encode("utf-8") for encoder in itemAEncoder]

    def alterBDD(self):
        session = self.getSession()
        session.execute("ALTER TABLE individu_lite ADD COLUMN STATUS_IND TEXT")
        #session.execute("DROP TABLE connexion")
        session.execute('''CREATE TABLE connexion
                        (NUM_CONN INTEGER PRIMARY KEY AUTOINCREMENT, SESAME_ETU TEXT, DATE_CONN TEXT, FOREIGN KEY(SESAME_ETU) REFERENCES individu_lite(SESAME_ETU))''')
        session.commit()

    def alterTableContenu(self, param):
        session = self.getSession()
        session.execute("update individu_lite set SESAME_ETU='%s' where SESAME_ETU=='%s'" % (param["NEW_SESAME_ETU"], param["SESAME_ETU"]))
        session.commit()

    def updateNbIns(self, COD_ELP, nb):
        session = self.getSession()
        session.execute("update element_pedagogi_lite set ETU_ELP=%s where COD_ELP=='%s'" % (str(nb), COD_ELP))
        session.flush()
        session.commit()

    def addTableConsultationCours(self):
        session = self.getSession()
        session.execute('''CREATE TABLE consultationCours
                        (NUM_CONN INTEGER PRIMARY KEY AUTOINCREMENT, SESAME_ETU TEXT, DATE_CONS TEXT, ID_COURS TEXT, TYPE_CONS TEXT, ID_CONS TEXT, FOREIGN KEY(SESAME_ETU) REFERENCES individu_lite(SESAME_ETU))''')
        session.commit()

    def insererConsultation(self, param):
        if self._activerStockageConsultation:
            session = self.getSession()
            if self._typeBDD == "sqlite":
                return jalonsqlite.insererConsultation(session, param)

    def getConsultation(self):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getConsultation(session)

    def convertirResultatBDD(self, resultat):
        conversion = []
        if resultat:
            for ligne in resultat:
                conversion.append(dict(zip(ligne.keys(), ligne)))
        return conversion

    def execRequeteBDD(self, requete, maj=False):
        session = self.getSession()
        requete = session.execute(requete)
        if maj:
            session.commit()
            return "MAJ OK"
        return self.convertirResultatBDD(requete)
