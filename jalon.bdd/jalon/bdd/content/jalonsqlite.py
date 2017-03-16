# -*- coding: utf-8 -*-
import tables
import datetime

from DateTime import DateTime

# SQL Alchemy
from sqlalchemy import and_, or_, distinct, not_, DDL
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased

from math import ceil

# Messages de debug :
#from logging import getLogger
#LOG = getLogger( '[jalonsqlite]' )


#-------------------------------------#
# Utilitaire de la base de données    #
#-------------------------------------#
def convertirResultatBDD(recherche):
    resultat = []
    if recherche:
        for ligne in recherche:
            resultat.append(dict(zip(ligne.keys(), ligne)))
    return resultat


#-------------------------------------#
# Consultation de la base de données  #
#-------------------------------------#
def getIndividuLITE(session, sesame):
    IND = aliased(tables.IndividuSQLITE)
    recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_NOM_USU_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.DATE_NAI_IND, IND.TYPE_IND, IND.COD_ETU, IND.EMAIL_ETU, IND.ADR1_IND, IND.ADR2_IND, IND.COD_POST_IND, IND.VIL_IND, IND.UNIV_IND, IND.PROMO_IND).filter(IND.SESAME_ETU == sesame)
    return convertirResultatBDD(recherche)


def getTousIndividuLITE(session, page=None):
    if not page:
        page = 1
    IND = aliased(tables.IndividuSQLITE)
    recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.TYPE_IND, IND.COD_ETU, IND.EMAIL_ETU, IND.STATUS_IND).order_by(IND.LIB_NOM_PAT_IND).limit(50).offset((page - 1) * 50).all()
    return convertirResultatBDD(recherche)


def getNbPagesInd(session):
    IND = aliased(tables.IndividuSQLITE)
    recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.TYPE_IND, IND.COD_ETU, IND.EMAIL_ETU)
    nbPagesInd = float(recherche.count()) / 50.0
    return int(ceil(nbPagesInd))


def getUtilisateursNonInscrits(session, COD_ELP, TYPE_IND):
    IND = aliased(tables.IndividuSQLITE)
    ICE = aliased(tables.IndContratElpSQLITE)
    nbSesames = session.query(distinct(ICE.SESAME_ETU)).filter(ICE.COD_ELP == str(COD_ELP)).order_by(ICE.SESAME_ETU).count()
    if nbSesames > 500:
        listeSesames = session.query(distinct(ICE.SESAME_ETU)).filter(ICE.COD_ELP == str(COD_ELP)).order_by(ICE.SESAME_ETU)
        liste = []
        deb = 0
        while deb < nbSesames:
            fin = deb + 499
            if fin > nbSesames:
                fin = nbSesames
            rechercheInscrit = session.query(IND.SESAME_ETU).filter(IND.SESAME_ETU.in_(listeSesames[deb:fin]), IND.TYPE_IND == TYPE_IND)
            resultat = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).filter(IND.TYPE_IND == TYPE_IND).filter(not_(IND.SESAME_ETU.in_(rechercheInscrit)))
            liste.extend(resultat.all())
            deb = deb + 500
        return convertirResultatBDD(liste)
    else:
        listeSesames = session.query(distinct(ICE.SESAME_ETU)).filter(ICE.COD_ELP == str(COD_ELP)).order_by(ICE.SESAME_ETU)
        rechercheInscrit = session.query(IND.SESAME_ETU).filter(IND.SESAME_ETU.in_(listeSesames), IND.TYPE_IND == TYPE_IND)
        resultat = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).filter(IND.TYPE_IND == TYPE_IND).filter(not_(IND.SESAME_ETU.in_(rechercheInscrit)))
        return convertirResultatBDD(resultat)


def getIndividus(session, listeSesames):
    IND = aliased(tables.IndividuSQLITE)
    taille = len(listeSesames)
    if taille > 500:
        liste = []
        deb = 0
        while deb < taille:
            fin = deb + 499
            if fin > taille:
                fin = taille
            recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU, IND.TYPE_IND).filter(IND.SESAME_ETU.in_(listeSesames[deb:fin])).order_by(IND.LIB_NOM_PAT_IND)
            liste.extend(recherche.all())
            deb = deb + 500
        return liste
    else:
        recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU, IND.TYPE_IND).filter(IND.SESAME_ETU.in_(listeSesames)).order_by(IND.LIB_NOM_PAT_IND)
        return recherche.all()


def getInfosELP(session, COD_ELP):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens"), ELP.TYP_ELP, ELP.DATE_CREATION, ELP.DATE_MODIF).filter(ELP.COD_ELP == COD_ELP)
    return convertirResultatBDD(recherche)[0]


def getInfosElpParType(session, TYP_ELP, page):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    if not page:
        recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens"), ELP.TYP_ELP, ELP.DATE_CREATION, ELP.DATE_MODIF).filter(ELP.TYP_ELP == TYP_ELP).order_by(ELP.LIB_ELP)
    else:
        recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens"), ELP.TYP_ELP, ELP.DATE_CREATION, ELP.DATE_MODIF).filter(ELP.TYP_ELP == TYP_ELP).order_by(ELP.LIB_ELP).limit(50).offset((page - 1) * 50)

    return convertirResultatBDD(recherche)


def getInfosToutesELP(session, page=None):
    if not page:
        page = 1
    ELP = aliased(tables.ElementPedagogiSQLITE)

    recherche = session.query(ELP.TYP_ELP, ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens"), ELP.DATE_CREATION, ELP.DATE_MODIF).order_by(ELP.LIB_ELP).limit(50).offset((page - 1) * 50).all()
    listeELPs = convertirResultatBDD(recherche)
    return ajouterResponsable(session, listeELPs)


def ajouterResponsable(session, listeELPs):
    IND = aliased(tables.IndividuSQLITE)
    ICE = aliased(tables.IndContratElpSQLITE)
    listeCodes = [ligne["COD_ELP"] for ligne in listeELPs]

    dicoNoms = {}
    listeNoms = session.query(ICE.COD_ELP, IND.LIB_PR1_IND.concat(" ").concat(IND.LIB_NOM_PAT_IND)).outerjoin(IND, ICE.SESAME_ETU == IND.SESAME_ETU).filter(and_(ICE.RESPONSABLE == 1, ICE.COD_ELP.in_(listeCodes))).all()
    if listeNoms:
        for ligne in listeNoms:
            dicoNoms[ligne[0]] = ligne[1]
        for ligne in listeELPs:
            try:
                ligne["RESPONSABLE"] = dicoNoms[ligne["COD_ELP"]]
            except:
                ligne["RESPONSABLE"] = None
        return listeELPs
    else:
        return listeELPs


def getNbPagesELP(session):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    recherche = session.query(ELP.TYP_ELP, ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu"))
    nbPagesELP = float(recherche.count()) / 50.0
    return int(ceil(nbPagesELP))


def getNbPagesELPByType(session, TYP_ELP):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    recherche = session.query(ELP.COD_ELP).filter(ELP.TYP_ELP == TYP_ELP)
    nbPagesELP = float(recherche.count()) / 50.0
    return int(ceil(nbPagesELP))


def getInfosEtape(session, COD_ETP):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu")).filter(ELP.COD_ELP == COD_ETP)
    return recherche.first()


def getInfosGPE(session, COD_GPE):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu"), ELP.COD_GPE).filter(ELP.COD_ELP == COD_GPE)
    return recherche.first()


def getInfosELP2(session, COD_ELP):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens"), ELP.TYP_ELP, ELP.DATE_CREATION, ELP.DATE_MODIF).filter(ELP.COD_ELP == COD_ELP)
    return recherche.first()


def getELPProperties(session, COD_ELP):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.COD_GPE, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens"), ELP.TYP_ELP, ELP.DATE_CREATION, ELP.DATE_MODIF).filter(ELP.COD_ELP == COD_ELP)
    return convertirResultatBDD(recherche)


def getELPData(session, COD_ELP):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    recherche = session.query(ELP.LIB_ELP, ELP.TYP_ELP, ELP.COD_ELP, ELP.COD_GPE, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens"), ELP.DATE_CREATION, ELP.DATE_MODIF).filter(ELP.COD_ELP == COD_ELP)
    return recherche.first()


def getInscriptionPedago(session, SESAME_ETU, COD_ELP, COD_VRS_VET=None):
    ICE = aliased(tables.IndContratElpSQLITE)
    ELP = aliased(tables.ElementPedagogiSQLITE)
    ERE = aliased(tables.ETPRegroupeELPSQLITE)
    if COD_VRS_VET:
        listeIDUE = [idue[0] for idue in session.query(ICE.COD_ELP).distinct().filter(and_(ICE.SESAME_ETU == SESAME_ETU, ICE.COD_ELP_PERE == '%s-%s' % (COD_ELP, COD_VRS_VET))).all()]
    else:
        listeIDUE = []
        listeInscription = [idue[0] for idue in session.query(ICE.COD_ELP).distinct().filter(ICE.SESAME_ETU == SESAME_ETU).all()]
        if not listeInscription:
            return None
        listeEnfant = [idue[0] for idue in session.query(ERE.COD_ELP_FILS).distinct().filter(ERE.COD_ELP_PERE == COD_ELP).all()]
        taille = len(listeEnfant)
        if taille > 500:
            listeEnfant2 = []
            deb = 0
            while deb < taille:
                print deb
                fin = deb + 499
                if fin > taille:
                    fin = taille
                listeEnfant2.extend([idue[0] for idue in session.query(ERE.COD_ELP_FILS).distinct().filter(ERE.COD_ELP_PERE.in_(listeEnfant[deb:fin])).all()])
                deb = deb + 500
        else:
            listeEnfant2 = [idue[0] for idue in session.query(ERE.COD_ELP_FILS).distinct().filter(ERE.COD_ELP_PERE.in_(listeEnfant)).all()]
        if listeEnfant2:
            listeEnfant.extend(listeEnfant2)
        listeEnfant.append(COD_ELP)
        for codELP in listeInscription:
            if codELP in listeEnfant:
                listeIDUE.append(codELP)
    if not listeIDUE:
        return []
    recherche = session.query(ELP.COD_ELP, ELP.LIB_ELP, ELP.TYP_ELP).filter(ELP.COD_ELP.in_(listeIDUE))
    return convertirResultatBDD(recherche)


def getInscriptionIND(session, SESAME_ETU, TYPE_ELP):
    ICE = aliased(tables.IndContratElpSQLITE)
    ELP = aliased(tables.ElementPedagogiSQLITE)
    listeIDUE = [idue[0] for idue in session.query(ICE.COD_ELP).filter(and_(ICE.SESAME_ETU == SESAME_ETU, ICE.TYPE_ELP == TYPE_ELP)).all()]
    if not listeIDUE:
        return []
    recherche = session.query(ELP.COD_ELP, ELP.LIB_ELP).filter(ELP.COD_ELP.in_(listeIDUE))
    return convertirResultatBDD(recherche)


def getGroupesEtudiant(session, COD_ETU):
    listeGroupe = []
    ELP = aliased(tables.ElementPedagogiSQLITE)
    ICE = aliased(tables.IndContratElpSQLITE)
    ERE = aliased(tables.ETPRegroupeELPSQLITE)
    rechercheGroupe = [groupe[0] for groupe in session.query(ICE.COD_ELP).distinct().filter(and_(ICE.SESAME_ETU == COD_ETU, ICE.TYPE_ELP == 'groupe')).all()]
    if not rechercheGroupe:
        return []
    recherche = session.query(ELP.COD_ELP, ELP.LIB_ELP, ELP.COD_GPE).filter(ELP.COD_ELP.in_(rechercheGroupe)).all()
    for groupe in recherche:
        rechercheERE = session.query(ERE.TYP_ELP, ERE.COD_ELP_PERE).filter(ERE.COD_ELP_FILS == groupe[0])
        for ligne in rechercheERE.all():
            if ligne[0] == "etape":
                COD_ELP = ligne[1]
                COD_ETP, COD_VRS_VET = ligne[1].split("-")
            else:
                COD_ELP = COD_ETP = COD_VRS_VET = ligne[1]
            groupe = list(groupe)
            groupe.extend([ligne[0], COD_ELP, COD_ETP, COD_VRS_VET])
            listeGroupe.append(groupe)
    return listeGroupe


def getUeEtape(session, COD_ETP, COD_VRS_VET=None, TYP_ELP_SELECT=None):
    ERE = aliased(tables.ETPRegroupeELPSQLITE)
    ELP = aliased(tables.ElementPedagogiSQLITE)
    if COD_VRS_VET:
        COD_ELP = "%s-%s" % (COD_ETP, COD_VRS_VET)
    else:
        COD_ELP = COD_ETP
    listeIDUE = [idue[0] for idue in session.query(ERE.COD_ELP_FILS).distinct().filter(and_(ERE.COD_ELP_PERE == COD_ELP, ERE.TYP_ELP == TYP_ELP_SELECT)).all()]
    if not listeIDUE:
        return []
    taille = len(listeIDUE)
    # LOG.info("taille : %s" % taille)
    if taille > 500:
        listeIDUE2 = []
        deb = 0
        while deb < taille:
            fin = deb + 499
            if fin > taille:
                fin = taille
            listeIDUE2.extend(session.query(ELP.COD_ELP, ELP.LIB_ELP, ELP.TYP_ELP).filter(and_(ELP.COD_ELP.in_(listeIDUE[deb:fin]))))
            deb = deb + 500
    else:
        listeIDUE2 = session.query(ELP.COD_ELP, ELP.LIB_ELP, ELP.TYP_ELP).filter(and_(ELP.COD_ELP.in_(listeIDUE)))
    return convertirResultatBDD(listeIDUE2)


def getVersionEtape(session, COD_ELP, COD_VRS_VET=None):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    if COD_VRS_VET:
        etape = session.query(ELP.LIB_ELP).filter(ELP.COD_ELP == '%s-%s' % (COD_ELP, str(COD_VRS_VET))).first()
    else:
        etape = session.query(ELP.LIB_ELP).filter(ELP.COD_ELP == COD_ELP).first()
    return etape


def getElpAttach(session, COD_ELP, TYP_ELP_SELECT, TYP_ELP):
    if not TYP_ELP_SELECT:
        return []
    ERE = aliased(tables.ETPRegroupeELPSQLITE)
    ELP = aliased(tables.ElementPedagogiSQLITE)
    ERE_TYP_ELP = TYP_ELP_SELECT
    #Pegasus vérifier TYP_ELP ; TYP_ELP_SELECT
    if (TYP_ELP in ['ue', 'uel'] and TYP_ELP_SELECT == 'etape') or TYP_ELP_SELECT == 'groupe':
        ERE_TYP_ELP = TYP_ELP
    if TYP_ELP == 'etape' or (TYP_ELP in ['ue', 'uel'] and TYP_ELP_SELECT == 'groupe'):
        recherche = session.query(ERE.COD_ELP_FILS).filter(ERE.COD_ELP_PERE == COD_ELP, ERE.TYP_ELP == ERE_TYP_ELP)
    else:
        recherche = session.query(ERE.COD_ELP_PERE).filter(ERE.COD_ELP_FILS == COD_ELP, ERE.TYP_ELP == ERE_TYP_ELP)
    if not recherche:
        return []
    listeRes = [ligne[0] for ligne in recherche.all()]
    if listeRes:
        recherche = session.query(ELP.COD_ELP, ELP.LIB_ELP).filter(ELP.COD_ELP.in_(listeRes), ELP.TYP_ELP == TYP_ELP_SELECT)
        return convertirResultatBDD(recherche)
    return []


def rechercherAll(session, listeRecherche):
    listeCond = []
    ELP = aliased(tables.ElementPedagogiSQLITE)
    for element in listeRecherche:
        mot = supprimerAccent(element).upper()
        listeCond.append(or_(func.upper(ELP.COD_ELP).like(mot), func.upper(ELP.LIB_ELP).like(mot), func.upper(ELP.COD_ELP).like(element.upper().decode("utf-8")), func.upper(ELP.LIB_ELP).like(element.upper().decode("utf-8"))))
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.TYP_ELP, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens")).filter(and_(*listeCond)).order_by(ELP.LIB_ELP)
    return convertirResultatBDD(recherche.all())


def rechercherEtape(session, listeRecherche):
    listeCond = []
    ELP = aliased(tables.ElementPedagogiSQLITE)
    for element in listeRecherche:
        mot = supprimerAccent(element).upper()
        listeCond.append(or_(func.upper(ELP.COD_ELP).like(mot), func.upper(ELP.LIB_ELP).like(mot), func.upper(ELP.COD_ELP).like(element.upper().decode("utf-8")), func.upper(ELP.LIB_ELP).like(element.upper().decode("utf-8"))))
        listeCond.append(ELP.TYP_ELP == "etape")
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.TYP_ELP, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens")).filter(and_(*listeCond)).order_by(ELP.LIB_ELP)
    return convertirResultatBDD(recherche.all())


def rechercherELP(session, listeRecherche, uel):
    listeCond = []
    ELP = aliased(tables.ElementPedagogiSQLITE)
    for element in listeRecherche:
        mot = supprimerAccent(element).upper()
        listeCond.append(or_(func.upper(ELP.COD_ELP).like(mot), func.upper(ELP.LIB_ELP).like(mot), func.upper(ELP.COD_ELP).like(element.upper().decode("utf-8")), func.upper(ELP.LIB_ELP).like(element.upper().decode("utf-8"))))
    if uel:
        listeCond.append(ELP.TYP_ELP == "uel")
    else:
        listeCond.append(ELP.TYP_ELP == "ue")
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.TYP_ELP, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens")).filter(and_(*listeCond)).order_by(ELP.LIB_ELP)
    return convertirResultatBDD(recherche.all())


def rechercherGPE(session, listeRecherche):
    listeCond = []
    ELP = aliased(tables.ElementPedagogiSQLITE)
    for element in listeRecherche:
        mot = supprimerAccent(element).upper()
        listeCond.append(or_(func.upper(ELP.COD_ELP).like(mot), func.upper(ELP.LIB_ELP).like(mot), func.upper(ELP.COD_GPE).like(mot), func.upper(ELP.COD_ELP).like(element.upper().decode("utf-8")), func.upper(ELP.LIB_ELP).like(element.upper().decode("utf-8")), func.upper(ELP.COD_GPE).like(element.upper().decode("utf-8"))))
        listeCond.append(ELP.TYP_ELP == "groupe")
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.TYP_ELP, ELP.COD_GPE, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens")).filter(and_(*listeCond)).order_by(ELP.LIB_ELP)
    return convertirResultatBDD(recherche.all())


def searchELP(session, search_terms_list, search_elp_type=None):
    conditions_list = []
    ELP = aliased(tables.ElementPedagogiSQLITE)
    for search_term in search_terms_list:
        word = supprimerAccent(search_term).upper()
        conditions_list.append(or_(func.upper(ELP.COD_ELP).like(word), func.upper(ELP.LIB_ELP).like(word), func.upper(ELP.COD_GPE).like(word), func.upper(ELP.COD_ELP).like(search_term.decode("utf-8")), func.upper(ELP.LIB_ELP).like(search_term.decode("utf-8")), func.upper(ELP.COD_GPE).like(search_term.decode("utf-8"))))
    if search_elp_type:
        conditions_list.append(ELP.TYP_ELP == search_elp_type)
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, ELP.TYP_ELP, ELP.COD_GPE, ELP.ETU_ELP.label("nb_etu"), ELP.ENS_ELP.label("nb_ens")).filter(and_(*conditions_list)).order_by(ELP.LIB_ELP)
    return convertirResultatBDD(recherche.all())


def rechercherEtudiantXLS(session, COD_ELP, TYPE_IND):
    IND = aliased(tables.IndividuSQLITE)
    ICE = aliased(tables.IndContratElpSQLITE)
    #recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU, IND.UNIV_IND).filter(ICE.COD_ELP == COD_ELP, IND.TYPE_IND == TYPE_IND).order_by(IND.LIB_NOM_PAT_IND)
    recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU, IND.UNIV_IND).outerjoin(ICE, ICE.SESAME_ETU == IND.SESAME_ETU).filter(ICE.COD_ELP == COD_ELP, IND.TYPE_IND == TYPE_IND).order_by(IND.LIB_NOM_PAT_IND)
    return convertirResultatBDD(recherche)


def rechercherUtilisateurs(session, COD_ELP, TYPE_IND, inscrit=None, listeEtu=None, Resp=None):
    IND = aliased(tables.IndividuSQLITE)
    ICE = aliased(tables.IndContratElpSQLITE)
    sesameEnsResp = session.query(ICE.SESAME_ETU).filter(and_(ICE.COD_ELP == str(COD_ELP), ICE.RESPONSABLE == 1)).first()
    # S'il y a un enseignant responsable pour cet ELP
    if sesameEnsResp:
        if inscrit:
            if Resp == 0:
                recherche = session.query(IND.LIB_NOM_PAT_IND.concat(" ").concat(IND.LIB_PR1_IND).label("name"), IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).outerjoin(ICE, ICE.SESAME_ETU == IND.SESAME_ETU).filter(ICE.COD_ELP == COD_ELP, IND.TYPE_IND == TYPE_IND, IND.SESAME_ETU != sesameEnsResp[0]).order_by(IND.LIB_NOM_PAT_IND)
            else:
                recherche = session.query(IND.LIB_NOM_PAT_IND.concat(" ").concat(IND.LIB_PR1_IND).label("name"), IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).outerjoin(ICE, ICE.SESAME_ETU == IND.SESAME_ETU).filter(ICE.COD_ELP == COD_ELP, IND.TYPE_IND == TYPE_IND).order_by(IND.LIB_NOM_PAT_IND)
        else:
            if listeEtu and type(listeEtu[0]) == dict:
                listeEtu = [x["SESAME_ETU"] for x in listeEtu]
            if Resp == 0:
                recherche = session.query(IND.LIB_NOM_PAT_IND.concat(" ").concat(IND.LIB_PR1_IND).label("name"), IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).filter(not_(IND.SESAME_ETU.in_(listeEtu)), IND.TYPE_IND == TYPE_IND, IND.SESAME_ETU != sesameEnsResp[0]).order_by(IND.LIB_NOM_PAT_IND)
            else:
                recherche = session.query(IND.LIB_NOM_PAT_IND.concat(" ").concat(IND.LIB_PR1_IND).label("name"), IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).filter(not_(IND.SESAME_ETU.in_(listeEtu)), IND.TYPE_IND == TYPE_IND).order_by(IND.LIB_NOM_PAT_IND)
    # S'il n'y a pas d'enseignant responsable
    else:
        if inscrit:
            recherche = session.query(IND.LIB_NOM_PAT_IND.concat(" ").concat(IND.LIB_PR1_IND).label("name"), IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).outerjoin(ICE, ICE.SESAME_ETU == IND.SESAME_ETU).filter(ICE.COD_ELP == COD_ELP, IND.TYPE_IND == TYPE_IND).order_by(IND.LIB_NOM_PAT_IND)
        else:
            if listeEtu and type(listeEtu[0]) == dict:
                listeEtu = [x["SESAME_ETU"] for x in listeEtu]
            recherche = session.query(IND.LIB_NOM_PAT_IND.concat(" ").concat(IND.LIB_PR1_IND).label("name"), IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.COD_ETU, IND.EMAIL_ETU).filter(not_(IND.SESAME_ETU.in_(listeEtu)), IND.TYPE_IND == TYPE_IND).order_by(IND.LIB_NOM_PAT_IND)
    return convertirResultatBDD(recherche)


def rechercherUtilisateursByName(session, listeRecherche, typeUser):
    IND = aliased(tables.IndividuSQLITE)
    listeCond = []
    for element in listeRecherche:
        mot = supprimerAccent(element).upper()
        listeCond.append(or_(func.upper(IND.LIB_NOM_PAT_IND).like(mot), func.upper(IND.LIB_PR1_IND).like(mot), func.upper(IND.SESAME_ETU).like(mot)))
    if typeUser == "Etudiant":
        listeCond.append(IND.TYPE_IND == "Etudiant")
    else:
        listeCond.append(IND.TYPE_IND <> "Etudiant")
    recherche = session.query(IND.LIB_PR1_IND.concat(" ").concat(IND.LIB_NOM_PAT_IND).concat(" (").concat(IND.SESAME_ETU).concat(")").label("name"), IND.SESAME_ETU.label("id"), IND.EMAIL_ETU.label("email")).filter(and_(*listeCond)).order_by(IND.LIB_NOM_PAT_IND)
    return convertirResultatBDD(recherche)


def rechercherUtilisateursByNameOrType(session, listeRecherche, typeUser, page=None):
    if not page:
        page = 1
    IND = aliased(tables.IndividuSQLITE)
    listeCond = []
    if listeRecherche:
        for element in listeRecherche:
            mot = supprimerAccent(element).upper()
            mot2 = element.decode("utf-8")
            listeCond.append(or_(func.upper(IND.LIB_NOM_PAT_IND).like(mot), IND.LIB_NOM_PAT_IND.like(mot2), func.upper(IND.LIB_PR1_IND).like(mot), IND.LIB_PR1_IND.like(mot2), func.upper(IND.SESAME_ETU).like(mot), IND.SESAME_ETU.like(mot2)))
    if typeUser:
        listeCond.append(IND.TYPE_IND == typeUser)
    if listeCond:
        recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.TYPE_IND, IND.COD_ETU, IND.EMAIL_ETU, IND.STATUS_IND).filter(and_(*listeCond)).order_by(IND.LIB_NOM_PAT_IND).limit(50).offset((page - 1) * 50).all()
        return convertirResultatBDD(recherche)
    return []


def rechercherEnseignantResp(session, code):
    IND = aliased(tables.IndividuSQLITE)
    ICE = aliased(tables.IndContratElpSQLITE)
    sesame = session.query(ICE.SESAME_ETU).filter(and_(ICE.COD_ELP == str(code), ICE.RESPONSABLE == 1)).first()
    if sesame:
        recherche = session.query(IND.LIB_PR1_IND.concat(" ").concat(IND.LIB_NOM_PAT_IND).label("name")).filter(IND.SESAME_ETU == sesame[0])
        return convertirResultatBDD(recherche)


def isINDActif(session, SESAME_ETU):
    IND = aliased(tables.IndividuSQLITE)
    recherche = session.query(IND.STATUS_IND).filter(IND.SESAME_ETU==SESAME_ETU)
    return convertirResultatBDD(recherche)


def supprimerAccent(ligne):
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


def getEnfantELP(session, COD_ELP, TYP_ELP_SELECT=None):
    ERE = aliased(tables.ETPRegroupeELPSQLITE)
    ELP = aliased(tables.ElementPedagogiSQLITE)

    if TYP_ELP_SELECT:
        recherche = session.query(ERE.COD_ELP_FILS).filter(ERE.COD_ELP_PERE == COD_ELP, ERE.TYP_ELP == TYP_ELP_SELECT)
    else:
        recherche = session.query(ERE.COD_ELP_FILS).filter(ERE.COD_ELP_PERE == COD_ELP)

    if not recherche:
        return []
    listeRes = [ligne[0] for ligne in recherche.all()]
    recherche = session.query(ELP.COD_ELP, ELP.LIB_ELP, ELP.TYP_ELP, ELP.COD_GPE).filter(ELP.COD_ELP.in_(listeRes)).order_by(ELP.LIB_ELP)
    return convertirResultatBDD(recherche)


#----------------------------#
# Interrogation statistique  #
#----------------------------#
def updateTableConnexion(session):
    add_column = DDL('ALTER TABLE connexion ADD COLUMN ANNEE_CONN INTEGER AFTER DATE_CONN')
    session.execute(add_column)
    add_column = DDL('ALTER TABLE connexion ADD COLUMN MOIS_CONN INTEGER AFTER ANNEE_CONN')
    session.execute(add_column)
    add_column = DDL('ALTER TABLE connexion ADD COLUMN JOUR_CONN INTEGER AFTER MOIS_CONN')
    session.execute(add_column)
    add_column = DDL('ALTER TABLE connexion ADD COLUMN TIME_CONN INTEGER AFTER JOUR_CONN')
    session.execute(add_column)
    add_column = DDL('ALTER TABLE connexion ADD COLUMN HEURE_CONN INTEGER AFTER HEURE_CONN')
    session.execute(add_column)
    #session.commit()

    CI = aliased(tables.ConnexionINDSQLITE)
    listeConnexion = session.query(CI.SESAME_ETU, CI.DATE_CONN).all()

    for connexion in listeConnexion:
        date = DateTime(connexion[1])
        session.execute("update connexion set ANNEE_CONN=%s, MOIS_CONN=%s, JOUR_CONN=%s, TIME_CONN='0', HEURE_CONN=0 where SESAME_ETU='%s' and DATE_CONN='%s'" % (date.year(), date.month(), date.day(), connexion[0], connexion[1]))

    listeConnexion = session.query(CI.SESAME_ETU, CI.DATE_CONN, CI.ANNEE_CONN, CI.MOIS_CONN, CI.JOUR_CONN, CI.TIME_CONN, CI.HEURE_CONN).all()
    return listeConnexion


def getIndByElp(session, COD_ELP):
    ICE = aliased(tables.IndContratElpSQLITE)
    requete = session.query(ICE.SESAME_ETU).filter(ICE.COD_ELP==COD_ELP).all()
    listeInds = [x[0] for x in requete]
    return listeInds


def getConnexionELPByMonth(session, COD_ELP, month, year='%', listeInds=None):
    if not listeInds:
        ICE = aliased(tables.IndContratElpSQLITE)
        requete = session.query(ICE.SESAME_ETU).filter(ICE.COD_ELP==COD_ELP).all()
        listeInds = [x[0] for x in requete]

    mois = year + '/' + month + '/%'
    CI = aliased(tables.ConnexionINDSQLITE)
    nbConnexion = session.query(CI.SESAME_ETU).filter(and_(CI.SESAME_ETU.in_(listeInds), CI.DATE_CONN.like(mois)))
    return nbConnexion.count()


def getConnexionELPByYear(session, COD_ELP, year, listeInds=None):
    if not listeInds:
        ICE = aliased(tables.IndContratElpSQLITE)
        requete = session.query(ICE.SESAME_ETU).filter(ICE.COD_ELP==COD_ELP).all()
        listeInds = [x[0] for x in requete]

    annee = year + '/%'
    CI = aliased(tables.ConnexionINDSQLITE)
    nbConnexion = session.query(CI.SESAME_ETU, CI.DATE_CONN).filter(and_(CI.SESAME_ETU.in_(listeInds), CI.DATE_CONN.like(annee)))
    return nbConnexion


def getIndAndNameByElp(session, COD_ELP):
    ICE = aliased(tables.IndContratElpSQLITE)
    requete = session.query(ICE.SESAME_ETU).filter(ICE.COD_ELP==COD_ELP).all()
    listeSesames = [x[0] for x in requete]

    IND = aliased(tables.IndividuSQLITE)
    listeInds = session.query(IND.SESAME_ETU, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.UNIV_IND).filter(IND.SESAME_ETU.in_(listeSesames)).order_by(IND.LIB_NOM_PAT_IND).all()
    return convertirResultatBDD(listeInds)


def getConnexionELPByMonthByIND(session, COD_ELP, month, year='%', listeInds=None):
    if not listeInds:
        ICE = aliased(tables.IndContratElpSQLITE)
        requete = session.query(ICE.SESAME_ETU).filter(ICE.COD_ELP==COD_ELP).all()
        listeInds = [x[0] for x in requete]

    mois = year + '/' + month + '/%'
    CI = aliased(tables.ConnexionINDSQLITE)
    nbConnexion = session.query(CI.SESAME_ETU, func.count(CI.DATE_CONN)).filter(and_(CI.SESAME_ETU.in_(listeInds), CI.DATE_CONN.like(mois))).group_by(CI.SESAME_ETU)
    return nbConnexion


def getConnexionELPByYearByIND(session, COD_ELP, year, listeInds=None):
    if not listeInds:
        ICE = aliased(tables.IndContratElpSQLITE)
        requete = session.query(ICE.SESAME_ETU).filter(ICE.COD_ELP==COD_ELP).all()
        listeInds = [x[0] for x in requete]

    annee = year + '/%'
    CI = aliased(tables.ConnexionINDSQLITE)
    nbConnexion = session.query(CI.SESAME_ETU, func.count(CI.DATE_CONN)).filter(and_(CI.SESAME_ETU.in_(listeInds), CI.DATE_CONN.like(annee))).group_by(CI.SESAME_ETU)
    return nbConnexion


def getConnexionByIND(session, SESAME_ETU):
    CI = aliased(tables.ConnexionINDSQLITE)
    nbConnexion = session.query(CI.DATE_CONN).filter(CI.SESAME_ETU==SESAME_ETU)
    return nbConnexion


def getConsultationCoursByMonth(session, month, year='%', listeIdCours=[], SESAME_ETU=None):
    mois = year + '/' + month + '/%'
    COC = aliased(tables.ConsultationCoursSQLITE)
    if SESAME_ETU:
        nbConnexion = session.query(COC.ID_COURS, func.count(COC.DATE_CONS)).filter(and_(COC.SESAME_ETU==SESAME_ETU, COC.ID_COURS.in_(listeIdCours), COC.DATE_CONS.like(mois))).group_by(COC.ID_COURS)
    else:
        nbConnexion = session.query(COC.ID_COURS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS.in_(listeIdCours), COC.DATE_CONS.like(mois))).group_by(COC.ID_COURS)
    return nbConnexion


def getConsultationCoursByYear(session, year='%', listeIdCours=[], SESAME_ETU=None):
    mois = year + '/%'
    COC = aliased(tables.ConsultationCoursSQLITE)
    if SESAME_ETU:
        nbConnexion = session.query(COC.ID_COURS, func.count(COC.DATE_CONS)).filter(and_(COC.SESAME_ETU==SESAME_ETU, COC.ID_COURS.in_(listeIdCours), COC.DATE_CONS.like(mois))).group_by(COC.ID_COURS)
    else:
        nbConnexion = session.query(COC.ID_COURS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS.in_(listeIdCours), COC.DATE_CONS.like(mois))).group_by(COC.ID_COURS)
    return nbConnexion


def getMinMaxYearByELP(session, COD_ELP, listeInds):
    retour = {"min": 0, "max": 0, "ecart": 0}
    CI = aliased(tables.ConnexionINDSQLITE)
    minMaxYear = session.query(func.distinct(CI.DATE_CONN)).filter(CI.SESAME_ETU.in_(listeInds)).order_by(CI.DATE_CONN)
    if minMaxYear:
        retour["min"] = int(minMaxYear[0][0].split("/")[0])
        retour["max"] = int(minMaxYear[-1][0].split("/")[0])
        retour["ecart"] = retour["max"] - retour["min"]
    return retour


#-------------------------------------#
# Modification de la base de données  #
#-------------------------------------#
def addConnexionIND(session, SESAME_ETU, DATE_CONN):
    session.add(tables.ConnexionINDSQLITE(SESAME_ETU=SESAME_ETU, DATE_CONN=DATE_CONN))
    session.commit()


def setInfosELP(session, param):
    for key in param.keys():
        param[key] = param[key].decode("utf-8")
    datemodif = datetime.datetime.now().strftime('%m/%d/%y %H:%M')
    if (param["COD_ELP"] != param["codeELP"]):
        session.execute("update ind_contrat_elp_lite set COD_ELP='%s' where COD_ELP=='%s'" % (param["COD_ELP"], param["codeELP"]))
        session.execute("update etp_regroupe_elp_lite set COD_ELP_FILS='%s' where COD_ELP_PERE=='%s'" % (param["COD_ELP"], param["codeELP"]))
    session.execute("update element_pedagogi_lite set COD_ELP='%s', LIB_ELP='%s', TYP_ELP='%s', DATE_MODIF='%s' where COD_ELP=='%s'" % (param["COD_ELP"], param["LIB_ELP"], param["TYP_ELP"], datemodif, param["codeELP"]))
    session.flush()
    session.commit()


def insererELP(session, param):
    for key in param.keys():
        param[key] = param[key].decode("utf-8")
    datecreation = datetime.datetime.now().strftime('%m/%d/%y %H:%M')
    if param["TYP_ELP"] == "groupe":
        codeGroupe = param["COD_ELP"]
        session.add(tables.ElementPedagogiSQLITE(COD_ELP=param["COD_ELP"], LIB_ELP=param["LIB_ELP"], TYP_ELP=param["TYP_ELP"], COD_GPE=codeGroupe, DATE_CREATION=datecreation))
    else:
        session.add(tables.ElementPedagogiSQLITE(COD_ELP=param["COD_ELP"], LIB_ELP=param["LIB_ELP"], TYP_ELP=param["TYP_ELP"], DATE_CREATION=datecreation))
    session.commit()


def supprimerELP(session, param):
    session.execute("delete from etp_regroupe_elp_lite where COD_ELP_FILS=='%s'" % (param["COD_ELP"]))
    session.execute("delete from element_pedagogi_lite where COD_ELP=='%s'" % (param["COD_ELP"]))
    session.execute("delete from ind_contrat_elp_lite where COD_ELP=='%s'" % (param["COD_ELP"]))
    session.flush()
    session.commit()


def creerUtilisateur(session, param):
    sesame = param["SESAME_ETU"].replace(" ", "")
    individu = getIndividuLITE(session, sesame)
    if not individu:
        if param["TYPE_IND"] in ['Personnel', 'Secretaire']:
            param["COD_ETU"] = ''
            param["PROMO_IND"] = ''
        for key in param.keys():
            try:
                param[key] = param[key].decode("utf-8")
            except:
                try:
                    param[key] = param[key].decode("iso-8859-1")
                except:
                    pass
        session.add(tables.IndividuSQLITE(SESAME_ETU=sesame, DATE_NAI_IND=param["DATE_NAI_IND"], LIB_NOM_PAT_IND=param["LIB_NOM_PAT_IND"], LIB_NOM_USU_IND=param["LIB_NOM_USU_IND"], LIB_PR1_IND=param["LIB_PR1_IND"], TYPE_IND=param["TYPE_IND"], COD_ETU=param["COD_ETU"], EMAIL_ETU=param["EMAIL_ETU"], ADR1_IND=param["ADR1_IND"], ADR2_IND=param["ADR2_IND"], COD_POST_IND=param["COD_POST_IND"], VIL_IND=param["VIL_IND"], UNIV_IND=param["UNIV_IND"], PROMO_IND=param["PROMO_IND"], STATUS_IND="actif"))
        session.commit()
        return True
    return False


def setInfosUtilisateurs(session, param):
    for key in param.keys():
        param[key] = param[key].decode("utf-8")
        param[key] = param[key].replace("'", "&quot;")
    session.execute("update individu_lite set DATE_NAI_IND='%s', LIB_NOM_PAT_IND='%s', LIB_NOM_USU_IND='%s', LIB_PR1_IND='%s', TYPE_IND='%s', COD_ETU='%s', EMAIL_ETU='%s', ADR1_IND='%s', ADR2_IND='%s', COD_POST_IND='%s', VIL_IND='%s', UNIV_IND='%s', PROMO_IND='%s' where SESAME_ETU=='%s'" % (param["DATE_NAI_IND"], param["LIB_NOM_PAT_IND"], param["LIB_NOM_USU_IND"], param["LIB_PR1_IND"], param["TYPE_IND"], param["COD_ETU"], param["EMAIL_ETU"], param["ADR1_IND"], param["ADR2_IND"], param["COD_POST_IND"], param["VIL_IND"], param["UNIV_IND"], param["PROMO_IND"], param["SESAME_ETU"]))
    session.flush()
    session.commit()


def attacherELP(session, param):
    #liste = param['selected[]']
    #if not type(liste) == list:
    #    liste = [param['selected[]']]
    for elp in param["listeELP"]:
        codeElpFils = elp
        session.add(tables.ETPRegroupeELPSQLITE(COD_ELP_PERE=param["COD_ELP"], COD_ELP_FILS=codeElpFils, TYP_ELP=param['TYP_ELP_SELECT']))
    session.commit()


def sattacherAELP(session, param):
    #liste = param['selected[]']
    #if not type(liste) == list:
    #    liste = [param['selected[]']]
    for elp in param["listeTousELP"]:
        codeElpPere = elp
        session.add(tables.ETPRegroupeELPSQLITE(COD_ELP_PERE=codeElpPere, COD_ELP_FILS=param["COD_ELP"], TYP_ELP=param['TYP_ELP']))
    session.commit()


def detacherToutesELP(session, param):
    #liste = param['selected[]']
    #if not type(liste) == list:
    #    liste = [param['selected[]']]
    #for elp in liste:
    #    codeElpFils = elp
    session.execute("delete from etp_regroupe_elp_lite where COD_ELP_PERE=='%s' and TYP_ELP='%s'" % (param["COD_ELP"], param["TYP_ELP_SELECT"]))
    session.flush()
    session.commit()


def seDetacherToutesELP(session, param):
    #liste = param['selected[]']
    #if not type(liste) == list:
    #    liste = [param['selected[]']]
    #for elp in liste:
    #    codeElpPere = elp
    session.execute("delete from etp_regroupe_elp_lite where COD_ELP_FILS=='%s' and TYP_ELP='%s'" % (param["COD_ELP"], param["TYP_ELP"]))
    session.flush()
    session.commit()


def seDetacherDeELP(session, param):
    liste = param['selected[]']
    if not type(liste) == list:
        liste = [param['selected[]']]
    for elp in liste:
        codeElpPere = elp
    session.execute("delete from etp_regroupe_elp_lite where COD_ELP_FILS=='%s' and COD_ELP_PERE='%s'" % (param["COD_ELP"], codeElpPere))
    session.flush()
    session.commit()


def detacherELP(session, param):
    liste = param['selected[]']
    if not type(liste) == list:
        liste = [param['selected[]']]
    for elp in liste:
        codeElpFils = elp
    session.execute("delete from etp_regroupe_elp_lite where COD_ELP_PERE=='%s' and COD_ELP_FILS='%s'" % (param["COD_ELP"], codeElpFils))
    session.flush()
    session.commit()


def inscrireEnsResp(session, param):
    #session.execute("delete from ind_contrat_elp_lite where COD_ELP=='%s'" % param['COD_ELP'])
    try:
        session.add(tables.IndContratElpSQLITE(SESAME_ETU=param["rechercheEns"], COD_ELP=param["COD_ELP"], TYPE_ELP=param["TYP_ELP"], RESPONSABLE=True))
    except:
        session.execute("update ind_contrat_elp_lite set SESAME_ETU='%s' where COD_ELP=='%s' and RESPONSABLE=1" % (param["rechercheEns"], param["COD_ELP"]))
    session.flush()
    session.commit()


def inscrireEnseignant(session, param):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    nbInscrit = 0
    liste = param['username'].split(",")
    #if not type(liste) == list:
    #    liste = [param['selected[]']]
    for username in liste:
        session.add(tables.IndContratElpSQLITE(SESAME_ETU=username, COD_ELP=param["COD_ELP"], TYPE_ELP=param["TYP_ELP"]))
        nbInscrit += 1
    if nbInscrit:
        nbEns = session.query(ELP.ENS_ELP).filter(ELP.COD_ELP == param["COD_ELP"]).first()[0] + nbInscrit
        session.execute("update element_pedagogi_lite set ENS_ELP=%s where COD_ELP=='%s'" % (str(nbEns), param["COD_ELP"]))
        session.flush()
    session.flush()
    session.commit()


def inscrireEtudiant(session, param):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    nbInscrit = 0
    liste = param['username'].split(",")
    #liste = param['selected[]']
    #if not type(liste) == list:
    #    liste = [param['selected[]']]
    for username in liste:
        session.add(tables.IndContratElpSQLITE(SESAME_ETU=username, COD_ELP=param["COD_ELP"], TYPE_ELP=param["TYP_ELP"]))
        nbInscrit += 1
    if nbInscrit:
        nbEtu = session.query(ELP.ETU_ELP).filter(ELP.COD_ELP == param["COD_ELP"]).first()[0] + nbInscrit
        session.execute("update element_pedagogi_lite set ETU_ELP=%s where COD_ELP=='%s'" % (str(nbEtu), param["COD_ELP"]))
        session.flush()
    session.flush()
    session.commit()


def inscrireINDELP(session, SESAME_ETU, TYPE_ELP, LISTE_ELP):
    if not type(LISTE_ELP) == list:
        LISTE_ELP = [LISTE_ELP]
    for COD_ELP in LISTE_ELP:
        #individu = getIndividuLITE(session, SESAME_ETU)[0]
        #if individu["TYPE_IND"] == "Etudiant":
        inscrireEtudiant(session, {"username": SESAME_ETU, "TYP_ELP": TYPE_ELP, "COD_ELP": COD_ELP})
        #if individu["TYPE_IND"] == "Personnel":
        #    inscrireEnseignant(session, {"selected[]": [SESAME_ETU], "TYP_ELP": TYPE_ELP, "COD_ELP": COD_ELP})
        #if individu["TYPE_IND"] == "Secretaire":
        #    session.add(tables.IndContratElpSQLITE(SESAME_ETU=SESAME_ETU, COD_ELP=COD_ELP, TYPE_ELP=TYPE_ELP))
    session.flush()
    session.commit()


def desinscrireINDELP(session, SESAME_ETU, TYPE_ELP):
    session.execute("delete from ind_contrat_elp_lite where SESAME_ETU=='%s' and TYPE_ELP=='%s'" % (SESAME_ETU, TYPE_ELP))
    session.flush()
    session.commit()


"""
def desinscrireINDELP(session, SESAME_ETU, TYPE_ELP, LISTE_ELP):
    if not type(LISTE_ELP) == list:
        LISTE_ELP = [LISTE_ELP]
    for COD_ELP in LISTE_ELP:
        individu = getIndividuLITE(session, SESAME_ETU)[0]
        if individu["TYPE_IND"] == "Etudiant":
            desinscrireEtudiant(session, {"selected[]": [SESAME_ETU], "TYP_ELP": TYPE_ELP, "COD_ELP": COD_ELP})
        if individu["TYPE_IND"] == "Personnel":
            desinscrireEnseignant(session, {"selected[]": [SESAME_ETU], "TYP_ELP": TYPE_ELP, "COD_ELP": COD_ELP})
        if individu["TYPE_IND"] == "Secretaire":
            session.execute("delete from ind_contrat_elp_lite where SESAME_ETU=='%s' and COD_ELP=='%s' and TYPE_ELP=='%s'" % (SESAME_ETU, COD_ELP, TYPE_ELP))
    session.flush()
    session.commit()
"""


def desinscrireEnseignant(session, param):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    nbInscrit = 0
    for username in param["enseignants"]:
        session.execute("delete from ind_contrat_elp_lite where SESAME_ETU=='%s' and COD_ELP=='%s'" % (username, param['COD_ELP']))
        nbInscrit += 1
    if nbInscrit:
        nbEns = session.query(ELP.ENS_ELP).filter(ELP.COD_ELP == param["COD_ELP"]).first()[0] - nbInscrit
        session.execute("update element_pedagogi_lite set ENS_ELP=%s where COD_ELP=='%s'" % (str(nbEns), param["COD_ELP"]))
        session.flush()
    session.flush()
    session.commit()


def desinscrireEtudiant(session, param):
    ELP = aliased(tables.ElementPedagogiSQLITE)
    nbInscrit = 0
    #liste = param['selected[]']
    #if not type(liste) == list:
    #    liste = [param['selected[]']]
    for username in param["etudiants"]:
        session.execute("delete from ind_contrat_elp_lite where SESAME_ETU=='%s' and COD_ELP=='%s'" % (username, param['COD_ELP']))
        nbInscrit += 1
    if nbInscrit:
        nbEtu = session.query(ELP.ETU_ELP).filter(ELP.COD_ELP == param["COD_ELP"]).first()[0] - nbInscrit
        session.execute("update element_pedagogi_lite set ETU_ELP=%s where COD_ELP=='%s'" % (str(nbEtu), param["COD_ELP"]))
        session.flush()
    session.flush()
    session.commit()


def supprUtilisateur(session, param):
    session.execute("delete from individu_lite where SESAME_ETU=='%s'" % param['SESAME_ETU'])
    session.flush()
    session.commit()


def bloquerIND(session, param):
    session.execute("update individu_lite set STATUS_IND='closed' where SESAME_ETU=='%s'" % (param["SESAME_ETU"]))
    session.flush()
    session.commit()


def activerIND(session, param):
    session.execute("update individu_lite set STATUS_IND='actif' where SESAME_ETU=='%s'" % (param["SESAME_ETU"]))
    session.flush()
    session.commit()


def ajouterActuCours(session, param):
    session.add(tables.ActualitesCoursSQLITE(ID_COURS=param["ID_COURS"], TYPE_IND=param["TYPE_IND"], COD_ELP=param["COD_ELP"], TITRE_COURS=param["TITRE_COURS"], ACTU_COURS=param["ACTU_COURS"]))
    session.commit()


def insererConsultation(session, SESAME_ETU, DATE_CONS, ID_COURS, TYPE_CONS, ID_CONS):
    session.add(tables.ConsultationCoursSQLITE(SESAME_ETU=SESAME_ETU, DATE_CONS=DATE_CONS, ID_COURS=ID_COURS, TYPE_CONS=TYPE_CONS, ID_CONS=ID_CONS))
    session.commit()


def getConsultation(session):
    COC = aliased(tables.ConsultationCoursSQLITE)
    recherche = session.query(COC.SESAME_ETU, COC.DATE_CONS, COC.ID_COURS, COC.TYPE_CONS, COC.ID_CONS)
    return convertirResultatBDD(recherche.all())
