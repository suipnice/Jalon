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
    # LOG.info("addConnexionIND")
    try:
        session.add(tables.ConnexionINDMySQL(SESAME_ETU=SESAME_ETU, DATE_CONN=DATE_CONN))
    except:
        # LOG.info("Not addConnexionIND")
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
    # LOG.info("----- getConsultationByCoursByMonth -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.PUBLIC_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", func.MONTH(COC.DATE_CONS) == month, func.YEAR(COC.DATE_CONS) == year)).group_by(COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByCoursByYear(session, ID_COURS, year='%'):
    # LOG.info("----- getConsultationByCoursByYear -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.PUBLIC_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", func.YEAR(COC.DATE_CONS) == year)).group_by(COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByCoursByUniversityYear(session, ID_COURS, year='%'):
    # LOG.info("----- getConsultationByCoursByUniversityYear -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.PUBLIC_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", COC.DATE_CONS.between("%s/09/01" % str(year - 1), "%s/08/31" % str(year)))).group_by(COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByCoursByYearForGraph(session, ID_COURS, year='%'):
    # LOG.info("----- getConsultationByCoursByYearForGraph -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(func.MONTH(COC.DATE_CONS), func.count(COC.DATE_CONS), COC.PUBLIC_CONS).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", func.YEAR(COC.DATE_CONS) == year)).group_by(func.MONTH(COC.DATE_CONS), COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByCoursByUniversityYearForGraph(session, ID_COURS, year):
    # LOG.info("----- getConsultationByCoursByUniversityYearForGraph -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(func.MONTH(COC.DATE_CONS), func.count(func.disctinct(COC.SESAME_ETU)), COC.PUBLIC_CONS).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", COC.DATE_CONS.between("%s/09/01" % str(year - 1), "%s/08/31" % str(year)))).group_by(func.MONTH(COC.DATE_CONS), COC.PUBLIC_CONS)
    #nbConsultations = session.query(func.MONTH(COC.DATE_CONS), func.count(COC.DATE_CONS), COC.PUBLIC_CONS).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", COC.DATE_CONS.between("%s/09/01" % str(year - 1), "%s/08/31" % str(year)))).group_by(func.MONTH(COC.DATE_CONS), COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByCoursByUniversityYearByDate(session, ID_COURS, DATE_CONS_YEAR, FILTER_DATE, PUBLIC_CONS):
    # LOG.info("----- getConsultationByCoursByUniversityYearByDate -----")
    COC = aliased(tables.ConsultationCoursMySQL)

    filter_date = func.MONTH(COC.DATE_CONS)
    if FILTER_DATE:
        filter_date = func.date(COC.DATE_CONS)

    if PUBLIC_CONS:
        nbConsultations = session.query(filter_date, func.count(func.distinct(COC.SESAME_ETU))).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", COC.PUBLIC_CONS == PUBLIC_CONS, COC.DATE_CONS.between("%s/09/01" % str(DATE_CONS_YEAR - 1), "%s/08/31" % str(DATE_CONS_YEAR)))).group_by(filter_date)
    else:
        nbConsultations = session.query(filter_date, func.count(func.distinct(COC.SESAME_ETU)), COC.PUBLIC_CONS).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", COC.DATE_CONS.between("%s/09/01" % str(DATE_CONS_YEAR - 1), "%s/08/31" % str(DATE_CONS_YEAR)))).group_by(filter_date, COC.PUBLIC_CONS)

    #nbConsultations = session.query(func.MONTH(COC.DATE_CONS), func.count(func.distinct(COC.SESAME_ETU)), COC.PUBLIC_CONS).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", COC.DATE_CONS.between("%s/09/01" % str(year - 1), "%s/08/31" % str(year)))).group_by(func.MONTH(COC.DATE_CONS), COC.PUBLIC_CONS)
    #nbConsultations = session.query(func.MONTH(COC.DATE_CONS), func.count(COC.DATE_CONS), COC.PUBLIC_CONS).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", COC.DATE_CONS.between("%s/09/01" % str(year - 1), "%s/08/31" % str(year)))).group_by(func.MONTH(COC.DATE_CONS), COC.PUBLIC_CONS)

    return nbConsultations


def getFrequentationByCoursByUniversityYearByDateForGraph(session, ID_COURS, PUBLIC_CONS, DATE_CONS_YEAR):
    # LOG.info("----- getFrequentationByCoursByUniversityYearByDateForGraph -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(func.date(COC.DATE_CONS), func.count(func.distinct(COC.SESAME_ETU))).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", COC.PUBLIC_CONS == PUBLIC_CONS, COC.DATE_CONS.between("%s/09/01" % str(DATE_CONS_YEAR - 1), "%s/08/31" % str(DATE_CONS_YEAR)))).group_by(func.date(COC.DATE_CONS))
    #nbConsultations = session.query(func.date(COC.DATE_CONS), func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.TYPE_CONS == "Cours", COC.PUBLIC_CONS == PUBLIC_CONS, COC.DATE_CONS.between("%s/09/01" % str(DATE_CONS_YEAR - 1), "%s/08/31" % str(DATE_CONS_YEAR)))).group_by(func.date(COC.DATE_CONS))
    return nbConsultations


def getConsultationByElementsByCoursByMonth(session, ID_COURS, month, year='%', elements_list=[]):
    # LOG.info("----- getConsultationByElementsByCoursByMonth -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.ID_CONS, func.count(COC.DATE_CONS), func.count(func.distinct(COC.SESAME_ETU))).filter(and_(COC.ID_COURS == ID_COURS, COC.PUBLIC_CONS.in_(["Etudiant", "Lecteur"]), COC.ID_CONS.in_(elements_list), func.MONTH(COC.DATE_CONS) == month, func.YEAR(COC.DATE_CONS) == year)).group_by(COC.ID_CONS)
    return nbConsultations


def getConsultationByElementsByCoursByYear(session, ID_COURS, year, elements_list=[]):
    # LOG.info("----- getConsultationByElementsByCoursByYear -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.ID_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS.in_(elements_list), func.YEAR(COC.DATE_CONS) == year)).group_by(COC.ID_CONS)
    return nbConsultations


def getConsultationByElementsByCoursByUniversityYear(session, ID_COURS, year, elements_list=[]):
    # LOG.info("----- getConsultationByElementsByCoursByUniversityYear -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.ID_CONS, func.count(COC.DATE_CONS), func.count(func.distinct(COC.SESAME_ETU))).filter(and_(COC.ID_COURS == ID_COURS, COC.PUBLIC_CONS.in_(["Etudiant", "Lecteur"]), COC.ID_CONS.in_(elements_list), COC.DATE_CONS.between("%s/09/01" % str(year - 1), "%s/08/31" % str(year)))).group_by(COC.ID_CONS)
    return nbConsultations


def getConsultationByElementByCoursByMonth(session, ID_COURS, ID_CONS, month, year='%'):
    # LOG.info("----- getConsultationByElementsByCoursByMonth -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.PUBLIC_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS == ID_CONS, func.MONTH(COC.DATE_CONS) == month, func.YEAR(COC.DATE_CONS) == year)).group_by(COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByElementByCoursByYear(session, ID_COURS, ID_CONS, year='%'):
    # LOG.info("----- getConsultationByElementsByCoursByYear -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.PUBLIC_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS == ID_CONS, func.YEAR(COC.DATE_CONS) == year)).group_by(COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByElementByCoursByUniversityYear(session, ID_COURS, ID_CONS, year):
    # LOG.info("----- getConsultationByElementByCoursByUniversityYear -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(COC.PUBLIC_CONS, func.count(COC.DATE_CONS)).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS == ID_CONS, COC.DATE_CONS.between("%s/09/01" % str(year - 1), "%s/08/31" % str(year)))).group_by(COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByElementByCoursByYearForGraph(session, ID_COURS, ID_CONS, year='%'):
    # LOG.info("----- getConsultationByElementByCoursByYearForGraph -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(func.MONTH(COC.DATE_CONS), func.count(COC.DATE_CONS), COC.PUBLIC_CONS).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS == ID_CONS, func.YEAR(COC.DATE_CONS) == year)).group_by(func.MONTH(COC.DATE_CONS), COC.PUBLIC_CONS)
    return nbConsultations


def getConsultationByElementByCoursByUniversityYearForGraph(session, ID_COURS, ID_CONS, year='%'):
    # LOG.info("----- getConsultationByElementByCoursByUniversityYearForGraph -----")
    COC = aliased(tables.ConsultationCoursMySQL)
    nbConsultations = session.query(func.MONTH(COC.DATE_CONS), func.count(COC.DATE_CONS), COC.PUBLIC_CONS).filter(and_(COC.ID_COURS == ID_COURS, COC.ID_CONS == ID_CONS, COC.DATE_CONS.between("%s/09/01" % str(year - 1), "%s/08/31" % str(year)))).group_by(func.MONTH(COC.DATE_CONS), COC.PUBLIC_CONS)
    return nbConsultations


#--------------------------#
# Évaluation par les pairs #
#--------------------------#
def setEvaluatePeer(session, DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, CRITERIA, CRITERIA_DATE, CRITERIA_NOTE, CRITERIA_COMMENT):
    PE = aliased(tables.PeersEvaluationMySQL)
    for line in session.query(PE).filter(PE.DEPOSIT_BOX == DEPOSIT_BOX, PE.DEPOSIT_STU == DEPOSIT_STU, PE.CORRECTED_STU == CORRECTED_STU, PE.CRITERIA == CRITERIA):
        line.FOR_AVG = False
    session.commit()
    session.add(tables.PeersEvaluationMySQL(DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, CRITERIA, CRITERIA_DATE, CRITERIA_NOTE, CRITERIA_COMMENT))
    session.commit()


def deletePeersEvaluation(session, DEPOSIT_BOX):
    session.execute("delete from peers_evaluation_average_mysql where DEPOSIT_BOX='%s'" % DEPOSIT_BOX)
    session.execute("delete from peers_average_mysql where DEPOSIT_BOX='%s'" % DEPOSIT_BOX)
    session.execute("delete from peers_self_evaluation_note_mysql where DEPOSIT_BOX='%s'" % DEPOSIT_BOX)
    session.execute("delete from peers_self_evaluation_mysql where DEPOSIT_BOX='%s'" % DEPOSIT_BOX)
    session.execute("delete from peers_evaluation_note_mysql where DEPOSIT_BOX='%s'" % DEPOSIT_BOX)
    session.execute("delete from peers_evaluation_mysql where DEPOSIT_BOX='%s'" % DEPOSIT_BOX)
    session.flush()
    session.commit()


def setSelfEvaluate(session, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_DATE, CRITERIA_NOTE, CRITERIA_COMMENT):
    session.add(tables.PeersSelfEvaluationMySQL(DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_DATE, CRITERIA_NOTE, CRITERIA_COMMENT))
    session.commit()


def getSelfEvaluate(session, DEPOSIT_BOX, DEPOSIT_STU):
    PSE = aliased(tables.PeersSelfEvaluationMySQL)
    self_evaluation = session.query(PSE.CRITERIA, PSE.CRITERIA_NOTE, PSE.CRITERIA_COMMENT).filter(PSE.DEPOSIT_BOX == DEPOSIT_BOX, PSE.DEPOSIT_STU == DEPOSIT_STU)
    return self_evaluation


def setPeerEvaluationNote(session, DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, NOTE):
    insert = True
    PEN = aliased(tables.PeersEvaluationNoteMySQL)
    note_list = session.query(PEN).filter(PEN.DEPOSIT_BOX == DEPOSIT_BOX, PEN.DEPOSIT_STU == DEPOSIT_STU, PEN.CORRECTED_STU == CORRECTED_STU)
    for line in note_list:
        line.NOTE = NOTE
        insert = False
    if insert:
        session.add(tables.PeersEvaluationNoteMySQL(DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, NOTE))
    session.commit()


def setSelfEvaluationNote(session, DEPOSIT_BOX, DEPOSIT_STU, NOTE):
    session.add(tables.PeersSelfEvaluationNoteMySQL(DEPOSIT_BOX, DEPOSIT_STU, NOTE))
    session.commit()


def getSelfEvaluationNote(session, DEPOSIT_BOX, DEPOSIT_STU):
    PSEN = aliased(tables.PeersSelfEvaluationNoteMySQL)
    peer_evaluation = session.query(PSEN.NOTE).filter(PSEN.DEPOSIT_BOX == DEPOSIT_BOX, PSEN.DEPOSIT_STU == DEPOSIT_STU)
    return peer_evaluation


def getPeerEvaluation(session, DEPOSIT_BOX, DEPOSIT_STU):
    PE = aliased(tables.PeersEvaluationMySQL)
    peer_evaluation = session.query(PE.CRITERIA, PE.CORRECTED_STU, PE.CRITERIA_NOTE, PE.CRITERIA_COMMENT).filter(PE.DEPOSIT_BOX == DEPOSIT_BOX, PE.DEPOSIT_STU == DEPOSIT_STU, PE.FOR_AVG == 1)
    #return convertirResultatBDD(peer_evaluation)
    return peer_evaluation


def getPeerEvaluationsNotes(session, DEPOSIT_BOX, CORRECTED_STU):
    PEN = aliased(tables.PeersEvaluationNoteMySQL)
    peer_evaluations_notes = session.query(PEN.DEPOSIT_STU, PEN.NOTE).filter(PEN.DEPOSIT_BOX == DEPOSIT_BOX, PEN.CORRECTED_STU == CORRECTED_STU)
    #return convertirResultatBDD(peer_evaluation)
    return peer_evaluations_notes


def getPeerAverage(session, DEPOSIT_BOX, DEPOSIT_STU):
    PA = aliased(tables.PeersAverageMySQL)
    peer_average = session.query(PA.CRITERIA, PA.CRITERIA_AVERAGE, PA.CRITERIA_CODE, PA.CRITERIA_VALUE, PA.CRITERIA_NOTE_T, PA.CRITERIA_COMMENT_T).filter(PA.DEPOSIT_BOX == DEPOSIT_BOX, PA.DEPOSIT_STU == DEPOSIT_STU)
    #return convertirResultatBDD(peer_evaluation)
    return peer_average


def getCriteriaAverage(session, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA):
    PA = aliased(tables.PeersAverageMySQL)
    criteria_average = session.query(PA.CRITERIA_AVERAGE, PA.CRITERIA_CODE).filter(PA.DEPOSIT_BOX == DEPOSIT_BOX, PA.DEPOSIT_STU == DEPOSIT_STU, PA.CRITERIA == CRITERIA)
    return criteria_average


def getEvaluationByCorrectedSTU(session, DEPOSIT_BOX, CORRECTED_STU):
    PE = aliased(tables.PeersEvaluationMySQL)
    peers_evaluations = session.query(PE.CRITERIA, PE.DEPOSIT_STU, PE.CRITERIA_NOTE_FIRST, PE.CRITERIA_COMMENT_FIRST).filter(PE.DEPOSIT_BOX == DEPOSIT_BOX, PE.CORRECTED_STU == CORRECTED_STU)
    #return convertirResultatBDD(peer_evaluation)
    return peers_evaluations


def getEvaluationByCorrectedAndDepositSTU(session, DEPOSIT_BOX, CORRECTED_STU, DEPOSIT_STU):
    PE = aliased(tables.PeersEvaluationMySQL)
    criteria_evaluated_list = session.query(PE.CRITERIA, PE.CRITERIA_NOTE, PE.CRITERIA_COMMENT).filter(PE.DEPOSIT_BOX == DEPOSIT_BOX, PE.CORRECTED_STU == CORRECTED_STU, PE.DEPOSIT_STU == DEPOSIT_STU, PE.FOR_AVG == 1)
    #return convertirResultatBDD(peer_evaluation)
    return criteria_evaluated_list


def generatePeersAverage(session, DEPOSIT_BOX):
    PE = aliased(tables.PeersEvaluationMySQL)
    peers_average = session.query(PE.DEPOSIT_STU, PE.CRITERIA, func.avg(PE.CRITERIA_NOTE).label("CRITERIA_AVG"), func.count(PE.CRITERIA_NOTE), func.min(PE.CRITERIA_NOTE).label("NOTE_MIN"), func.max(PE.CRITERIA_NOTE).label("MAX")).filter(PE.DEPOSIT_BOX == DEPOSIT_BOX, PE.FOR_AVG == 1).group_by(PE.DEPOSIT_STU, PE.CRITERIA)
    #return convertirResultatBDD(peers_average)
    return peers_average


def generateEvaluationsAverage(session, DEPOSIT_BOX):
    PEN = aliased(tables.PeersEvaluationNoteMySQL)
    peers_average = session.query(PEN.DEPOSIT_STU, func.avg(PEN.NOTE).label("CRITERIA_AVG")).filter(PEN.DEPOSIT_BOX == DEPOSIT_BOX).group_by(PEN.DEPOSIT_STU)
    #return convertirResultatBDD(peers_average)
    return peers_average


def setAveragePeer(session, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_CODE, CRITERIA_VALUE, CRITERIA_DATE, CRITERIA_AVERAGE, CRITERIA_NOTE_T, CRITERIA_COMMENT_T):
    session.add(tables.PeersAverageMySQL(DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_CODE, CRITERIA_VALUE, CRITERIA_DATE, CRITERIA_AVERAGE, CRITERIA_NOTE_T, CRITERIA_COMMENT_T))
    session.commit()


def updateAveragePeer(session, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_CODE, CRITERIA_VALUE, CRITERIA_DATE, CRITERIA_AVERAGE, CRITERIA_NOTE_T, CRITERIA_COMMENT_T):
    PA = aliased(tables.PeersAverageMySQL)
    peer_average = session.query(PA).filter(PA.DEPOSIT_BOX == DEPOSIT_BOX, PA.DEPOSIT_STU == DEPOSIT_STU, PA.CRITERIA == CRITERIA)
    for line in peer_average:
        line.CRITERIA_CODE = CRITERIA_CODE
        line.CRITERIA_VALUE = CRITERIA_VALUE
        line.CRITERIA_AVERAGE = CRITERIA_AVERAGE
        line.CRITERIA_NOTE_T = CRITERIA_NOTE_T
        line.CRITERIA_COMMENT_T = CRITERIA_COMMENT_T
    session.commit()


def deleteAverageByDepositBox(session, DEPOSIT_BOX):
    session.execute("delete from peers_average_mysql where DEPOSIT_BOX='%s'" % DEPOSIT_BOX)
    session.flush()
    session.commit()


def setEvaluationAverage(session, DEPOSIT_BOX, DEPOSIT_STU, AVERAGE, IS_VERIFICATION):
    session.add(tables.PeersEvaluationAverageMySQL(DEPOSIT_BOX, DEPOSIT_STU, AVERAGE, IS_VERIFICATION))
    session.commit()


def updateEvaluationAverage(session, DEPOSIT_BOX, DEPOSIT_STU, AVERAGE, IS_VERIFICATION):
    PEA = aliased(tables.PeersEvaluationAverageMySQL)
    peer_average = session.query(PEA).filter(PEA.DEPOSIT_BOX == DEPOSIT_BOX, PEA.DEPOSIT_STU == DEPOSIT_STU)
    for line in peer_average:
        line.AVERAGE = AVERAGE
        line.IS_VERIFICATION = IS_VERIFICATION
    session.commit()


def deleteEvaluationsAverageByDepositBox(session, DEPOSIT_BOX):
    session.execute("delete from peers_evaluation_average_mysql where DEPOSIT_BOX='%s'" % DEPOSIT_BOX)
    session.flush()
    session.commit()


def getPeersAverage(session, DEPOSIT_BOX):
    PA = aliased(tables.PeersAverageMySQL)
    peers_average = session.query(PA.DEPOSIT_STU, PA.CRITERIA, PA.CRITERIA_CODE, PA.CRITERIA_VALUE, PA.CRITERIA_AVERAGE, PA.CRITERIA_NOTE_T, PA.CRITERIA_COMMENT_T).filter(PA.DEPOSIT_BOX == DEPOSIT_BOX)
    #return convertirResultatBDD(peers_average)
    return peers_average


def getCountEvaluationsNotes(session, DEPOSIT_BOX):
    PEA = aliased(tables.PeersEvaluationAverageMySQL)
    evaluations_notes = session.query(func.count(PEA.DEPOSIT_STU)).filter(PEA.DEPOSIT_BOX == DEPOSIT_BOX)
    #return convertirResultatBDD(peers_average)
    return evaluations_notes


def getCountVerifEvaluationsNotes(session, DEPOSIT_BOX):
    PEA = aliased(tables.PeersEvaluationAverageMySQL)
    verif_evaluations_notes = session.query(func.count(PEA.DEPOSIT_STU)).filter(PEA.DEPOSIT_BOX == DEPOSIT_BOX, PEA.IS_VERIFICATION == True)
    # LOG.info("***** getCountVerifEvaluationsNotes : %s" % verif_evaluations_notes)
    #return convertirResultatBDD(peers_average)
    return verif_evaluations_notes


def getInfoEvaluationsNotes(session, DEPOSIT_BOX):
    PEA = aliased(tables.PeersEvaluationAverageMySQL)
    evaluations_notes = session.query(func.min(PEA.AVERAGE), func.max(PEA.AVERAGE), func.avg(PEA.AVERAGE)).filter(PEA.DEPOSIT_BOX == DEPOSIT_BOX)
    #return convertirResultatBDD(peers_average)
    return evaluations_notes


def getInfoCriteriaNotes(session, DEPOSIT_BOX):
    PA = aliased(tables.PeersAverageMySQL)
    evaluations_notes = session.query(PA.CRITERIA, func.min(PA.CRITERIA_AVERAGE), func.max(PA.CRITERIA_AVERAGE), func.avg(PA.CRITERIA_AVERAGE)).filter(PA.DEPOSIT_BOX == DEPOSIT_BOX).group_by(PA.CRITERIA)
    #return convertirResultatBDD(peers_average)
    return evaluations_notes


def getInfoCriteriaNoteByDepositStu(session, DEPOSIT_BOX, CHECK=None):
    PA = aliased(tables.PeersAverageMySQL)
    if not CHECK:
        evaluations_notes = session.query(PA.DEPOSIT_STU, PA.CRITERIA, PA.CRITERIA_AVERAGE, PA.CRITERIA_CODE).filter(PA.DEPOSIT_BOX == DEPOSIT_BOX)
    else:
        if CHECK != 1:
            evaluations_notes = session.query(PA.DEPOSIT_STU, PA.CRITERIA, PA.CRITERIA_AVERAGE, PA.CRITERIA_CODE).filter(PA.DEPOSIT_BOX == DEPOSIT_BOX, PA.CRITERIA_CODE <> 1)
        if CHECK == 1:
            evaluations_notes = session.query(PA.DEPOSIT_STU, PA.CRITERIA, PA.CRITERIA_AVERAGE, PA.CRITERIA_CODE).filter(PA.DEPOSIT_BOX == DEPOSIT_BOX, PA.CRITERIA_CODE == 1)
    return evaluations_notes


def getInfoEvaluationNoteByDepositStu(session, DEPOSIT_BOX, CHECK=None):
    PEA = aliased(tables.PeersEvaluationAverageMySQL)
    if not CHECK:
        evaluations_notes = session.query(PEA.DEPOSIT_STU, PEA.AVERAGE, PEA.IS_VERIFICATION).filter(PEA.DEPOSIT_BOX == DEPOSIT_BOX)
    else:
        if CHECK == 1:
            evaluations_notes = session.query(PEA.DEPOSIT_STU, PEA.AVERAGE, PEA.IS_VERIFICATION).filter(PEA.DEPOSIT_BOX == DEPOSIT_BOX, PEA.IS_VERIFICATION == False)
        if CHECK != 1:
            evaluations_notes = session.query(PEA.DEPOSIT_STU, PEA.AVERAGE, PEA.IS_VERIFICATION).filter(PEA.DEPOSIT_BOX == DEPOSIT_BOX, PEA.IS_VERIFICATION == True)
    return evaluations_notes


def getEvaluationNoteByDeposiSTU(session, DEPOSIT_BOX, DEPOSIT_STU):
    PEA = aliased(tables.PeersEvaluationAverageMySQL)
    evaluation_note = session.query(PEA.AVERAGE).filter(PEA.DEPOSIT_BOX == DEPOSIT_BOX, PEA.DEPOSIT_STU == DEPOSIT_STU)
    return evaluation_note
