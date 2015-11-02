# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer

Base = declarative_base()

class ConnexionINDSQLITE(Base):
    __tablename__ = "connexion"

    NUM_CONN = Column(Integer, primary_key=True)
    SESAME_ETU = Column(Text)
    DATE_CONN = Column(Text)

    def __init__(self, SESAME_ETU=None, DATE_CONN=None):
        self.SESAME_ETU = SESAME_ETU
        self.DATE_CONN = DATE_CONN

    def __repr__(self):
        return "<Individu SESAME_ETU=%s DATE_CONN=%s>" % (self.SESAME_ETU, self.DATE_CONN)
