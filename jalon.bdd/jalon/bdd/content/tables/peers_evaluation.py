# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, TEXT

Base = declarative_base()


class PeersEvaluationMySQL(Base):
    __tablename__ = "peers_evaluation_mysql"

    DEPOSIT_BOX = Column(String(50), primary_key=True)
    DEPOSIT_STU = Column(String(50), primary_key=True)
    CORRECTED_STU = Column(String(50), primary_key=True)
    CRITERIA = Column(Integer, primary_key=True, autoincrement=False)
    CRITERIA_DATE = Column(DateTime(True))
    CRITERIA_NOTE = Column(Integer)
    CRITERIA_COMMENT = Column(String(300))

    def __init__(self, DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, CRITERIA, CRITERIA_DATE=None, CRITERIA_NOTE=None, CRITERIA_COMMENT=None):
        self.DEPOSIT_BOX = DEPOSIT_BOX
        self.DEPOSIT_STU = DEPOSIT_STU
        self.CORRECTED_STU = CORRECTED_STU
        self.CRITERIA = CRITERIA
        self.CRITERIA_DATE = CRITERIA_DATE
        self.CRITERIA_NOTE = CRITERIA_NOTE
        self.CRITERIA_COMMENT = CRITERIA_COMMENT

    def __repr__(self):
        return "<PeersEvaluationMySQL DEPOSIT_BOX=%s DEPOSIT_STU=%s CORRECTED_STU=%s CRITERIA=%s>" % (self.DEPOSIT_BOX, self.DEPOSIT_STU, self.CORRECTED_STU, self.CRITERIA)


class PeersAverageMySQL(Base):
    __tablename__ = "peers_average_mysql"

    DEPOSIT_BOX = Column(String(50), primary_key=True)
    DEPOSIT_STU = Column(String(50), primary_key=True)
    CRITERIA = Column(Integer, primary_key=True, autoincrement=False)
    CRITERIA_STATE = Column(Boolean)
    CRITERIA_DATE = Column(DateTime(True))
    CRITERIA_AVERAGE = Column(Integer)
    CRITERIA_NOTE_T = Column(Integer)
    CRITERIA_COMMENT_T = Column(TEXT)

    def __init__(self, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_STATE=False, CRITERIA_DATE=None, CRITERIA_AVERAGE=0, CRITERIA_NOTE_T=0, CRITERIA_COMMENT_T=""):
        self.DEPOSIT_BOX = DEPOSIT_BOX
        self.DEPOSIT_STU = DEPOSIT_STU
        self.CRITERIA = CRITERIA
        self.CRITERIA_STATE = CRITERIA_STATE
        self.CRITERIA_DATE = CRITERIA_DATE
        self.CRITERIA_AVERAGE = CRITERIA_AVERAGE
        self.CRITERIA_NOTE_T = CRITERIA_NOTE_T
        self.CRITERIA_COMMENT_T = CRITERIA_COMMENT_T

    def __repr__(self):
        return "<PeersEvaluationMySQL DEPOSIT_BOX=%s DEPOSIT_STU=%s CRITERIA=%s>" % (self.DEPOSIT_BOX, self.DEPOSIT_STU, self.CRITERIA)
