# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, String, DateTime, ForeignKey

from individu import IndividuMySQL

Base = declarative_base()


class ConsultationCoursSQLITE(Base):
    __tablename__ = "consultationCours"

    NUM_CONN = Column(Integer, primary_key=True)
    SESAME_ETU = Column(Text)
    DATE_CONS = Column(Text)
    ID_COURS = Column(Text)
    TYPE_CONS = Column(Text)
    ID_CONS = Column(Text)

    def __init__(self, SESAME_ETU=None, DATE_CONS=None, ID_COURS=None, TYPE_CONS=None, ID_CONS=None):
        self.SESAME_ETU = SESAME_ETU
        self.DATE_CONS = DATE_CONS
        self.ID_COURS = ID_COURS
        self.TYPE_CONS = TYPE_CONS
        self.ID_CONS = ID_CONS

    def __repr__(self):
        return "<Individu SESAME_ETU=%s DATE_CONN=%s ID_COURS=%s TYPE_CONS=%s ID_CONS=%s>" % (self.SESAME_ETU, self.DATE_CONN, self.ID_COURS, self.TYPE_CONS, self.ID_CONS)


class ConsultationCoursMySQL(Base):
    __tablename__ = "consultation_cours_mysql"

    NUM_CONS = Column(Integer, primary_key=True, autoincrement=True)
    SESAME_ETU = Column(String(50), ForeignKey(IndividuMySQL.SESAME_ETU))
    DATE_CONS = Column(DateTime(True))
    ID_COURS = Column(String(50), index=True)
    TYPE_CONS = Column(String(10), index=True)
    ID_CONS = Column(String(50))
    PUBLIC_CONS = Column(String(50), index=True)

    def __init__(self, SESAME_ETU=None, DATE_CONS=None, ID_COURS=None, TYPE_CONS=None, ID_CONS=None, PUBLIC_CONS=None):
        self.SESAME_ETU = SESAME_ETU
        self.DATE_CONS = DATE_CONS
        self.ID_COURS = ID_COURS
        self.TYPE_CONS = TYPE_CONS
        self.ID_CONS = ID_CONS
        self.PUBLIC_CONS = PUBLIC_CONS

    def __repr__(self):
        return "<Individu SESAME_ETU=%s DATE_CONN=%s ID_COURS=%s TYPE_CONS=%s ID_CONS=%s PUBLIC_CONS=%s>" % (self.SESAME_ETU, self.DATE_CONN, self.ID_COURS, self.TYPE_CONS, self.ID_CONS, self.PUBLIC_CONS)
