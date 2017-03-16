# -*- coding: utf-8 -*-
from zope.interface import implements
from OFS.SimpleItem import SimpleItem

from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot

from sqlite3 import dbapi2 as sqlite

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import aliased
from sqlalchemy.pool import NullPool

from interfaces import IJalonBDD
from jalon.bdd import contentMessageFactory as _
from jalon.content.content import jalon_utils

import tables
import jalonsqlite
import jalon_mysql

import os
import os.path
import sqlite3
import json

from dateutil import rrule
from datetime import datetime, timedelta
from DateTime import DateTime

# Messages de debug :
from logging import getLogger
LOG = getLogger('[JalonBDD]')
"""
# Log examples :
# LOG.info('info message')
"""


class JalonBDD(SimpleItem):
    """Classe Jalon BDD."""

    implements(IJalonBDD)
    _urlConnexion = "/home/zope/sites/bdd_jalon/"
    _typeBDD = "sqlite"
    _typeBDDActif = ""
    Session = sessionmaker()

    _activer_stockage_connexion = 1
    _activer_stockage_consultation = 1

    _use_mysql = 1
    _host_mysql = "127.0.0.1"
    _user_mysql = "zope"
    _password_mysql = "zope"
    _port_mysql = 3306
    _db_name_mysql = "jalon"
    _session_mysql_open = False
    SessionMySQL = sessionmaker()

    _public_bdd = ["Etudiant", "Lecteur"]

    def __init__(self, *args, **kwargs):
        super(JalonBDD, self).__init__(*args, **kwargs)

    # -------------------------------------#
    #  Gestion des variables du connecteur #
    # -------------------------------------#
    def getBDDProperty(self, key):
        return getattr(self, "_%s" % key)

    def getUrlConnexion(self):
        return self._urlConnexion

    def setUrlConnexion(self, urlConnexion):
        self._urlConnexion = urlConnexion

    def getTypeBDD(self):
        return self._typeBDD

    def setTypeBDD(self, typeBDD):
        self._typeBDD = typeBDD

    def getVariablesBDD(self):
        return {"typeBDD":                     self._typeBDD,
                "urlConnexion":                self._urlConnexion,
                "activerStockageConnexion":    self._activer_stockage_connexion,
                "activerStockageConsultation": self._activer_stockage_consultation,
                "useSaveMySQL":                self._use_mysql,
                "hostMySQL":                   self._host_mysql,
                "portMySQL":                   self._port_mysql,
                "dbNameMySQL":                 self._db_name_mysql,
                "userMySQL":                   self._user_mysql,
                "passwordMySQL":               self._password_mysql}

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
            if "jalonBDD.db" not in liste_export:
                self.creerBDD(variablesBDD)
                retour = 3
        for key in variablesBDD.keys():
            val = variablesBDD[key]
            if key.startswith("activer_") or key.startswith("use_"):
                val = int(val)
            setattr(self, "_%s" % key, val)
        self._typeBDDActif = ""
        return retour

    def creerBDD(self, variablesBDD=None):
        if variablesBDD:
            chemin = variablesBDD["urlConnexion"]
        else:
            chemin = self._urlConnexion

        # LOG.info("-------------- création et connexion jalonBDD.db --------------")
        conn = sqlite3.connect('%s/jalonBDD.db' % chemin)
        c = conn.cursor()

        # Creation tables
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
            self.creerTablesMySQL()

    def creerTablesMySQL(self):
            connexion = "mysql+mysqldb://%s:%s@%s:%s/%s" % (self._user_mysql, self._password_mysql, self._host_mysql, self._port_mysql, self._db_name_mysql)
            engine = create_engine(connexion, echo=True)
            #tables.IndividuMySQL.__table__.create(bind=engine)
            #tables.ConnexionINDMySQL.__table__.create(bind=engine)
            #tables.ConsultationCoursMySQL.__table__.create(bind=engine)
            tables.PeersEvaluationMySQL.__table__.create(bind=engine)
            tables.PeersEvaluationNoteMySQL.__table__.create(bind=engine)
            tables.PeersSelfEvaluationMySQL.__table__.create(bind=engine)
            tables.PeersSelfEvaluationNoteMySQL.__table__.create(bind=engine)
            tables.PeersAverageMySQL.__table__.create(bind=engine)
            tables.PeersEvaluationAverageMySQL.__table__.create(bind=engine)

    # ---------------------------- #
    #  Utilitaire base de données  #
    # ---------------------------- #
    def getSession(self):
        # LOG.info("----------- getSession -----------")
        try:
            self.Session().get_bind()
            # LOG.info(self.Session())
        except:
            # LOG.info("except Session")
            self._typeBDDActif = None
        if (not self._typeBDDActif) or (self._typeBDDActif != self._typeBDD):
            # LOG.info("initialiser session")
            try:
                self.Session().close()
            except:
                pass
            if self._typeBDD == "sqlite":
                # LOG.info("sqlite:///%s/jalonBDD.db" % self._urlConnexion)
                engine = create_engine("sqlite:///%s/jalonBDD.db" % self._urlConnexion, module=sqlite, echo=False, poolclass=NullPool)
            if self._typeBDD == "apogee":
                engine = create_engine("apogee:///%s" % self._urlConnexion, echo=False, poolclass=NullPool)
            # LOG.info("ouverture connexion")
            self.Session.configure(bind=engine)
            self._typeBDDActif = self._typeBDD
        return self.Session()

    def getSessionMySQL(self):
        # LOG.info("----------- getSessionMySQL -----------")
        try:
            self.SessionMySQL().get_bind()
            # LOG.info(self.Session())
        except:
            # LOG.info("except Session")
            self._session_mysql_open = False
        if not self._session_mysql_open:
            # LOG.info("initialiser session")
            try:
                self.SessionMySQL().close()
            except:
                pass
            connexion = "mysql+mysqldb://%s:%s@%s:%s/%s" % (self._user_mysql, self._password_mysql, self._host_mysql, self._port_mysql, self._db_name_mysql)
            engine = create_engine(connexion, echo=False, poolclass=NullPool)
            # LOG.info("ouverture connexion")
            self.SessionMySQL.configure(bind=engine)
            self._session_mysql_open = True
        return self.SessionMySQL()

    # ------------------------------------- #
    #  Interrogation de la base de données  #
    # ------------------------------------- #
    def getIndividuLITE(self, sesame):
        # LOG.info("----- getIndividuLITE -----")
        session = self.getSession()
        if self._typeBDD == "sqlite":
            result = jalonsqlite.getIndividuLITE(session, sesame)
            if result:
                # LOG.info("***** result : %s" % result)
                return result[0]
            else:
                # LOG.info("***** result : None")
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
        # if self._typeBDD == "sqlite":
        infosElp = jalonsqlite.getInfosELP(session, COD_ELP)
        infosElp = self.ajouterResponsable([infosElp])[0]
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

    def getELPProperties(self, COD_ELP):
        session = self.getSession()
        return jalonsqlite.getELPProperties(session, COD_ELP)

    def getELPData(self, COD_ELP):
        session = self.getSession()
        return jalonsqlite.getELPData(session, COD_ELP)

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

    def searchELP(self, search_terms_list, search_elp_type=None):
        session = self.getSession()
        return jalonsqlite.searchELP(session, search_terms_list, search_elp_type)

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

    # ------------------------------------ #
    #  Modification de la base de données  #
    # ------------------------------------ #
    def addConnexionUtilisateur(self, SESAME_ETU):
        # LOG.info('----- addConnexionUtilisateur -----')
        if self._activer_stockage_connexion:
            if self._use_mysql:
                # LOG.info('Appel MySQL')
                session = self.getSessionMySQL()
                # LOG.info("datetime : %s" % str(datetime.now()))
                jalon_mysql.addConnexionIND(session, SESAME_ETU, datetime.now())
            else:
                # LOG.info('Appel SQLITE')
                session = self.getSession()
                jalonsqlite.addConnexionIND(session, SESAME_ETU, str(DateTime()))

    def insererConsultation(self, SESAME_ETU, ID_COURS, TYPE_CONS, ID_CONS, PUBLIC_CONS):
        # LOG.info('----- insererConsultation -----')
        if self._activer_stockage_consultation:
            if self._use_mysql:
                # LOG.info('Appel MySQL')
                session = self.getSessionMySQL()
                jalon_mysql.addConsultationIND(session, SESAME_ETU, datetime.now(), ID_COURS, TYPE_CONS, ID_CONS, PUBLIC_CONS)
            else:
                # LOG.info('Appel SQLITE')
                session = self.getSession()
                jalonsqlite.insererConsultation(session, SESAME_ETU, str(DateTime()), ID_COURS, TYPE_CONS, ID_CONS, PUBLIC_CONS)

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

    def creerUtilisateur(self, param):
        # LOG.info("----- creerUtilisateur -----")
        retour = 0
        session = self.getSession()
        if self._typeBDD == "sqlite":
            # LOG.info("SQLITE")
            retour = jalonsqlite.creerUtilisateur(session, param)

        if self._use_mysql:
            session_mysql = self.getSessionMySQL()
            jalon_mysql.addIndividu(session_mysql, param)

        if retour:
            sesame = param["SESAME_ETU"].replace(" ", "")
            portal_membership = getToolByName(self, 'portal_membership')
            portal_registration = getToolByName(self, 'portal_registration')
            if not "PASSWORD" in param:
                param["PASSWORD"] = portal_registration.generatePassword()
            roles = (param["TYPE_IND"], "Member",)
            if param["TYPE_IND"] == "Secretaire":
                roles = ("Personnel", "Secretaire", "Member",)
            portal_membership.addMember(sesame, param["PASSWORD"], roles, "")
            # try:
            #    portal_registration.registeredNotify(sesame)
            # except:
            #    pass

    def creerUtilisateurTest(self, param, use_mysql=False):
        if use_mysql:
            session = self.getSessionMySQL()
            jalon_mysql.addIndividu(session, param)
        else:
            session = self.getSession()
            jalonsqlite.creerUtilisateur(session, param)

    def creerUtilisateurMySQL(self, param):
        session_mysql = self.getSessionMySQL()
        jalon_mysql.addIndividu(session_mysql, param)

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
            infos = jalon_utils.getIndividu(authMember.getId(), "dict")
            message = 'Bonjour\n\nVotre mot de passe a été changé par "%s". Pour vous connecter à %s (%s) vous devez utiliser :\n\nNom d\'utilisateur : %s\nMot de passe : %s\n\nVous pouvez changer ce mot de passe en cliquant sur le lien suivant : %s/mail_password_form?userid=%s\n\nCordialement,\nL\'équipe %s.' % (infos["fullname"],
                portal.Title(),
                portal.absolute_url(), param["SESAME_ETU"].encode("UTF-8"),
                param["password"].encode("UTF-8"), portal.absolute_url(),
                param["SESAME_ETU"].encode("UTF-8"), portal.Title())
            jalon_utils.envoyerMail({"a":       param["EMAIL_ETU"],
                                     "objet":   "Nouveau mot de passe",
                                     "message": message})

    def attacherELP(self, param):
        session = self.getSession()
        return jalonsqlite.attacherELP(session, param)

    def sattacherAELP(self, param):
        session = self.getSession()
        return jalonsqlite.sattacherAELP(session, param)

    def detacherToutesELP(self, param):
        session = self.getSession()
        return jalonsqlite.detacherToutesELP(session, param)

    def seDetacherToutesELP(self, param):
        session = self.getSession()
        return jalonsqlite.seDetacherToutesELP(session, param)

    def detacherELP(self, param):
        session = self.getSession()
        return jalonsqlite.detacherELP(session, param)

    def seDetacherDeELP(self, param):
        session = self.getSession()
        return jalonsqlite.seDetacherDeELP(session, param)

    def inscrireEnsResp(self, param):
        session = self.getSession()
        return jalonsqlite.inscrireEnsResp(session, param)

    def inscrireEnseignant(self, param):
        session = self.getSession()
        return jalonsqlite.inscrireEnseignant(session, param)

    def inscrireEtudiant(self, param):
        session = self.getSession()
        return jalonsqlite.inscrireEtudiant(session, param)

    def inscrireINDELP(self, SESAME_ETU, TYPE_ELP, LISTE_ELP):
        session = self.getSession()
        return jalonsqlite.inscrireINDELP(session, SESAME_ETU, TYPE_ELP, LISTE_ELP)

    def desinscrireINDELP(self, SESAME_ETU, TYPE_ELP):
        session = self.getSession()
        return jalonsqlite.desinscrireINDELP(session, SESAME_ETU, TYPE_ELP)

    def desinscrireEnseignant(self, param):
        session = self.getSession()
        return jalonsqlite.desinscrireEnseignant(session, param)

    def desinscrireEtudiant(self, param):
        session = self.getSession()
        return jalonsqlite.desinscrireEtudiant(session, param)

    def supprUtilisateur(self, param):
        session = self.getSession()
        return jalonsqlite.supprUtilisateur(session, param)

    def bloquerIndividu(self, param):
        session = self.getSession()
        return jalonsqlite.bloquerIND(session, param)

    def activerIndividu(self, param):
        session = self.getSession()
        return jalonsqlite.activerIND(session, param)

    def ajouterActuCours(self, param):
        session = self.getSession()
        return jalonsqlite.ajouterActuCours(session, param)

    # ----------------------- #
    #  Fonctions Statistiques #
    # ----------------------- #
    def updateTableConnexion(self):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.updateTableConnexion(session)

    def getIndByElp(self, COD_ELP):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getIndByElp(session, COD_ELP)

    def getConnexionCouranteByELP(self, COD_ELP):
        #month = DateTime().month()
        year = DateTime().year()
        return self.displayConnexion(COD_ELP, year)

    def displayConnexion(self, COD_ELP, year):
        listeInds = self.getIndByElp(COD_ELP)
        if not listeInds:
            return {"mois":  "Aucun inscrit dans cet élément pédagigique",
                    "annee": "Aucun inscrit dans cet élément pédagigique"}
        if self._use_mysql:
            session = self.getSessionMySQL()
            #coMois = jalon_mysql.getConnexionELPByMonth(session, COD_ELP, month, year, listeInds)
            coAnnee = jalon_mysql.getConnexionELPByYear(session, COD_ELP, year, listeInds)
        else:
            if int(month) < 10:
                month = "0%s" % month
            session = self.getSession()
            #coMois = jalonsqlite.getConnexionELPByMonth(session, COD_ELP, month, str(year), listeInds)
            coAnnee = jalonsqlite.getConnexionELPByYear(session, COD_ELP, str(year), listeInds)

        detailMois = ({"label": "Janvier",   "nb": 0},
                      {"label": "Février",   "nb": 0},
                      {"label": "Mars",      "nb": 0},
                      {"label": "Avril",     "nb": 0},
                      {"label": "Mai",       "nb": 0},
                      {"label": "Juin",      "nb": 0},
                      {"label": "Juillet",   "nb": 0},
                      {"label": "Août",      "nb": 0},
                      {"label": "Septembre", "nb": 0},
                      {"label": "Octobre",   "nb": 0},
                      {"label": "Novembre",  "nb": 0},
                      {"label": "Décembre",  "nb": 0})
        for connexion in coAnnee:
            month = DateTime(connexion[1]).month()
            detailMois[month - 1]["nb"] = detailMois[month - 1]["nb"] + 1

        return {"etu":        len(listeInds),
                "annee":      coAnnee.count(),
                "detailMois": detailMois,
                "graph":      self.genererGraphConnexionCourante(detailMois)}

    def getConnexionELPByMonth(self, COD_ELP, month=None, year="%", listeInds=None):
        session = self.getSession()
        if not listeInds:
            ICE = aliased(tables.IndContratElpSQLITE)
            requete = session.query(ICE.SESAME_ETU).filter(ICE.COD_ELP == COD_ELP).all()
            listeInds = [x[0] for x in requete]
        if self._use_mysql:
            return jalon_mysql.getConnexionELPByMonth(session, COD_ELP, month, year, listeInds)
        else:
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
        if not month or month == '0':
            month = DateTime().month()

        if not year or year == '0':
            year = DateTime().year()

        monthPrec = month - 1
        if monthPrec == 0:
            monthPrec = 12
            yearPrec = year - 1
        else:
            yearPrec = year

        session = self.getSession()
        listeInds = self.getIndAndNameByElp(COD_ELP)
        if not listeInds:
            return {"etu": []}
        listeSesames = self.getIndByElp(COD_ELP)

        dicoMoisInd = {}
        dicoMoisPrecInd = {}
        dicoAnneeInd = {}
        if self._use_mysql:
            session = self.getSessionMySQL()
            coMois = jalon_mysql.getConnexionELPByMonthByIND(session, COD_ELP, month, year, listeSesames)
            for ligne in coMois:
                dicoMoisInd[ligne[0]] = ligne[1]

            coMoisPrec = jalon_mysql.getConnexionELPByMonthByIND(session, COD_ELP, monthPrec, yearPrec, listeSesames)
            for ligne in coMoisPrec:
                dicoMoisPrecInd[ligne[0]] = ligne[1]

            coAnnee = jalon_mysql.getConnexionELPByYearByIND(session, COD_ELP, year, listeSesames)
            for ligne in coAnnee:
                dicoAnneeInd[ligne[0]] = ligne[1]
        else:
            year = str(year)
            month = str(month)
            if int(month) < 10:
                month = "0%s" % str(month)
            monthPrec = str(monthPrec)
            if int(monthPrec) < 10:
                monthPrec = "0%s" % str(monthPrec)

            coMois = jalonsqlite.getConnexionELPByMonthByIND(session, COD_ELP, month, year, listeSesames)
            for ligne in coMois:
                dicoMoisInd[ligne[0]] = ligne[1]

            coMoisPrec = jalonsqlite.getConnexionELPByMonthByIND(session, COD_ELP, monthPrec, str(yearPrec), listeSesames)
            for ligne in coMoisPrec:
                dicoMoisPrecInd[ligne[0]] = ligne[1]

            coAnnee = jalonsqlite.getConnexionELPByYearByIND(session, COD_ELP, year, listeSesames)
            for ligne in coAnnee:
                dicoAnneeInd[ligne[0]] = ligne[1]

        return {"etu":      listeInds,
                "mois":     dicoMoisInd,
                "moisPrec": dicoMoisPrecInd,
                "annee":    dicoAnneeInd}

    def getConnexionByIND(self, SESAME_ETU):
        dicoRetour = {}
        listeRetour = []

        dicoLabel = {1:  u"Janvier",
                     2:  u"Février",
                     3:  u"Mars",
                     4:  u"Avril",
                     5:  u"Mai",
                     6:  u"Juin",
                     7:  u"Juillet",
                     8:  u"Août",
                     9:  u"Septembre",
                     10: u"Octobre",
                     11: u"Novembre",
                     12: u"Décembre"}

        session = self.getSession()
        if self._use_mysql:
            session = self.getSessionMySQL()
            listeConnexion = jalon_mysql.getConnexionByIND(session, SESAME_ETU)
        else:
            listeConnexion = jalonsqlite.getConnexionByIND(session, SESAME_ETU)

        if listeConnexion:
            dicoRetour["first"] = jalon_utils.getLocaleDate(listeConnexion.first()[0], "%d/%m/%Y à %Hh%M")
            dicoRetour["last"] = jalon_utils.getLocaleDate(listeConnexion.all()[-1][0], "%d/%m/%Y à %Hh%M")
            dicoRetour["total"] = listeConnexion.count()

            i = 0
            monthP = 0
            for connexion in listeConnexion:
                try:
                    year = connexion[0].year
                except:
                    year = connexion[0].split("/")[0]
                try:
                    month = connexion[0].month
                except:
                    month = connexion[0].split("/")[1]
                if i == 0:
                    dico = {"label": "%s %s" % (dicoLabel[int(month)], year),
                            "tri":   "%s/%s" % (year, month),
                            "year":  year,
                            "month": month,
                            "nb":    1}
                elif monthP != 0 and month != monthP:
                    listeRetour.append(dico)
                    dico = {"label": "%s %s" % (dicoLabel[int(month)], year),
                            "tri":   "%s/%s" % (year, month),
                            "year":  year,
                            "month": month,
                            "nb":    1}
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
        dicoLabel = {1:  u"Janvier",
                     2:  u"Février",
                     3:  u"Mars",
                     4:  u"Avril",
                     5:  u"Mai",
                     6:  u"Juin",
                     7:  u"Juillet",
                     8:  u"Août",
                     9:  u"Septembre",
                     10: u"Octobre",
                     11: u"Novembre",
                     12: u"Décembre"}

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
                dicoCours[cours.getId] = {"id":      cours.getId,
                                          "Title":   cours.Title,
                                          "Creator": cours.Creator,
                                          "NbPrec":  0,
                                          "NbCour":  0,
                                          "NbAnnee": 0}

        if not month or month == '0':
            month = DateTime().month()
        monthPrec = month - 1
        if not year or year == '0':
            year = DateTime().year()

        if monthPrec == 0:
            monthPrec = 12
            yearPrec = year - 1
        else:
            yearPrec = year

        if self._use_mysql:
            session = self.getSessionMySQL()
            consultationCoursPrec = jalon_mysql.getConsultationCoursByMonth(session, monthPrec, yearPrec, dicoCours.keys(), SESAME_ETU)
            for ligne in consultationCoursPrec.all():
                try:
                    dicoCours[ligne[0]]["NbPrec"] = ligne[1]
                except:
                    pass

            consultationCours = jalon_mysql.getConsultationCoursByMonth(session, month, year, dicoCours.keys(), SESAME_ETU)
            for ligne in consultationCours.all():
                try:
                    dicoCours[ligne[0]]["NbCour"] = ligne[1]
                except:
                    pass

            consultationCours = jalon_mysql.getConsultationCoursByYear(session, year, dicoCours.keys(), SESAME_ETU)
            for ligne in consultationCours.all():
                try:
                    dicoCours[ligne[0]]["NbAnnee"] = ligne[1]
                    if not dicoCours[ligne[0]] in listeCours:
                        listeCours.append(dicoCours[ligne[0]])
                except:
                    pass
        else:
            if int(month) < 10:
                month = "0%s" % month

            if int(monthPrec) < 10:
                monthPrec = "0%s" % str(monthPrec)
            else:
                monthPrec = str(monthPrec)
            yearPrec = str(yearPrec)

            session = self.getSession()
            consultationCoursPrec = jalonsqlite.getConsultationCoursByMonth(session, monthPrec, yearPrec, dicoCours.keys(), SESAME_ETU)
            for ligne in consultationCoursPrec.all():
                try:
                    dicoCours[ligne[0]]["NbPrec"] = ligne[1]
                except:
                    pass

            consultationCours = jalonsqlite.getConsultationCoursByMonth(session, month, str(year), dicoCours.keys(), SESAME_ETU)
            for ligne in consultationCours.all():
                try:
                    dicoCours[ligne[0]]["NbCour"] = ligne[1]
                except:
                    pass

            consultationCours = jalonsqlite.getConsultationCoursByYear(session, str(year), dicoCours.keys(), SESAME_ETU)
            for ligne in consultationCours.all():
                try:
                    dicoCours[ligne[0]]["NbAnnee"] = ligne[1]
                    if not dicoCours[ligne[0]] in listeCours:
                        listeCours.append(dicoCours[ligne[0]])
                except:
                    pass

        listeCours.sort(lambda x, y: cmp(x["Title"], y["Title"]))
        return listeCours

    def getConsultationByCoursByDate(self, ID_COURS, month=None, year=None):
        # LOG.info("----- getConsultationByCoursByDate -----")
        consultation_dict = {}
        for public in self._public_bdd:
            consultation_dict[public] = {"public":               public,
                                         "nb_cons_month_before": 0,
                                         "nb_cons_month":        0,
                                         "icon":                 "",
                                         "nb_cons_year":         0}
        consultations_list = []

        if not month or month == '0':
            month = DateTime().month()
        monthPrec = month - 1
        if not year or year == '0':
            year = DateTime().year()

        if monthPrec == 0:
            monthPrec = 12
            yearPrec = year - 1
        else:
            yearPrec = year

        if self._use_mysql:
            session = self.getSessionMySQL()

            consultationCours = jalon_mysql.getConsultationByCoursByUniversityYear(session, ID_COURS, year)
            # LOG.info("Consultation Année Courant")
            for ligne in consultationCours.all():
                # LOG.info(ligne)
                try:
                    consultation_dict[ligne[0]]["nb_cons_year"] = ligne[1]
                    if not consultation_dict[ligne[0]] in consultations_list:
                        consultations_list.append(consultation_dict[ligne[0]])
                except:
                    pass
            # LOG.info(consultation_dict)

            consultationCoursPrec = jalon_mysql.getConsultationByCoursByMonth(session, ID_COURS, monthPrec, yearPrec)
            # LOG.info("Consultation Mois Précédent")
            for ligne in consultationCoursPrec.all():
                # LOG.info(ligne)
                try:
                    consultation_dict[ligne[0]]["nb_cons_month_before"] = ligne[1]
                except:
                    # consultation_dict[ligne[0]]["nb_cons_month_before"] = 0
                    pass

            consultationCours = jalon_mysql.getConsultationByCoursByMonth(session, ID_COURS, month, year)
            # LOG.info("Consultation Mois Courant")
            for ligne in consultationCours.all():
                # LOG.info(ligne)
                try:
                    consultation_dict[ligne[0]]["nb_cons_month"] = ligne[1]
                except:
                    # consultation_dict[ligne[0]]["nb_cons_month"] = 0
                    pass
        else:
            if int(month) < 10:
                month = "0%s" % month

            if int(monthPrec) < 10:
                monthPrec = "0%s" % str(monthPrec)
            else:
                monthPrec = str(monthPrec)
            yearPrec = str(yearPrec)

            session = self.getSession()
            consultationCoursPrec = jalonsqlite.getConsultationByCoursByMonth(session, ID_COURS, monthPrec, yearPrec)
            for ligne in consultationCoursPrec.all():
                try:
                    consultation["nb_cons_month_before"] = ligne[0]
                except:
                    pass

            consultationCours = jalonsqlite.getConsultationByCoursByMonth(session, ID_COURS, month, str(year))
            for ligne in consultationCours.all():
                try:
                    consultation["nb_cons_month"] = ligne[0]
                except:
                    pass

            consultationCours = jalonsqlite.getConsultationByCoursByYear(session, ID_COURS, str(year))
            for ligne in consultationCours.all():
                try:
                    consultation["nb_cons_year"] = ligne[0]
                except:
                    pass

        # LOG.info(consultations_list)
        for consultation in consultations_list:
            consultation["icon"] = "fa fa-arrow-down no-pad warning" if consultation["nb_cons_month"] < consultation["nb_cons_month_before"] else "fa fa-arrow-up no-pad success"
            if consultation["nb_cons_month"] == consultation["nb_cons_month_before"]:
                consultation["icon"] = "fa fa-arrow-right no-pad"
        return consultations_list

    def getConsultationByCoursByUniversityYearByDate(self, ID_COURS, DATE_CONS_YEAR, FILTER_DATE, PUBLIC_CONS):
        # LOG.info("----- getConsultationByCoursByUniversityYear -----")
        if not DATE_CONS_YEAR or DATE_CONS_YEAR == '0':
            DATE_CONS_YEAR = DateTime().year()
        session = self.getSessionMySQL()
        consultationCours = jalon_mysql.getConsultationByCoursByUniversityYearByDate(session, ID_COURS, DATE_CONS_YEAR, FILTER_DATE, PUBLIC_CONS)
        return consultationCours

    def getConsultationByCoursByYearForGraph(self, ID_COURS, year=None):
        # LOG.info("----- getConsultationByCoursByYearForGraph -----")
        if not year or year == '0':
            year = DateTime().year()
        session = self.getSessionMySQL()
        consultationCours = jalon_mysql.getConsultationByCoursByYearForGraph(session, ID_COURS, year)
        return consultationCours

    def getConsultationByCoursByUniversityYearForGraph(self, ID_COURS, year=None):
        # LOG.info("----- getConsultationByCoursByUniversityYearForGraph -----")
        if not year or year == '0':
            year = DateTime().year()
        session = self.getSessionMySQL()
        consultationCours = jalon_mysql.getConsultationByCoursByUniversityYearForGraph(session, ID_COURS, year)
        return consultationCours

    def getFrequentationByCoursByUniversityYearByDateForGraph(self, ID_COURS, PUBLIC_CONS, DATE_CONS_YEAR=None):
        # LOG.info("----- getFrequentationByCoursByUniversityYearByDateForGraph -----")
        if not DATE_CONS_YEAR or DATE_CONS_YEAR == '0':
            DATE_CONS_YEAR = DateTime().year()
        session = self.getSessionMySQL()
        consultationCours = jalon_mysql.getFrequentationByCoursByUniversityYearByDateForGraph(session, ID_COURS, PUBLIC_CONS, DATE_CONS_YEAR)
        return consultationCours

    def getConsultationElementsByCours(self, ID_COURS, month=None, year=None, elements_list=[], elements_dict={}):
        # LOG.info("----- getConsultationElementsByCours -----")
        consultation_dict = {}
        for element in elements_list:
            consultation_dict[element] = {"element_id":           element,
                                          "element_titre":        elements_dict.get(element, "Sans titre"),
                                          "nb_cons_month_before": 0,
                                          "nb_cons_month":        0,
                                          "nb_cons_year":         0,
                                          "nb_freq_month_before": 0,
                                          "nb_freq_month":        0,
                                          "nb_freq_year":         0,
                                          "icon":                 ""}
        consultations_list = []

        if not month or month == '0':
            month = DateTime().month()
        monthPrec = month - 1

        if not year or year == '0':
            year = DateTime().year()

        if monthPrec == 0:
            monthPrec = 12
            yearPrec = year - 1
        else:
            yearPrec = year

        session = self.getSessionMySQL()
        elements_consultation = jalon_mysql.getConsultationByElementsByCoursByUniversityYear(session, ID_COURS, year, elements_list)

        for ligne in elements_consultation.all():
            # LOG.info(ligne)
            # try:
            consultation_dict[ligne[0]]["nb_cons_year"] = ligne[1]
            consultation_dict[ligne[0]]["nb_freq_year"] = ligne[2]
            if not consultation_dict[ligne[0]] in consultations_list:
                consultations_list.append(consultation_dict[ligne[0]])
            # except:
            #    pass
        # LOG.info(consultation_dict)

        elements_consultation_month_before = jalon_mysql.getConsultationByElementsByCoursByMonth(session, ID_COURS, monthPrec, yearPrec, elements_list)
        for ligne in elements_consultation_month_before.all():
            # try:
            consultation_dict[ligne[0]]["nb_cons_month_before"] = ligne[1]
            consultation_dict[ligne[0]]["nb_freq_month_before"] = ligne[2]
            # except:
            #    consultation_dict[ligne[0]]["nb_cons_month_before"] = 0
            #    pass

        elements_consultation_month = jalon_mysql.getConsultationByElementsByCoursByMonth(session, ID_COURS, month, year, elements_list)
        for ligne in elements_consultation_month.all():
            # try:
            consultation_dict[ligne[0]]["nb_cons_month"] = ligne[1]
            consultation_dict[ligne[0]]["nb_freq_month"] = ligne[2]
            # except:
            #    consultation_dict[ligne[0]]["nb_cons_month"] = 0

        # LOG.info(consultations_list)
        for consultation in consultations_list:
            consultation["icon"] = "fa fa-arrow-down no-pad warning" if consultation["nb_freq_month"] < consultation["nb_freq_month_before"] else "fa fa-arrow-up no-pad success"
            if consultation["nb_freq_month"] == consultation["nb_freq_month_before"]:
                consultation["icon"] = "fa fa-arrow-right no-pad"
        return consultations_list

    def getConsultationByElementByCours(self, ID_COURS, ID_CONS, month=None, year=None):
        # LOG.info("----- getConsultationByElementByCours -----")
        consultation_dict = {}
        for public in self._public_bdd:
            consultation_dict[public] = {"public":               public,
                                         "nb_cons_month_before": 0,
                                         "nb_cons_month":        0,
                                         "icon":                 "",
                                         "nb_cons_year":         0}
        consultations_list = []

        if not month or month == '0':
            month = DateTime().month()
        monthPrec = month - 1
        if not year or year == '0':
            year = DateTime().year()

        if monthPrec == 0:
            monthPrec = 12
            yearPrec = year - 1
        else:
            yearPrec = year

        if self._use_mysql:
            session = self.getSessionMySQL()

            consultation_element = jalon_mysql.getConsultationByElementByCoursByUniversityYear(session, ID_COURS, ID_CONS, year)
            for ligne in consultation_element.all():
                # LOG.info(ligne)
                try:
                    consultation_dict[ligne[0]]["nb_cons_year"] = ligne[1]
                    if not consultation_dict[ligne[0]] in consultations_list:
                        consultations_list.append(consultation_dict[ligne[0]])
                except:
                    pass
            # LOG.info(consultation_dict)

            consultation_element = jalon_mysql.getConsultationByElementByCoursByMonth(session, ID_COURS, ID_CONS, monthPrec, yearPrec)
            for ligne in consultation_element.all():
                try:
                    consultation_dict[ligne[0]]["nb_cons_month_before"] = ligne[1]
                except:
                    pass

            consultation_element = jalon_mysql.getConsultationByElementByCoursByMonth(session, ID_COURS, ID_CONS, month, year)
            for ligne in consultation_element.all():
                try:
                    consultation_dict[ligne[0]]["nb_cons_month"] = ligne[1]
                except:
                    pass

        # LOG.info(consultations_list)
        for consultation in consultations_list:
            consultation["icon"] = "fa fa-arrow-down no-pad warning" if consultation["nb_cons_month"] < consultation["nb_cons_month_before"] else "fa fa-arrow-up no-pad success"
            if consultation["nb_cons_month"] == consultation["nb_cons_month_before"]:
                consultation["icon"] = "fa fa-arrow-right no-pad"
        return consultations_list

    def getConsultationByElementByCoursByYearForGraph(self, ID_COURS, ID_CONS, year=None):
        # LOG.info("----- getConsultationByElementByCoursByYearForGraph -----")
        if not year or year == '0':
            year = DateTime().year()
        session = self.getSessionMySQL()
        consultationCours = jalon_mysql.getConsultationByElementByCoursByYearForGraph(session, ID_COURS, ID_CONS, year)
        return consultationCours

    def getConsultationByElementByCoursByUniversityYearForGraph(self, ID_COURS, ID_CONS, year=None):
        # LOG.info("----- getConsultationByElementByCoursByUniversityYearForGraph -----")
        if not year or year == '0':
            year = DateTime().year()
        session = self.getSessionMySQL()
        consultationCours = jalon_mysql.getConsultationByElementByCoursByUniversityYearForGraph(session, ID_COURS, ID_CONS, year)
        return consultationCours

    def genererGraphIndicateurs(self, months_dict):
        # LOG.info("----- genererGraphIndicateurs -----")
        # LOG.info(months_dict)
        dicoLabel = {1:  u"Janvier",
                     2:  u"Février",
                     3:  u"Mars",
                     4:  u"Avril",
                     5:  u"Mai",
                     6:  u"Juin",
                     7:  u"Juillet",
                     8:  u"Août",
                     9:  u"Septembre",
                     10: u"Octobre",
                     11: u"Novembre",
                     12: u"Décembre"}

        legend_list = []
        graph = ['<script type="text/javascript">']
        graph.append("var chartData = [")

        for month in range(9, 13):
            graph.append("{")
            graph.append('  "month": "%s",' % dicoLabel[month])
            if month in months_dict:
                for month_consultation in months_dict[month]:
                    graph.append('  "%s": %s,' % (month_consultation["public"], str(month_consultation["consultations"])))
                    # legend_list.append(month_consultation["public"])

            graph.append('},')

        for month in range(1, 9):
            graph.append("{")
            graph.append('  "month": "%s",' % dicoLabel[month])
            if month in months_dict:
                for month_consultation in months_dict[month]:
                    graph.append('  "%s": %s,' % (month_consultation["public"], str(month_consultation["consultations"])))
                    # legend_list.append(month_consultation["public"])

            graph.append('},')

        graph.append('];')

        graph.append('''
        AmCharts.ready(function() {
            // SERIALL CHART
            var chart = new AmCharts.AmSerialChart();
            chart.dataProvider = chartData;
            chart.categoryField = "month";
            chart.plotAreaBorderAlpha = 0.2;

            // AXES
            // Category
            var categoryAxis = chart.categoryAxis;
            categoryAxis.gridAlpha = 0.1;
            categoryAxis.axisAlpha = 0;
            categoryAxis.gridPosition = "start";
            categoryAxis.labelRotation = 65;

            // value
            var valueAxis = new AmCharts.ValueAxis();
            valueAxis.stackType = "regular";
            valueAxis.gridAlpha = 0.1;
            valueAxis.axisAlpha = 0;
            chart.addValueAxis(valueAxis);
        ''')

        legend_color = {"Auteur":     "#C72C95",
                        "Co-auteur":  "#D8E0BD",
                        "Lecteur":    "#B3DBD4",
                        "Etudiant":   "#69A55C",
                        "Manager":    "#B5B8D3",
                        "Secretaire": "#F4E23B"}
        # legend_list = list(set(legend_list))
        legend_list = self._public_bdd
        for legend in legend_list:
            graph.append('''
                // GRAPHS
                // firstgraph
                 var graph = new AmCharts.AmGraph();
                graph.title = "%s";
                graph.labelText = "[[value]]";
                graph.valueField = "%s";
                graph.type = "column";
                graph.lineAlpha = 0;
                graph.fillAlphas = 1;
                graph.lineColor = "%s";
                graph.balloonText = "<b><span style='color:%s'>[[title]]</b></span><br><span style='font-size:14px'>[[category]]: <b>[[value]]</b></span>";
                graph.labelPosition = "middle";
                chart.addGraph(graph);

                // LEGEND
                var legend = new AmCharts.AmLegend();
                legend.position = "bottom";
                legend.borderAlpha = 0.3;
                legend.horizontalGap = 10;
                legend.switchType = "v";
                chart.addLegend(legend);''' % (legend, legend, legend_color[legend], legend_color[legend]))

        graph.append('''
            chart.creditsPosition = "top-right";

            chart.write("chartdiv");
        });
        </script>''')

        return "\n".join(graph)

    def getMinMaxYearByELP(self, COD_ELP):
        session = self.getSession()
        ICE = aliased(tables.IndContratElpSQLITE)
        requete = session.query(ICE.SESAME_ETU).filter(ICE.COD_ELP == COD_ELP).all()
        listeInds = [x[0] for x in requete]
        if self._use_mysql:
            session = self.getSessionMySQL()
            return jalon_mysql.getMinMaxYearByELP(session, COD_ELP, listeInds)
        else:
            return jalonsqlite.getMinMaxYearByELP(session, COD_ELP, listeInds)

    # -------------------------- #
    #  Évaluation par les pairs  #
    # -------------------------- #
    def setEvaluatePeer(self, DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, CRITERIA, CRITERIA_NOTE, CRITERIA_COMMENT):
        session = self.getSessionMySQL()
        jalon_mysql.setEvaluatePeer(session, DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, CRITERIA, datetime.now(), CRITERIA_NOTE, CRITERIA_COMMENT)

    def deletePeersEvaluation(self, DEPOSIT_BOX):
        session = self.getSessionMySQL()
        jalon_mysql.deletePeersEvaluation(session, DEPOSIT_BOX)

    def setSelfEvaluate(self, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_NOTE, CRITERIA_COMMENT):
        session = self.getSessionMySQL()
        jalon_mysql.setSelfEvaluate(session, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, datetime.now(), CRITERIA_NOTE, CRITERIA_COMMENT)

    def getSelfEvaluate(self, DEPOSIT_BOX, DEPOSIT_STU):
        session = self.getSessionMySQL()
        return jalon_mysql.getSelfEvaluate(session, DEPOSIT_BOX, DEPOSIT_STU)

    def setPeerEvaluationNote(self, DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, NOTE):
        session = self.getSessionMySQL()
        jalon_mysql.setPeerEvaluationNote(session, DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, NOTE)

    def setSelfEvaluationNote(self, DEPOSIT_BOX, DEPOSIT_STU, NOTE):
        session = self.getSessionMySQL()
        jalon_mysql.setSelfEvaluationNote(session, DEPOSIT_BOX, DEPOSIT_STU, NOTE)

    def getSelfEvaluationNote(self, DEPOSIT_BOX, DEPOSIT_STU):
        session = self.getSessionMySQL()
        return jalon_mysql.getSelfEvaluationNote(session, DEPOSIT_BOX, DEPOSIT_STU)

    def getPeerEvaluation(self, DEPOSIT_BOX, DEPOSIT_STU):
        session = self.getSessionMySQL()
        return jalon_mysql.getPeerEvaluation(session, DEPOSIT_BOX, DEPOSIT_STU)

    def getPeerEvaluationsNotes(self, DEPOSIT_BOX, CORRECTED_STU):
        session = self.getSessionMySQL()
        return jalon_mysql.getPeerEvaluationsNotes(session, DEPOSIT_BOX, CORRECTED_STU)

    def getPeerAverage(self, DEPOSIT_BOX, DEPOSIT_STU):
        session = self.getSessionMySQL()
        return jalon_mysql.getPeerAverage(session, DEPOSIT_BOX, DEPOSIT_STU)

    def getCriteriaAverage(self, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA):
        session = self.getSessionMySQL()
        return jalon_mysql.getCriteriaAverage(session, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA)

    def getEvaluationByCorrectedSTU(self, DEPOSIT_BOX, CORRECTED_STU):
        session = self.getSessionMySQL()
        return jalon_mysql.getEvaluationByCorrectedSTU(session, DEPOSIT_BOX, CORRECTED_STU)

    def getEvaluationByCorrectedAndDepositSTU(self, DEPOSIT_BOX, CORRECTED_STU, DEPOSIT_STU):
        session = self.getSessionMySQL()
        return jalon_mysql.getEvaluationByCorrectedAndDepositSTU(session, DEPOSIT_BOX, CORRECTED_STU, DEPOSIT_STU)

    def generatePeersAverage(self, DEPOSIT_BOX):
        session = self.getSessionMySQL()
        return jalon_mysql.generatePeersAverage(session, DEPOSIT_BOX)

    def generateEvaluationsAverage(self, DEPOSIT_BOX):
        session = self.getSessionMySQL()
        return jalon_mysql.generateEvaluationsAverage(session, DEPOSIT_BOX)

    def setAveragePeer(self, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_CODE, CRITERIA_VALUE, CRITERIA_AVERAGE, CRITERIA_NOTE_T, CRITERIA_COMMENT_T):
        session = self.getSessionMySQL()
        jalon_mysql.setAveragePeer(session, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_CODE, CRITERIA_VALUE, datetime.now(), CRITERIA_AVERAGE, CRITERIA_NOTE_T, CRITERIA_COMMENT_T)

    def deleteAverageByDepositBox(self, DEPOSIT_BOX):
        session = self.getSessionMySQL()
        jalon_mysql.deleteAverageByDepositBox(session, DEPOSIT_BOX)

    def deleteEvaluationsAverageByDepositBox(self, DEPOSIT_BOX):
        session = self.getSessionMySQL()
        jalon_mysql.deleteEvaluationsAverageByDepositBox(session, DEPOSIT_BOX)

    def updateAveragePeer(self, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_CODE, CRITERIA_VALUE, CRITERIA_AVERAGE, CRITERIA_NOTE_T, CRITERIA_COMMENT_T):
        session = self.getSessionMySQL()
        jalon_mysql.updateAveragePeer(session, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_CODE, CRITERIA_VALUE, datetime.now(), CRITERIA_AVERAGE, CRITERIA_NOTE_T, CRITERIA_COMMENT_T)

    def setEvaluationAverage(self, DEPOSIT_BOX, DEPOSIT_STU, AVERAGE, IS_VERIFICATION):
        session = self.getSessionMySQL()
        jalon_mysql.setEvaluationAverage(session, DEPOSIT_BOX, DEPOSIT_STU, AVERAGE, IS_VERIFICATION)

    def updateEvaluationAverage(self, DEPOSIT_BOX, DEPOSIT_STU, AVERAGE, IS_VERIFICATION):
        session = self.getSessionMySQL()
        jalon_mysql.updateEvaluationAverage(session, DEPOSIT_BOX, DEPOSIT_STU, AVERAGE, IS_VERIFICATION)

    def getPeersAverage(self, DEPOSIT_BOX):
        session = self.getSessionMySQL()
        return jalon_mysql.getPeersAverage(session, DEPOSIT_BOX)

    def getCountEvaluationsNotes(self, DEPOSIT_BOX):
        session = self.getSessionMySQL()
        return jalon_mysql.getCountEvaluationsNotes(session, DEPOSIT_BOX)

    def getCountVerifEvaluationsNotes(self, DEPOSIT_BOX):
        session = self.getSessionMySQL()
        return jalon_mysql.getCountVerifEvaluationsNotes(session, DEPOSIT_BOX)

    def getInfoEvaluationsNotes(self, DEPOSIT_BOX):
        session = self.getSessionMySQL()
        return jalon_mysql.getInfoEvaluationsNotes(session, DEPOSIT_BOX)

    def getInfoCriteriaNotes(self, DEPOSIT_BOX):
        session = self.getSessionMySQL()
        return jalon_mysql.getInfoCriteriaNotes(session, DEPOSIT_BOX)

    def getInfoCriteriaNoteByDepositStu(self, DEPOSIT_BOX, CHECK=None):
        session = self.getSessionMySQL()
        return jalon_mysql.getInfoCriteriaNoteByDepositStu(session, DEPOSIT_BOX, CHECK)

    def getInfoEvaluationNoteByDepositStu(self, DEPOSIT_BOX, CHECK=None):
        session = self.getSessionMySQL()
        return jalon_mysql.getInfoEvaluationNoteByDepositStu(session, DEPOSIT_BOX, CHECK)

    def getEvaluationNoteByDeposiSTU(self, DEPOSIT_BOX, DEPOSIT_STU):
        session = self.getSessionMySQL()
        return jalon_mysql.getEvaluationNoteByDeposiSTU(session, DEPOSIT_BOX, DEPOSIT_STU)


    # def getPeerAverage(self, DEPOSIT_BOX, DEPOSIT_STU):
    #    session = self.getSessionMySQL()
    #    return jalon_mysql.getPeerAverage(session, DEPOSIT_BOX, DEPOSIT_STU)

    # ----------------------- #
    #  Fonctions utilitaires  #
    # ----------------------- #
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
                "tous":   [{"type":    "etape",
                            "libelle": _(u"Diplôme")},
                           {"type":    "ue",
                            "libelle": _(u"Unité d'enseignement")},
                           {"type":    "uel",
                            "libelle": _(u"Unité d'enseignement libre")},
                           {"type":    "groupe",
                            "libelle": _(u"Groupe")}]}
        return dico[type]

    def genererFrequentationGraph(self, dates_dict, DATE_CONS_YEAR=None):
        # LOG.info("----- genererFrequentationGraph -----")
        # LOG.info(dates_dict)

        graph = ['<script type="text/javascript">']
        graph.append("""var chart = AmCharts.makeChart("frequentationchartdiv", {
                        "type": "serial",
                        "theme": "light",
                        "marginRight": 40,
                        "marginLeft": 40,
                        "autoMarginOffset": 20,
                        "dataDateFormat": "YYYY-MM-DD",
                        "valueAxes": [{
                            "id": "v1",
                            "axisAlpha": 0,
                            "position": "left",
                            "ignoreAxisWidth":true
                        }],
                        "balloon": {
                            "borderThickness": 1,
                            "shadowAlpha": 0
                        },
                        "graphs": [{
                            "id": "g1",
                            "balloon":{
                              "drop":true,
                              "adjustBorderColor":false,
                              "color":"#ffffff"
                            },
                            "bullet": "round",
                            "bulletBorderAlpha": 1,
                            "bulletColor": "#FFFFFF",
                            "bulletSize": 5,
                            "hideBulletsCount": 50,
                            "lineThickness": 2,
                            "title": "red line",
                            "useLineColorForBulletBorder": true,
                            "valueField": "value",
                            "balloonText": "<span style='font-size:18px;'>[[value]]</span>"
                        }],
                        "chartScrollbar": {
                            "graph": "g1",
                            "oppositeAxis":false,
                            "offset":15,
                            "scrollbarHeight": 80,
                            "backgroundAlpha": 0,
                            "selectedBackgroundAlpha": 0.1,
                            "selectedBackgroundColor": "#888888",
                            "graphFillAlpha": 0,
                            "graphLineAlpha": 0.5,
                            "selectedGraphFillAlpha": 0,
                            "selectedGraphLineAlpha": 1,
                            "autoGridCount":true,
                            "color":"#AAAAAA"
                        },
                        "chartCursor": {
                            "pan": true,
                            "valueLineEnabled": true,
                            "valueLineBalloonEnabled": true,
                            "cursorAlpha":1,
                            "cursorColor":"#258cbb",
                            "limitToGraph":"g1",
                            "valueLineAlpha":0.2
                        },
                        "valueScrollbar":{
                          "oppositeAxis":false,
                          "offset":50,
                          "scrollbarHeight":10
                        },
                        "categoryField": "date",
                        "categoryAxis": {
                            "parseDates": true,
                            "dashLength": 1,
                            "minorGridEnabled": true
                        },
                        "export": {
                            "enabled": true
                        },
                        "dataProvider": [""")

        if not DATE_CONS_YEAR or DATE_CONS_YEAR == '0':
            DATE_CONS_YEAR = DateTime().year()

        date_stop = datetime.now().date()
        date_start = date_stop - timedelta(days=90)

        date_value = []
        for dt in rrule.rrule(rrule.DAILY, dtstart=date_start, until=date_stop):
            date = dt.date()
            # LOG.info(date)
            frequentation = dates_dict[date] if date in dates_dict else 0
            date_value.append("""{"date": "%s", "value": %s}""" % (date, frequentation))
        graph.append(",\n".join(date_value))
        graph.append("""]
                        });
                        chart.addListener("rendered", zoomChart);
                        zoomChart();

                        function zoomChart() {
                            chart.zoomToIndexes(chart.dataProvider.length - 40, chart.dataProvider.length - 1);
                        }""")
        graph.append("</script>")
        # LOG.info("\n".join(graph))
        return "\n".join(graph)

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
        textes = {"bdd":            _(u"Offre de formation"),
                  "configsite":     _(u"Configuration du site"),
                  "mes_ressources": _(u"Mes ressources"),
                  "gestion_util":   _(u"Gestion des Utilisateurs")}
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
        # session.execute("DROP TABLE connexion")
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

    def getConsultation(self):
        session = self.getSession()
        if self._typeBDD == "sqlite":
            return jalonsqlite.getConsultation(session)

    def addConnexionINDMySQL(self, SESAME_ETU, DATE_CONN):
        session = self.getSessionMySQL()
        jalon_mysql.addConnexionIND(session, SESAME_ETU, datetime.strptime(DATE_CONN, '%Y-%m-%d %H:%M:%S'))

    def addConsultationINDMySQL(self, SESAME_ETU, DATE_CONN, ID_COURS, TYPE_CONS, ID_CONS):
        session = self.getSessionMySQL()
        jalon_mysql.addConsultationIND(session, SESAME_ETU, datetime.strptime(DATE_CONN, '%Y-%m-%d %H:%M:%S'), ID_COURS, TYPE_CONS, ID_CONS)

    def convertirResultatBDD(self, resultat):
        conversion = []
        if resultat:
            for ligne in resultat:
                conversion.append(dict(zip(ligne.keys(), ligne)))
        return conversion

    def execRequeteBDD(self, requete, maj=False, use_mysql=False):
        if use_mysql:
            session = self.getSessionMySQL()
        else:
            session = self.getSession()
        requete = session.execute(requete)
        if maj:
            session.commit()
            return "MAJ OK"
        return self.convertirResultatBDD(requete)

    def getBreadcrumbs(self, user):
        if user.has_role("Secretaire"):
            return [{"title": _(u"Gestion pédagogique"),
                     "icon":  "fa fa-database",
                     "link":  "%s/gestion_utilisateurs" % self.absolute_url()}]
        else:
            return [{"title": _(u"Gestion pédagogique"),
                     "icon":  "fa fa-database",
                     "link":  "%s/@@jalon-bdd?gestion=gestion_bdd" % self.absolute_url()}]
