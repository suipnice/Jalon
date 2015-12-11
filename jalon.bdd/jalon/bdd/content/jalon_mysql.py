# -*- coding: utf-8 -*-
import tables

# SQL Alchemy
from sqlalchemy import and_
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased


# Messages de debug :
from logging import getLogger
LOG = getLogger('[jalon_mysql]')


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
# Modification de la base de données  #
#-------------------------------------#
def addIndividu(session, param):
    sesame = param["SESAME_ETU"].replace(" ", "")
    individu = getIndividu(session, sesame)
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
        session.add(tables.IndividuMySQL(SESAME_ETU=sesame, DATE_NAI_IND=param["DATE_NAI_IND"], LIB_NOM_PAT_IND=param["LIB_NOM_PAT_IND"], LIB_NOM_USU_IND=param["LIB_NOM_USU_IND"], LIB_PR1_IND=param["LIB_PR1_IND"], TYPE_IND=param["TYPE_IND"], COD_ETU=param["COD_ETU"], EMAIL_ETU=param["EMAIL_ETU"]))
        session.commit()
        return True
    return False


def addConnexionIND(session, SESAME_ETU, DATE_CONN):
    #LOG.info("addConnexionIND")
    try:
        session.add(tables.ConnexionINDMySQL(SESAME_ETU=SESAME_ETU, DATE_CONN=DATE_CONN))
    except:
        #LOG.info("Not addConnexionIND")
        pass
    session.commit()


def addConsultationIND(session, SESAME_ETU, DATE_CONS, ID_COURS, TYPE_CONS, ID_CONS, PUBLIC_CONS):
    session.add(tables.ConsultationCoursMySQL(SESAME_ETU=SESAME_ETU, DATE_CONS=DATE_CONS, ID_COURS=ID_COURS, TYPE_CONS=TYPE_CONS, ID_CONS=ID_CONS, PUBLIC_CONS=PUBLIC_CONS))
    session.commit()


#-------------------------------------#
# Interrogation de la base de données #
#-------------------------------------#
def getIndividu(session, sesame):
    IND = aliased(tables.IndividuMySQL)
    recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_NOM_USU_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.DATE_NAI_IND, IND.TYPE_IND, IND.COD_ETU, IND.EMAIL_ETU).filter(IND.SESAME_ETU == sesame)
    return convertirResultatBDD(recherche)


#----------------------------#
# Interrogation statistique  #
#----------------------------#
def getConnexionELPByMonth(session, COD_ELP, month, year, listeInds):
    CI = aliased(tables.ConnexionINDMySQL)
    nbConnexion = session.query(CI.SESAME_ETU).filter(and_(CI.SESAME_ETU.in_(listeInds), func.MONTH(CI.DATE_CONN) == month, func.YEAR(CI.DATE_CONN) == year))
    return nbConnexion.count()


def getConnexionELPByYear(session, COD_ELP, year, listeInds):
    CI = aliased(tables.ConnexionINDMySQL)
    nbConnexion = session.query(CI.SESAME_ETU, CI.DATE_CONN).filter(and_(CI.SESAME_ETU.in_(listeInds), func.YEAR(CI.DATE_CONN) == year))
    return nbConnexion


def getConnexionELPByMonthByIND(session, COD_ELP, month, year, listeInds):
    CI = aliased(tables.ConnexionINDMySQL)
    nbConnexion = session.query(CI.SESAME_ETU, func.count(CI.DATE_CONN)).filter(and_(CI.SESAME_ETU.in_(listeInds), func.MONTH(CI.DATE_CONN) == month, func.YEAR(CI.DATE_CONN) == year)).group_by(CI.SESAME_ETU)
    return nbConnexion


def getConnexionELPByYearByIND(session, COD_ELP, year, listeInds):
    CI = aliased(tables.ConnexionINDMySQL)
    nbConnexion = session.query(CI.SESAME_ETU, func.count(CI.DATE_CONN)).filter(and_(CI.SESAME_ETU.in_(listeInds), func.YEAR(CI.DATE_CONN) == year)).group_by(CI.SESAME_ETU)
    return nbConnexion


def getMinMaxYearByELP(session, COD_ELP, listeInds):
    retour = {"min": 0, "max": 0, "ecart": 0}
    CI = aliased(tables.ConnexionINDMySQL)
    minMaxYear = session.query(func.distinct(CI.DATE_CONN)).filter(CI.SESAME_ETU.in_(listeInds)).order_by(CI.DATE_CONN)
    if minMaxYear:
        retour["min"] = minMaxYear[0][0].year
        retour["max"] = minMaxYear[-1][0].year
        retour["ecart"] = retour["max"] - retour["min"]
    return retour


def getConnexionByIND(session, SESAME_ETU):
    CI = aliased(tables.ConnexionINDMySQL)
    nbConnexion = session.query(CI.DATE_CONN).filter(CI.SESAME_ETU == SESAME_ETU)
    return nbConnexion


def getConsultationCoursByMonth(session, month, year='%', listeIdCours=[], SESAME_ETU=None):
    COC = aliased(tables.ConsultationCoursMySQL)
    if SESAME_ETU:
        nbConsultations = session.query(COC.ID_COURS, func.count(COC.DATE_CONS)).filter(and_(COC.SESAME_ETU == SESAME_ETU, COC.ID_COURS.in_(listeIdCours), func.MONTH(COC.DATE_CONS) == month, func.YEAR(COC.DATE_CONS) == year)).group_by(COC.ID_COURS)
    else:
        nbConsultations = session.query(COC.ID_COURS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS.in_(listeIdCours), func.MONTH(COC.DATE_CONS) == month, func.YEAR(COC.DATE_CONS) == year)).group_by(COC.ID_COURS)
    return nbConsultations


def getConsultationCoursByYear(session, year='%', listeIdCours=[], SESAME_ETU=None):
    COC = aliased(tables.ConsultationCoursMySQL)
    if SESAME_ETU:
        nbConsultations = session.query(COC.ID_COURS, func.count(COC.DATE_CONS)).filter(and_(COC.SESAME_ETU == SESAME_ETU, COC.ID_COURS.in_(listeIdCours), func.YEAR(COC.DATE_CONS) == year)).group_by(COC.ID_COURS)
    else:
        nbConsultations = session.query(COC.ID_COURS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS.in_(listeIdCours), func.YEAR(COC.DATE_CONS) == year)).group_by(COC.ID_COURS)
    return nbConsultations


def getConsultationByCoursByMonth(session, ID_COURS, month, year='%'):
    #LOG.info("----- getConsultationByCoursByMonth -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.PUBLIC_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", func.MONTH(COC.DATE_CONS) == month, func.YEAR(COC.DATE_CONS) == year)).group_by(COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByCoursByYear(session, ID_COURS, year='%'):
    #LOG.info("----- getConsultationByCoursByYear -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.PUBLIC_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", func.YEAR(COC.DATE_CONS) == year)).group_by(COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByCoursByYearForGraph(session, ID_COURS, year='%'):
    #LOG.info("----- getConsultationByCoursByYearForGraph -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(func.MONTH(COC.DATE_CONS), func.count(COC.DATE_CONS), COC.PUBLIC_CONS).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", func.YEAR(COC.DATE_CONS) == year)).group_by(func.MONTH(COC.DATE_CONS), COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByElementsByCoursByMonth(session, ID_COURS, month, year='%', elements_list=[]):
    #LOG.info("----- getConsultationByElementsByCoursByMonth -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.ID_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS.in_(elements_list), func.MONTH(COC.DATE_CONS) == month, func.YEAR(COC.DATE_CONS) == year)).group_by(COC.ID_CONS)
    return nbConsultations


def getConsultationByElementsByCoursByYear(session, ID_COURS, year='%', elements_list=[]):
    #LOG.info("----- getConsultationByElementsByCoursByYear -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.ID_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS.in_(elements_list), func.YEAR(COC.DATE_CONS) == year)).group_by(COC.ID_CONS)
    return nbConsultations


def getConsultationByElementByCoursByMonth(session, ID_COURS, ID_CONS, month, year='%'):
    #LOG.info("----- getConsultationByElementsByCoursByMonth -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.PUBLIC_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS == ID_CONS, func.MONTH(COC.DATE_CONS) == month, func.YEAR(COC.DATE_CONS) == year)).group_by(COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByElementByCoursByYear(session, ID_COURS, ID_CONS, year='%'):
    #LOG.info("----- getConsultationByElementsByCoursByYear -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.PUBLIC_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS == ID_CONS, func.YEAR(COC.DATE_CONS) == year)).group_by(COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByElementByCoursByYearForGraph(session, ID_COURS, ID_CONS, year='%'):
    #LOG.info("----- getConsultationByElementByCoursByYearForGraph -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(func.MONTH(COC.DATE_CONS), func.count(COC.DATE_CONS), COC.PUBLIC_CONS).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS == ID_CONS, func.YEAR(COC.DATE_CONS) == year)).group_by(func.MONTH(COC.DATE_CONS), COC.PUBLIC_CONS)
    return nbConsultations
