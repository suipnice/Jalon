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
    LOG.info("addConnexionIND")
    try:
        session.add(tables.ConnexionINDMySQL(SESAME_ETU=SESAME_ETU, DATE_CONN=DATE_CONN))
    except:
        LOG.info("Not addConnexionIND")
    session.commit()


#-------------------------------------#
# Interrogation de la base de données #
#-------------------------------------#
def getIndividu(session, sesame):
    IND = aliased(tables.IndividuMySQL)
    recherche = session.query(IND.LIB_NOM_PAT_IND, IND.LIB_NOM_USU_IND, IND.LIB_PR1_IND, IND.SESAME_ETU, IND.DATE_NAI_IND, IND.TYPE_IND, IND.COD_ETU, IND.EMAIL_ETU).filter(IND.SESAME_ETU == sesame)
    return convertirResultatBDD(recherche)
