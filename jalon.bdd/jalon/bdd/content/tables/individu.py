# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text

Base = declarative_base()


class Individu(Base):
    __tablename__ = "individu"

    COD_IND = Column(Integer, primary_key=True)
    DATE_NAI_IND = Column(String(10))
    LIB_NOM_PAT_IND = Column(String(30))
    LIB_NOM_USU_IND = Column(String(30))
    LIB_PR1_IND = Column(String(20))
    COD_ETU = Column(Integer)
    LIB_VIL_NAI_ETU = Column(String(20))

    def __init__(self, COD_IND=None):
        self.COD_IND = COD_IND

    def __repr__(self):
        return "<Individu COD_IND=%s>" % str(self.COD_IND)


class IndividuSQLITE(Base):
    __tablename__ = "individu_lite"

    SESAME_ETU = Column(Text, primary_key=True)
    DATE_NAI_IND = Column(Text)
    LIB_NOM_PAT_IND = Column(Text)
    LIB_NOM_USU_IND = Column(Text)
    LIB_PR1_IND = Column(Text)
    TYPE_IND = Column(Text)
    COD_ETU = Column(Integer)
    EMAIL_ETU = Column(Text)
    ADR1_IND = Column(Text)
    ADR2_IND = Column(Text)
    COD_POST_IND = Column(Text)
    VIL_IND = Column(Text)
    UNIV_IND = Column(Text)
    PROMO_IND = Column(Text)
    STATUS_IND = Column(Text)

    def __init__(self, SESAME_ETU=None, COD_ETU=0, DATE_NAI_IND=None, LIB_NOM_USU_IND=None, LIB_NOM_PAT_IND=None, LIB_PR1_IND=None, TYPE_IND=None, EMAIL_ETU=None, ADR1_IND=None, ADR2_IND=None, COD_POST_IND=None, VIL_IND=None, UNIV_IND=None, PROMO_IND=None, STATUS_IND=None):
        self.SESAME_ETU = SESAME_ETU
        self.COD_ETU = COD_ETU
        self.DATE_NAI_IND = DATE_NAI_IND
        self.LIB_NOM_USU_IND = LIB_NOM_USU_IND
        self.LIB_NOM_PAT_IND = LIB_NOM_PAT_IND
        self.LIB_PR1_IND = LIB_PR1_IND
        self.TYPE_IND = TYPE_IND
        self.EMAIL_ETU = EMAIL_ETU
        self.ADR1_IND = ADR1_IND
        self.ADR2_IND = ADR2_IND
        self.COD_POST_IND = COD_POST_IND
        self.VIL_IND = VIL_IND
        self.UNIV_IND = UNIV_IND
        self.PROMO_IND = PROMO_IND
        self.STATUS_IND = STATUS_IND

    def __repr__(self):
        return "<Individu SESAME_ETU=%s COD_ETU=%s DATE_NAI_IND=%s LIB_NOM_USU_IND=%s LIB_NOM_PAT_IND=%s LIB_PR1_IND=%s TYPE_IND=%s EMAIL_ETU=%s>" % (self.SESAME_ETU, str(self.COD_ETU), self.DATE_NAI_IND, self.LIB_NOM_USU_IND, self.LIB_NOM_PAT_IND, self.LIB_PR1_IND, self.TYPE_IND, self.EMAIL_ETU)


class IndividuMySQL(Base):
    __tablename__ = "individu_mysql"

    SESAME_ETU = Column(String(50), primary_key=True)
    COD_ETU = Column(Integer)
    DATE_NAI_IND = Column(String(10))
    LIB_NOM_PAT_IND = Column(String(100))
    LIB_NOM_USU_IND = Column(String(100))
    LIB_PR1_IND = Column(String(100))
    TYPE_IND = Column(String(50))
    EMAIL_ETU = Column(String(50))

    def __init__(self, SESAME_ETU=None, COD_ETU=0, DATE_NAI_IND=None, LIB_NOM_USU_IND=None, LIB_NOM_PAT_IND=None, LIB_PR1_IND=None, TYPE_IND=None, EMAIL_ETU=None):
        self.SESAME_ETU = SESAME_ETU
        self.COD_ETU = COD_ETU
        self.DATE_NAI_IND = DATE_NAI_IND
        self.LIB_NOM_USU_IND = LIB_NOM_USU_IND
        self.LIB_NOM_PAT_IND = LIB_NOM_PAT_IND
        self.LIB_PR1_IND = LIB_PR1_IND
        self.TYPE_IND = TYPE_IND
        self.EMAIL_ETU = EMAIL_ETU

    def __repr__(self):
        return "<Individu SESAME_ETU=%s COD_ETU=%s DATE_NAI_IND=%s LIB_NOM_USU_IND=%s LIB_NOM_PAT_IND=%s LIB_PR1_IND=%s TYPE_IND=%s EMAIL_ETU=%s>" % (self.SESAME_ETU, str(self.COD_ETU), self.DATE_NAI_IND, self.LIB_NOM_USU_IND, self.LIB_NOM_PAT_IND, self.LIB_PR1_IND, self.TYPE_IND, self.EMAIL_ETU)
