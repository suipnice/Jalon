# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Integer

Base = declarative_base()


class ElementPedagogi(Base):
    __tablename__ = "element_pedagogi"

    COD_ELP = Column(String(8), primary_key=True)
    LIB_ELP = Column(String(60))
    ETA_ELP = Column(String(1))

    def __init__(self, COD_ETP=None, COD_VRS_VET=None):
        self.COD_ETP = COD_ETP
        self.COD_VRS_VET = COD_VRS_VET

    def __repr__(self):
        return "<ElementPedagogi COD_ETP=%d COD_VRS_VET=%s>" % (self.COD_ETP, self.COD_VRS_VET)


class ElementPedagogiSQLITE(Base):
    __tablename__ = "element_pedagogi_lite"

    COD_ELP = Column(Text, primary_key=True)
    LIB_ELP = Column(Text)
    TYP_ELP = Column(Text)
    COD_GPE = Column(Text)
    ETU_ELP = Column(Integer)
    ENS_ELP = Column(Integer)
    DATE_CREATION = Column(Text)
    DATE_MODIF = Column(Text)

    def __init__(self, COD_ELP=None, LIB_ELP=None, TYP_ELP=None, COD_GPE=None, ETU_ELP=0, ENS_ELP=0, DATE_CREATION=None, DATE_MODIF=None):
        self.COD_ELP = COD_ELP
        self.LIB_ELP = LIB_ELP
        self.TYP_ELP = TYP_ELP
        self.COD_GPE = COD_GPE
        self.ETU_ELP = ETU_ELP
        self.ENS_ELP = ETU_ELP
        self.DATE_CREATION = DATE_CREATION
        self.DATE_MODIF = DATE_MODIF

    def __repr__(self):
        return "<ElementPedagogi COD_ELP=%s LIB_ELP=%s TYP_ELP=%s COD_GPE=%s ETU_ELP=%s ENS_ELP=%s DATE_CREATION=%s DATE_MODIF=%s>" % (self.COD_ELP, self.LIB_ELP, self.TYP_ELP, self.COD_GPE, str(self.ETU_ELP), str(self.ENS_ELP), self.DATE_CREATION, self.DATE_MODIF)
