# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text

Base = declarative_base()


class ActualitesCoursSQLITE(Base):
    __tablename__ = "actualites_cours"

    ID_COURS = Column(Text, primary_key=True)
    TYPE_IND = Column(Text, primary_key=True)
    COD_ELP = Column(Text)
    TITRE_COURS = Column(Text)
    ACTU_COURS = Column(Text)

    def __init__(self, ID_COURS=None, TYPE_IND=None, COD_ELP=None, TITRE_COURS=None, ACTU_COURS=None):
        self.ID_COURS = ID_COURS
        self.TYPE_IND = TYPE_IND
        self.COD_ELP = COD_ELP
        self.TITRE_COURS = TITRE_COURS
        self.ACTU_COURS = ACTU_COURS

    def __repr__(self):
        return "<ActualitesCours ID_COURS=%s TYPE_IND=%s COD_ELP=%s TITRE_COURS=%s ACTU_COURS=%s>" % (self.ID_COURS, self.TYPE_IND, self.COD_ELP, self.TITRE_COURS, self.ACTU_COURS)
