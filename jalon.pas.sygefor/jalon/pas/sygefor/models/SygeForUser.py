"""Class: SygeforHelper
"""

import random, string, sha, md5, datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, TIMESTAMP
from sqlalchemy import Text, Float, ForeignKey, Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class User(Base):
    __tablename__ = "tiers_stagiaire"

    idTiers = Column(Integer, primary_key=True)
    loginStagiaire = Column(String(50), unique=True)
    passwordStagiaire = Column(String(10))

    # roles
    #_roles =  relation(
    #    RoleAssignment, collection_class=set, cascade="all, delete, delete-orphan")
    #roles = association_proxy("_roles", "name")

    # memberdata property sheet
    bannedStagiaire = Column(Integer)
    idCategoriePublic = Column(Integer)
    idSituationProfessionnelle = Column(Integer)
    idDiscipline = Column(Integer)
    idCursus = Column(Integer)

    def __init__(self, idTiers=None, loginStagiaire=None, passwordStagiaire=None):
        self.idTiers = idTiers
        self.loginStagiaire = loginStagiaire
        self.passwordStagiaire = passwordStagiaire
        #self.salt = self.generate_salt()
        #self.date_created = datetime.datetime.now()

    def generate_salt(self):
        return ''.join(random.sample(string.letters, 12))

    def encrypt(self, password):
        return md5.md5(password).hexdigest()
        #return sha.sha(password).hexdigest()

    def check_password(self, password):
        print "------------------- check ---------------"
        print self.encrypt(password)
        print self.passwordStagiaire
        print "------------ check  (fin) ---------------"
        return self.encrypt(password) == self.passwordStagiaire
        #return password == self.password

    def __repr__(self):
        return "<User idtiers=%d login=%s name=%s>" % (self.idTiers, self.loginStagiaire, self.loginStagiaire)

class UserInfos(Base):
    __tablename__ = "tiers"

    idTiers = Column(Integer, primary_key=True)
    typeTiers = Column(String(1))
    idCivilite = Column(Integer)
    nomTiers = Column(String(50))
    prenomTiers = Column(String(50))
    idOrganisation = Column(Integer)
    organisationTiers = Column(String(50))
    serviceTiers = Column(String(50))
    statutTiers = Column(String(50))
    typeAdresseTiers = Column(String(5))
    etablissementAdresseTiers = Column(String(50))
    adresseTiers = Column(String(50))
    bpTiers = Column(String(30))
    cpTiers = Column(String(10))
    villeTiers = Column(String(20))
    cedexTiers = Column(String(10))
    telTiers = Column(String(20))
    faxTiers = Column(String(20))
    mailTiers = Column(String(50))
    siteWebTiers = Column(String(50))
    responsabilitesTiers = Column(String(50))
    observationsTiers = Column(String(100))
    situationProfessionnelleTiers = Column(String(50))
    idDomaine = Column(Integer)
    dateCreation = Column(String(20))
    dateModif = Column(String(20))

    def __init__(self, idTiers=None):
        self.idTiers = idTiers

    def __repr__(self):
        return "<User idtiers=%d>" % (self.idTiers)