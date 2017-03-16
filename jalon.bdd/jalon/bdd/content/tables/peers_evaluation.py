# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, TEXT, UniqueConstraint

Base = declarative_base()


class PeersEvaluationMySQL(Base):
    __tablename__ = "peers_evaluation_mysql"

    PKEY = Column(Integer, primary_key=True, autoincrement=True)
    DEPOSIT_BOX = Column(String(50), index=True)
    DEPOSIT_STU = Column(String(50), index=True)
    CORRECTED_STU = Column(String(50))
    CRITERIA = Column(String(5))
    CRITERIA_DATE = Column(DateTime(True))
    CRITERIA_NOTE = Column(Integer)
    CRITERIA_COMMENT = Column(TEXT)
    FOR_AVG = Column(Boolean)
    UniqueConstraint("DEPOSIT_BOX", "DEPOSIT_STU", "CORRECTED_STU", "CRITERIA")

    def __init__(self, DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, CRITERIA, CRITERIA_DATE=None, CRITERIA_NOTE=None, CRITERIA_COMMENT=None, FOR_AVG=True):
        self.DEPOSIT_BOX = DEPOSIT_BOX
        self.DEPOSIT_STU = DEPOSIT_STU
        self.CORRECTED_STU = CORRECTED_STU
        self.CRITERIA = CRITERIA
        self.CRITERIA_DATE = CRITERIA_DATE
        self.CRITERIA_NOTE = CRITERIA_NOTE
        self.CRITERIA_COMMENT = CRITERIA_COMMENT
        self.FOR_AVG = FOR_AVG

    def __repr__(self):
        return "<PeersEvaluationMySQL DEPOSIT_BOX=%s DEPOSIT_STU=%s CORRECTED_STU=%s CRITERIA=%s>" % (self.DEPOSIT_BOX, self.DEPOSIT_STU, self.CORRECTED_STU, self.CRITERIA)


class PeersEvaluationNoteMySQL(Base):
    __tablename__ = "peers_evaluation_note_mysql"

    PKEY = Column(Integer, primary_key=True, autoincrement=True)
    DEPOSIT_BOX = Column(String(50), index=True)
    DEPOSIT_STU = Column(String(50), index=True)
    CORRECTED_STU = Column(String(50))
    NOTE = Column(Float)
    UniqueConstraint("DEPOSIT_BOX", "DEPOSIT_STU", "CORRECTED_STU")

    def __init__(self, DEPOSIT_BOX, DEPOSIT_STU, CORRECTED_STU, NOTE):
        self.DEPOSIT_BOX = DEPOSIT_BOX
        self.DEPOSIT_STU = DEPOSIT_STU
        self.CORRECTED_STU = CORRECTED_STU
        self.NOTE = NOTE

    def __repr__(self):
        return "<PeersEvaluationNoteMySQL DEPOSIT_BOX=%s DEPOSIT_STU=%s CORRECTED_STU=%s NOTE=%s>" % (self.DEPOSIT_BOX, self.DEPOSIT_STU, self.CORRECTED_STU, self.NOTE)


class PeersSelfEvaluationMySQL(Base):
    __tablename__ = "peers_self_evaluation_mysql"

    PKEY = Column(Integer, primary_key=True, autoincrement=True)
    DEPOSIT_BOX = Column(String(50), index=True)
    DEPOSIT_STU = Column(String(50), index=True)
    CRITERIA = Column(String(5))
    CRITERIA_DATE = Column(DateTime(True))
    CRITERIA_NOTE = Column(Integer)
    CRITERIA_COMMENT = Column(TEXT)
    UniqueConstraint("DEPOSIT_BOX", "DEPOSIT_STU", "CRITERIA")

    def __init__(self, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_DATE=None, CRITERIA_NOTE=None, CRITERIA_COMMENT=None):
        self.DEPOSIT_BOX = DEPOSIT_BOX
        self.DEPOSIT_STU = DEPOSIT_STU
        self.CRITERIA = CRITERIA
        self.CRITERIA_DATE = CRITERIA_DATE
        self.CRITERIA_NOTE = CRITERIA_NOTE
        self.CRITERIA_COMMENT = CRITERIA_COMMENT

    def __repr__(self):
        return "<PeersEvaluationMySQL DEPOSIT_BOX=%s DEPOSIT_STU=%s CRITERIA=%s>" % (self.DEPOSIT_BOX, self.DEPOSIT_STU, self.CRITERIA)


class PeersSelfEvaluationNoteMySQL(Base):
    __tablename__ = "peers_self_evaluation_note_mysql"

    PKEY = Column(Integer, primary_key=True, autoincrement=True)
    DEPOSIT_BOX = Column(String(50), index=True)
    DEPOSIT_STU = Column(String(50), index=True)
    NOTE = Column(Float)
    UniqueConstraint("DEPOSIT_BOX", "DEPOSIT_STU")

    def __init__(self, DEPOSIT_BOX, DEPOSIT_STU, NOTE):
        self.DEPOSIT_BOX = DEPOSIT_BOX
        self.DEPOSIT_STU = DEPOSIT_STU
        self.NOTE = NOTE

    def __repr__(self):
        return "<PeersEvaluationNoteMySQL DEPOSIT_BOX=%s DEPOSIT_STU=%s NOTE=%s>" % (self.DEPOSIT_BOX, self.DEPOSIT_STU, self.NOTE)


class PeersAverageMySQL(Base):
    __tablename__ = "peers_average_mysql"

    PKEY = Column(Integer, primary_key=True, autoincrement=True)
    DEPOSIT_BOX = Column(String(50), index=True)
    DEPOSIT_STU = Column(String(50), index=True)
    CRITERIA = Column(String(5))
    CRITERIA_CODE = Column(Integer)
    # 1 : OK ; 2 : Pas assez d'évaluation ; 3 : MARGE du critère dépassée
    CRITERIA_VALUE = Column(TEXT)
    CRITERIA_DATE = Column(DateTime(True))
    CRITERIA_AVERAGE = Column(Float)
    CRITERIA_NOTE_T = Column(Integer)
    CRITERIA_COMMENT_T = Column(TEXT)
    UniqueConstraint("DEPOSIT_BOX", "DEPOSIT_STU", "CRITERIA")

    def __init__(self, DEPOSIT_BOX, DEPOSIT_STU, CRITERIA, CRITERIA_CODE=0, CRITERIA_VALUE=None, CRITERIA_DATE=None, CRITERIA_AVERAGE=0, CRITERIA_NOTE_T=0, CRITERIA_COMMENT_T=""):
        self.DEPOSIT_BOX = DEPOSIT_BOX
        self.DEPOSIT_STU = DEPOSIT_STU
        self.CRITERIA = CRITERIA
        self.CRITERIA_CODE = CRITERIA_CODE
        self.CRITERIA_VALUE = CRITERIA_VALUE
        self.CRITERIA_DATE = CRITERIA_DATE
        self.CRITERIA_AVERAGE = CRITERIA_AVERAGE
        self.CRITERIA_NOTE_T = CRITERIA_NOTE_T
        self.CRITERIA_COMMENT_T = CRITERIA_COMMENT_T

    def __repr__(self):
        return "<PeersEvaluationMySQL DEPOSIT_BOX=%s DEPOSIT_STU=%s CRITERIA=%s>" % (self.DEPOSIT_BOX, self.DEPOSIT_STU, self.CRITERIA)


class PeersEvaluationAverageMySQL(Base):
    __tablename__ = "peers_evaluation_average_mysql"

    PKEY = Column(Integer, primary_key=True, autoincrement=True)
    DEPOSIT_BOX = Column(String(50), index=True)
    DEPOSIT_STU = Column(String(50), index=True)
    AVERAGE = Column(Float)
    IS_VERIFICATION = Column(Boolean)
    UniqueConstraint("DEPOSIT_BOX", "DEPOSIT_STU")

    def __init__(self, DEPOSIT_BOX, DEPOSIT_STU, AVERAGE, IS_VERIFICATION):
        self.DEPOSIT_BOX = DEPOSIT_BOX
        self.DEPOSIT_STU = DEPOSIT_STU
        self.AVERAGE = AVERAGE
        self.IS_VERIFICATION = IS_VERIFICATION

    def __repr__(self):
        return "<PeersEvaluationAverageMySQL DEPOSIT_BOX=%s DEPOSIT_STU=%s AVERAGE=%s IS_VERIFICATION=%s>" % (self.DEPOSIT_BOX, self.DEPOSIT_STU, self.AVERAGE, self.IS_VERIFICATION)
