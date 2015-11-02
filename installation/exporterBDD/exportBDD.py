# -*- coding: utf-8 -*-

import os
import ldap
import urllib2
import sqlite3

import tables

# SQL Alchemy
from sqlalchemy import create_engine, and_, distinct
from sqlalchemy.sql import func, text
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.pool import NullPool

from datetime import datetime

print os.environ["ORACLE_HOME"]
print os.environ["LD_LIBRARY_PATH"]

# Parametres généraux
url_connexion = "URL_CONNEXION_APOGEE"
cod_anu = "2015"
# à mettre à 1 sur la génération de l'année n-1
anu_in_cod = 0
# 0 = ne pas effacer, à mettre sur année n-1
exterieur_jalon = 1
uel = "WUEL0"
chemin = "/opt/exportApogee/exportBD"
cheminPhoto = "/opt/exportApogee/trombino"
protocol = "PROTOCOLE"
host = "ADRESSE_LDAP"
host2 = "ADRESSE_LDAP"
port = "PORT"
binduid = "uid=UID_LDAP,ou=EXAMPLE,dc=EXAMPLE,dc=EXAMPLE"
bindpwd = "PASSWORD_LDAP"
login_attr = "LOGIN_ATTRIBUTE"
users_base = "ou=EXAMPLE,ou=EXAMPLE,dc=EXAMPLE,dc=EXAMPLE"
nom_fichier = "jalonBDD.db"

liste_photo = os.listdir(cheminPhoto)

print "-------------- check exportApogee.db --------------"
liste_export = os.listdir(chemin)
if nom_fichier in liste_export:
    os.rename("%s/%s" % (chemin, nom_fichier), "%s/%s-old%s" % (chemin, nom_fichier, str(len(liste_export))))
    print "-------------- rename exportApogee.db --------------"

print "-------------- exporterApogeeLITE --------------"
#connexion base

conn = sqlite3.connect('%s/%s' % (chemin, nom_fichier))
c = conn.cursor()
#creation tables
print "-------------- connexion base --------------"
c.execute('''CREATE TABLE individu_lite
             (SESAME_ETU TEXT PRIMARY KEY, DATE_NAI_IND TEXT, LIB_NOM_PAT_IND TEXT, LIB_NOM_USU_IND TEXT, LIB_PR1_IND TEXT, TYPE_IND TEXT, COD_ETU INTEGER, EMAIL_ETU TEXT, ADR1_IND TEXT, ADR2_IND TEXT, COD_POST_IND TEXT, VIL_IND TEXT, UNIV_IND TEXT, PROMO_IND TEXT, STATUS_IND TEXT, EXTERIEUR_JALON BOOLEAN)''')
c.execute('''CREATE TABLE element_pedagogi_lite
             (COD_ELP TEXT PRIMARY KEY, LIB_ELP TEXT, ETU_ELP INTEGER, ENS_ELP INTEGER, TYP_ELP TEXT, COD_GPE TEXT, DATE_CREATION TEXT, DATE_MODIF TEXT, EXTERIEUR_JALON BOOLEAN)''')
c.execute('''CREATE TABLE etp_regroupe_elp_lite
             (PKEY INTEGER PRIMARY KEY AUTOINCREMENT, COD_ELP_PERE TEXT, COD_ELP_FILS TEXT, TYP_ELP TEXT, EXTERIEUR_JALON BOOLEAN,
             FOREIGN KEY(COD_ELP_PERE) REFERENCES element_pedagogi_lite(COD_ELP),
             FOREIGN KEY(COD_ELP_FILS) REFERENCES element_pedagogi_lite(COD_ELP))''')
c.execute('''CREATE TABLE ind_contrat_elp_lite
             (SESAME_ETU TEXT, COD_ELP TEXT, TYPE_ELP TEXT, COD_ELP_PERE TEXT, RESPONSABLE BOOLEAN, EXTERIEUR_JALON BOOLEAN, PRIMARY KEY (SESAME_ETU, COD_ELP, COD_ELP_PERE))''')
#c.execute('''CREATE TABLE actualites_cours
#             (ID_COURS TEXT, TYPE_IND TEXT, COD_ELP TEXT, TITRE_COURS TEXT, ACTU_COURS TEXT, PRIMARY KEY (ID_COURS, TYPE_IND))''')
#c.execute('''CREATE TABLE connexion
#             (NUM_CONN INTEGER PRIMARY KEY AUTOINCREMENT, SESAME_ETU TEXT, DATE_CONN TEXT, FOREIGN KEY(SESAME_ETU) REFERENCES individu_lite(SESAME_ETU))''')
conn.commit()
print "-------------- table crees --------------"
# connexion apogée
print "-------------- Connexion Apogée  --------------"
Session = sessionmaker()
engine = create_engine(url_connexion, echo=False, poolclass=NullPool)
Session.configure(bind=engine)
session = Session()
print "-------------- Connexion Apogée OK --------------"
# groupe
print "-------------- Groupe --------------"
GPE = aliased(tables.Groupe)
IAG = aliased(tables.IndAffecteGpe)
recherche = session.query(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE, func.count(distinct(IAG.COD_IND)).label("nb_etu")).join(IAG, and_(IAG.COD_GPE==GPE.COD_GPE, IAG.COD_ANU==int(cod_anu))).filter(GPE.LIB_GPE <> 'None').group_by(GPE.LIB_GPE, GPE.COD_GPE, GPE.COD_EXT_GPE).order_by(GPE.LIB_GPE)
exportApogee = recherche.all()
num = 1
for groupe in exportApogee:
    LIB_GPE = groupe[0]
    LIB_GPE = LIB_GPE.replace("'", " ")
    LIB_GPE = LIB_GPE.replace('"', " ")
    LIB_GPE = LIB_GPE.strip()
    COD_ELP = groupe[1]
    if anu_in_cod:
       LIB_GPE = "%s %s" % (LIB_GPE, cod_anu)
       COD_ELP = "%s-%s" % (groupe[1], cod_anu)
    insert = "INSERT INTO element_pedagogi_lite VALUES ('%s', '%s', %i, 0, 'groupe', '%s', '', '', %i)" % (COD_ELP, LIB_GPE, groupe[3], groupe[2], exterieur_jalon)
    c.execute(insert)
    print "%s : %s : %s : %i" % (str(num), COD_ELP, LIB_GPE.encode("utf-8"), groupe[3])
    num = num + 1
conn.commit()
# ue
print "-------------- UE --------------"
num = 1
listeUE = []
ELP = aliased(tables.ElementPedagogi)
ERE = aliased(tables.ElpRegroupeElp)
ICE = aliased(tables.IndContratElp)

condition = ~ERE.COD_LSE.like(uel + '%')
recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, func.count(distinct(ICE.COD_IND)).label("nb_etu")).outerjoin(ERE, ERE.COD_ELP_FILS==ELP.COD_ELP).outerjoin(ICE, and_(ICE.COD_ELP==ELP.COD_ELP, ICE.COD_ANU==int(cod_anu))).filter(and_(ELP.ETA_ELP <> 'F', ERE.ETA_LSE <> 'F', condition)).group_by(ELP.LIB_ELP, ELP.COD_ELP).order_by(ELP.LIB_ELP)
exportApogee = recherche.all()
for ue in exportApogee:
    LIB_ELP = ue[0]
    LIB_ELP = LIB_ELP.replace("'", " ")
    LIB_ELP = LIB_ELP.replace('"', " ")
    LIB_ELP = LIB_ELP.strip()
    COD_ELP = ue[1]
    if anu_in_cod:
        LIB_ELP = "%s %s" % (LIB_ELP, cod_anu)
        COD_ELP = "%s-%s" % (ue[1], cod_anu)
    insert = "INSERT INTO element_pedagogi_lite VALUES ('%s', '%s', %i, 0, 'ue', '', '', '', %i)" % (COD_ELP, LIB_ELP, ue[2], exterieur_jalon)
    c.execute(insert)
    print "%s : %s : %s" % (str(num), COD_ELP, LIB_ELP.encode("utf-8"))
    num = num + 1
    listeUE.append(COD_ELP)
conn.commit()

# uel
print "-------------- UEL SEM PAIR--------------"
num = 1
listeUEL = []
#condition = ERE.COD_LSE.like(uel + '%')
listePair = ["WPAIRB", "WPAIRD", "WPAIRE", "WPAIRS"]
for COD_LSE in listePair:
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, func.count(distinct(ICE.COD_IND)).label("nb_etu")).outerjoin(ERE, and_(ERE.COD_ELP_FILS==ELP.COD_ELP)).outerjoin(ICE, and_(ICE.COD_ELP==ELP.COD_ELP, ICE.COD_LSE==COD_LSE, ICE.COD_ANU==int(cod_anu))).filter(and_(ELP.ETA_ELP <> 'F', ERE.ETA_LSE <> 'F', ERE.COD_LSE==COD_LSE)).group_by(ELP.LIB_ELP, ELP.COD_ELP).order_by(ELP.LIB_ELP)
    exportApogee = recherche.all()
    for uel in exportApogee:
        LIB_ELP = uel[0]
        LIB_ELP = LIB_ELP.replace("'", " ")
        LIB_ELP = LIB_ELP.replace('"', " ")
        LIB_ELP = LIB_ELP.strip()
        COD_ELP = uel[1]
    	if anu_in_cod:
       		LIB_ELP = "%s %s" % (LIB_ELP, cod_anu)
       		COD_ELP = "%s-%s" % (uel[1], cod_anu)
        try:
            insert = "INSERT INTO element_pedagogi_lite VALUES ('%s-SEM2', '%s', %i, 0, 'uel', '', '', '', %i)" % (COD_ELP, LIB_ELP, uel[2], exterieur_jalon)
            c.execute(insert)
            listeUE.append(COD_ELP)
            listeUEL.append(COD_ELP)
            print "%s : %s : %s" % (str(num), COD_ELP, LIB_ELP.encode("utf-8"))
            num = num + 1
        except:
            pass
    conn.commit()
print "-------------- UEL SEM IMPAIR--------------"
num = 1
#condition = ERE.COD_LSE.like(uel + '%')
listeImpair = ["WIMPB", "WIMPD", "WIMPH", "WIMPS"]
for COD_LSE in listeImpair:
    recherche = session.query(ELP.LIB_ELP, ELP.COD_ELP, func.count(distinct(ICE.COD_IND)).label("nb_etu")).outerjoin(ERE, and_(ERE.COD_ELP_FILS==ELP.COD_ELP)).outerjoin(ICE, and_(ICE.COD_ELP==ELP.COD_ELP, ICE.COD_LSE==COD_LSE, ICE.COD_ANU==int(cod_anu))).filter(and_(ELP.ETA_ELP <> 'F', ERE.ETA_LSE <> 'F', ERE.COD_LSE==COD_LSE)).group_by(ELP.LIB_ELP, ELP.COD_ELP).order_by(ELP.LIB_ELP)
    exportApogee = recherche.all()
    for uel in exportApogee:
        LIB_ELP = uel[0]
        LIB_ELP = LIB_ELP.replace("'", " ")
        LIB_ELP = LIB_ELP.replace('"', " ")
        LIB_ELP = LIB_ELP.strip()
        COD_ELP = uel[1]
    	if anu_in_cod:
       		LIB_ELP = "%s %s" % (LIB_ELP, cod_anu)
       		COD_ELP = "%s-%s" % (uel[1], cod_anu)
        try:
            insert = "INSERT INTO element_pedagogi_lite VALUES ('%s-SEM1', '%s', %i, 0, 'uel', '', '', '', %i)" % (COD_ELP, LIB_ELP, uel[2], exterieur_jalon)
            c.execute(insert)
            listeUE.append(COD_ELP)
            if not uel[1] in listeUEL:
                listeUEL.append(COD_ELP)
        except:
            pass
        print "%s : %s : %s" % (str(num), COD_ELP, LIB_ELP.encode("utf-8"))
        num = num + 1
    conn.commit()

# version etape
print "-------------- Etape --------------"
# connexion au ldap
user = binduid
password = bindpwd
try:
    server = "%s://%s:%s" % (protocol, host, port)
    ldapserver = ldap.initialize(server)
    ldapserver.simple_bind_s(user, password)
except:
    print "--------------------------- LDAP 2 ---------------------------"
    server = "%s://%s:%s" % (protocol, host2, port)
    ldapserver = ldap.initialize(server)
    ldapserver.simple_bind_s(user, password)
num = 1
dicoEtudiant = {}
V = aliased(tables.VersionEtape)
VV = aliased(tables.VdiFractionnerVet)
IAE = aliased(tables.InsAdmEtp)
IND = aliased(tables.Individu)
recherche = session.query(V.COD_ETP, V.COD_VRS_VET, V.LIB_WEB_VET, func.count(distinct(IAE.COD_IND))).outerjoin(VV, and_(VV.COD_ETP==V.COD_ETP, VV.COD_VRS_VET==V.COD_VRS_VET)).outerjoin(IAE, and_(IAE.COD_ETP==V.COD_ETP, IAE.COD_VRS_VET==V.COD_VRS_VET, IAE.ETA_IAE == "E", IAE.COD_ANU==int(cod_anu))).filter(and_(VV.DAA_FIN_RCT_VET >= int(cod_anu), VV.DAA_FIN_VAL_VET >= int(cod_anu))).group_by(V.LIB_WEB_VET, V.COD_ETP, V.COD_VRS_VET).having(func.count(distinct(IAE.COD_IND)) > 0).order_by(V.LIB_WEB_VET)
exportApogee = recherche.all()
print "etape : %s" % len(exportApogee)
for etape in exportApogee:
    COD_ETP = etape[0]
    COD_VRS_VET = str(etape[1])
    LIB_WEB_VET = etape[2]
    LIB_WEB_VET = LIB_WEB_VET.replace("'", " ")
    LIB_WEB_VET = LIB_WEB_VET.replace('"', " ")
    LIB_WEB_VET = LIB_WEB_VET.strip()
    COD_ELP =  "%s-%s" % (COD_ETP, COD_VRS_VET)
    if anu_in_cod:
       LIB_WEB_VET = "%s %s" % (LIB_WEB_VET, cod_anu)
       COD_ELP = "%s-%s-%s" % (COD_ETP, COD_VRS_VET, cod_anu)
    suite = 1
    try:
        insert = "INSERT INTO element_pedagogi_lite VALUES ('%s', '%s', %i, 0, 'etape', '', '', '', %i)" % (COD_ELP, LIB_WEB_VET, etape[3], exterieur_jalon)
        c.execute(insert)
        print "%s : %s : %s, %s etudiants" % (str(num), COD_ELP, LIB_WEB_VET.encode("utf-8"), str(etape[3]))
        num = num + 1
    except:
        suite = 0
    if suite:
        print "-------------- Etudiants --------------"
        numInd = 1
        rechercheEtu = session.query(IAE.COD_IND, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, IND.COD_ETU, IND.DATE_NAI_IND, IND.LIB_NOM_USU_IND).outerjoin(IND, IND.COD_IND == IAE.COD_IND).filter(and_(IAE.COD_ETP == COD_ETP, IAE.COD_VRS_VET == COD_VRS_VET, IAE.ETA_IAE == "E", IAE.COD_ANU == int(cod_anu))).order_by(IND.LIB_NOM_PAT_IND)
        requete = rechercheEtu.all()
        for individu in requete:
            # acquisition du sesame et de l'email dans le ldap
            EMAIL_ETU = ""
            SESAME_ETU = '%s%s%s' % (individu[1][0].lower(), individu[2][0].lower(), str(individu[3])[2:])
            ldapfilter = "(&(%s=%s))" % (login_attr, str(individu[3]))
            result = ldapserver.search_s(users_base, ldap.SCOPE_SUBTREE, ldapfilter, None)
            if result:
                EMAIL_ETU = result[0][1].get("mail", [""])[0]
                SESAME_ETU = result[0][1].get("supannAliasLogin", SESAME_ETU)[0]
            if not individu[0] in dicoEtudiant:
                dicoEtudiant[individu[0]] = SESAME_ETU
            if not SESAME_ETU in liste_photo:
                #req = urllib2.Request("http://camus.unice.fr/unicampus/images/Photos/21100074Apog0060931E.jpg")
                req = urllib2.Request("http://camus.unice.fr/unicampus/images/Photos/%sApog0060931E.jpg" % str(individu[3]))
                req.add_header("Expires", "Mon, 26 Jul 1997 05:00:00 GMT")
                req.add_header("Last-Modified", datetime.today())
                req.add_header("Cache-Control", "no-store, no-cache, must-revalidate, post-check=0, pre-check=0")
                req.add_header("Pragma", "no-cache")
                req.add_header("Content-type", "image/jpeg")
                try:
                    r = urllib2.urlopen(req)
                    photo = open("%s/%s.jpg" % (cheminPhoto, SESAME_ETU), "wb")
                    photo.write(r.read())
                    photo.close()
                except:
                    print "echec photo %s (%s)" % (SESAME_ETU, str(individu[3]))
                    pass
            LIB_NOM_PAT_IND = individu[1]
            LIB_NOM_PAT_IND = LIB_NOM_PAT_IND.replace("'", " ")
            LIB_NOM_PAT_IND = LIB_NOM_PAT_IND.replace('"', " ")
            LIB_NOM_USU_IND = individu[-1]
            if LIB_NOM_USU_IND:
                LIB_NOM_USU_IND = LIB_NOM_USU_IND.replace("'", " ")
                LIB_NOM_USU_IND = LIB_NOM_USU_IND.replace('"', " ")
            else:
                LIB_NOM_USU_IND = ""
            LIB_PR1_IND = individu[2]
            LIB_PR1_IND = LIB_PR1_IND.replace("'", " ")
            LIB_PR1_IND = LIB_PR1_IND.replace('"', " ")
            EMAIL_ETU = EMAIL_ETU.replace("'", "&quot;")
            insert = "INSERT INTO individu_lite VALUES ('%s', '%s', '%s', '%s', '%s', 'Etudiant', %i, '%s', '', '', '', '', '', '', '', %i)" % (SESAME_ETU, individu[4], LIB_NOM_PAT_IND, LIB_NOM_USU_IND, LIB_PR1_IND, individu[3], EMAIL_ETU, exterieur_jalon)
            try:
                c.execute(insert)
                print "%s : %s %s" % (str(numInd), LIB_NOM_PAT_IND.encode("utf-8"), LIB_PR1_IND.encode("utf-8"))
                numInd = numInd + 1
            except:
                pass
            try:
                insert = "INSERT INTO ind_contrat_elp_lite VALUES ('%s', '%s', 'etape', '%s', 0, %i)" % (SESAME_ETU, COD_ELP, COD_ELP, exterieur_jalon)
                c.execute(insert)
                print "%s : %s %s" % (numInd, SESAME_ETU, COD_ELP)
            except:
                pass
        conn.commit()
        #if COD_ETP == "SL1SF" and COD_VRS_VET == "140":
        #    print "FIN"
        #    break

        print "-------------- UE - ETAPE --------------"
        numUE = 1
        listeUEEtape = []

        requete = text("""SELECT ere.cod_elp_fils, elp.lib_elp
                            FROM elp_regroupe_elp ere, element_pedagogi elp
                            WHERE elp.cod_elp = ere.cod_elp_fils
                                START WITH ere.cod_lse in
                                     (SELECT LSE.COD_LSE
                                     FROM LISTE_ELP LSE, VET_REGROUPE_LSE VRL
                                     WHERE vrl.cod_etp = '%s'
                                        AND vrl.cod_vrs_vet = %s
                                        AND lse.cod_lse = vrl.cod_lse
                                        AND vrl.dat_frm_rel_lse_vet is null
                                        AND lse.eta_lse != 'F'
                                     )
                                     AND ere.cod_elp_pere is null
                                     AND ere.eta_elp_fils != 'F'
                                     AND ere.tem_sus_elp_fils = 'N'
                                CONNECT BY PRIOR ere.cod_elp_fils = ere.cod_elp_pere
                                     AND ere.eta_elp_fils != 'F'
                                     AND ere.tem_sus_elp_fils = 'N'
                                     AND NVL (ere.eta_elp_pere, 'O') != 'F'
                                     AND NVL (ere.tem_sus_elp_pere, 'N') = 'N'
                                     AND ere.eta_lse != 'F'
                                     AND ere.date_fermeture_lien is null
                              """ % (str(COD_ETP), int(COD_VRS_VET)))

        rechercheUEs = session.execute(requete)
        requete = rechercheUEs.fetchall()
        for ue in requete:
            COD_ELP_FILS = ue[0]
            if anu_in_cod:
                COD_ELP_FILS = "%s-%s" % (ue[0], cod_anu)
            if COD_ELP_FILS in listeUE and COD_ELP_FILS not in listeUEEtape:
                insert = "INSERT INTO etp_regroupe_elp_lite VALUES (null, '%s', '%s', 'ue', %i)" % (COD_ELP, COD_ELP_FILS, exterieur_jalon)
                c.execute(insert)
                print "%s : %s -> %s" % (str(numUE), COD_ELP_FILS, COD_ELP)
                numUE = numUE + 1
                listeUEEtape.append(COD_ELP_FILS)
                if ue[0] in listeUEL and not ("%s-SEM1" % COD_ELP_FILS in listeUEEtape):
                    insert = "INSERT INTO etp_regroupe_elp_lite VALUES (null, '%s', '%s-SEM1', 'ue', %i)" % (COD_ELP, COD_ELP_FILS, exterieur_jalon)
                    c.execute(insert)
                    print "%s : %s-SEM1" % (str(numUE), COD_ELP_FILS)
                    numUE = numUE + 1
                    listeUEEtape.append("%s-SEM1" % COD_ELP_FILS)
                    insert = "INSERT INTO etp_regroupe_elp_lite VALUES (null, '%s', '%s-SEM2', 'ue', %i)" % (COD_ELP, COD_ELP_FILS, exterieur_jalon)
                    c.execute(insert)
                    print "%s : %s-SEM2" % (str(numUE), COD_ELP_FILS)
                    numUE = numUE + 1
                    listeUEEtape.append("%s-SEM2" % COD_ELP_FILS)
        print "nb d'ue dans apogee pour cette etape : %s" % str(len(requete))
        print "nb d'ue sans doublon pour cette etape : %s" % str(len(listeUEEtape))
        conn.commit()
        print ""
# inscription ue - uel
print "-------------- INS - UE - UEL --------------"
num = 1
#listeUE = []
recherche = session.query(IND.COD_IND, IND.LIB_NOM_PAT_IND, IND.LIB_PR1_IND, ICE.COD_ELP, ICE.COD_ETP, ICE.COD_LSE, ICE.COD_VRS_VET).outerjoin(ICE, ICE.COD_IND == IND.COD_IND).outerjoin(ELP, ICE.COD_ELP == ELP.COD_ELP).filter(ICE.COD_ANU == int(cod_anu)).order_by(IND.LIB_NOM_PAT_IND)
exportApogee = recherche.all()
for inscription in exportApogee:
    if inscription[0] in dicoEtudiant:
        SESAME_ETU = dicoEtudiant[inscription[0]]
        TYPE_ELP = "ue"
        COD_ELP = inscription[3]
        COD_ELP_PERE = "%s-%s" % (inscription[4], inscription[6])
        if anu_in_cod:
           COD_ELP = "%s-%s" % (COD_ELP, cod_anu)
           COD_ELP_PERE = "%s-%s" % (COD_ELP_PERE, cod_anu)
        try:
            insert = "INSERT INTO ind_contrat_elp_lite VALUES ('%s', '%s', '%s', '%s', 0, %i)" % (SESAME_ETU, COD_ELP, TYPE_ELP, COD_ELP_PERE, exterieur_jalon)
            c.execute(insert)
            print "%s : %s %s (%s)" % (str(num), SESAME_ETU, COD_ELP, TYPE_ELP)
            num = num + 1
        except:
            pass
        if inscription[5] in listePair:
            TYPE_ELP = "uel"
            COD_ELP = "%s-SEM2" % COD_ELP
            try:
                insert = "INSERT INTO ind_contrat_elp_lite VALUES ('%s', '%s', '%s', '%s', 0, %i)" % (SESAME_ETU, COD_ELP, TYPE_ELP, COD_ELP_PERE, exterieur_jalon)
                c.execute(insert)
            except:
                pass
        if inscription[5] in listeImpair:
            TYPE_ELP = "uel"
            COD_ELP = "%s-SEM1" % COD_ELP
            try:
                insert = "INSERT INTO ind_contrat_elp_lite VALUES ('%s', '%s', '%s', '%s', 0, %i)" % (SESAME_ETU, COD_ELP, TYPE_ELP, COD_ELP_PERE, exterieur_jalon)
                c.execute(insert)
            except:
                pass
conn.commit()
# inscription groupe
print "-------------- INS - Groupe --------------"
num = 1
dicoICE = {}
listeERE = []
GPE = aliased(tables.Groupe)
GPO = aliased(tables.GpeObj)
IAG = aliased(tables.IndAffecteGpe)
recherche = session.query(IAG.COD_GPE, GPE.COD_EXT_GPE, IAG.COD_IND, GPO.TYP_OBJ_GPO, GPO.COD_ELP, GPO.COD_ETP, GPO.COD_VRS_VET).outerjoin(GPE, IAG.COD_GPE==GPE.COD_GPE).outerjoin(GPO, GPE.COD_GPE==GPO.COD_GPE).outerjoin(IND, IAG.COD_IND==IND.COD_IND).filter(and_(IAG.COD_ANU==int(cod_anu), GPE.LIB_GPE <> None)).group_by(IAG.COD_GPE, GPE.COD_EXT_GPE, IAG.COD_IND, GPO.TYP_OBJ_GPO, GPO.COD_ELP, GPO.COD_ETP, GPO.COD_VRS_VET)
exportApogee = recherche.all()
for inscription in exportApogee:
    if inscription[2] in dicoEtudiant:
        if not inscription[0] in dicoICE:
            dicoICE[inscription[0]] = []
        SESAME_ETU = dicoEtudiant[inscription[2]]
        COD_ELP = None
        if inscription[3] == "VET":
            COD_ELP = "%s-%s" % (inscription[5], inscription[6])
            if anu_in_cod:
            	COD_ELP = "%s-%s" % (COD_ELP, cod_anu)
            inscriptionType = "etape"
        if inscription[3] == "ELP":
            COD_ELP = inscription[4]
            if anu_in_cod:
            	COD_ELP = "%s-%s" % (COD_ELP, cod_anu)
            inscriptionType = "ue"
            #if inscription[7] in listeUELPair:
            #    inscriptionType = "uel"
            #    COD_ELP = "%s-SEM2" % inscription[4]
            #if inscription[7] in listeUELImpair:
            #    inscriptionType = "uel"
            #    COD_ELP = "%s-SEM1" % inscription[4]
        if not SESAME_ETU in dicoICE[inscription[0]]:
            COD_GPE = inscription[0]
            if anu_in_cod:
        	    COD_GPE = "%s-%s" % (COD_GPE, cod_anu)
            insert = "INSERT INTO ind_contrat_elp_lite VALUES ('%s', '%s', 'groupe', '%s', 0, %i)" % (SESAME_ETU, COD_GPE, COD_ELP, exterieur_jalon)
            c.execute(insert)
            dicoICE[inscription[0]].append(SESAME_ETU)
            print "%s : %s %s" % (str(num), SESAME_ETU, COD_GPE)
            num = num + 1

        COD_GPE = inscription[0]
        if anu_in_cod:
        	COD_GPE = "%s-%s" % (COD_GPE, cod_anu)
        if not "%s*-*%s" % (COD_GPE, COD_ELP) in listeERE:
            insert = "INSERT INTO etp_regroupe_elp_lite VALUES (null, '%s', '%s', '%s', %i)" % (COD_ELP, COD_GPE, inscriptionType, exterieur_jalon)
            c.execute(insert)
            print "%s : %s %s" % (COD_ELP, COD_GPE, inscriptionType)
            listeERE.append("%s*-*%s" % (COD_GPE, COD_ELP))
conn.commit()
print  "-------------- Export terminée -> Tranfert sur serveur--------------"

import paramiko

host = "HOST_JALON"
port = 22
user = "USER_TRANSFERT"
#password = "PASSWORD_USER_TRANSFERT"

transport = paramiko.Transport((host, port))

#utilisation clé privée publique
privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
transport.connect(username = user, pkey = mykey)

# avec mot de passe
#transport.connect(username = user, password = password)

sftp = paramiko.SFTPClient.from_transport(transport)
sftp.put('%s/%s' % (chemin, nom_fichier), '/opt/zope/sites/jalon/BDD/%s.mole' % nom_fichier)
sftp.close()
transport.close()

print  "-------------- Tranfert terminé--------------"

ssh = paramiko.SSHClient()
privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(host, username = user, key_filename = privatekeyfile)

#cmd = ["rm -f /opt/zope/sites/jalon/BDD/%s.old" % nom_fichier,
#       "mv /opt/zope/sites/jalon/BDD/%s /opt/zope/sites/jalon/BDD/%s.old" % ( nom_fichier,nom_fichier),
#       "mv /opt/zope/sites/jalon/BDD/%s.mole /opt/zope/sites/jalon/BDD/%s" %(nom_fichier,nom_fichier)]

cmd = ["cd /opt/zope/sites/majBDD",
       "/opt/zope/pythons/jalon/bin/python modifBDD.py"]

stdin, stdout, stderr = ssh.exec_command(" ; ".join(cmd))

#stdin, stdout, stderr = ssh.exec_command("rm -f /opt/zope/sites/jalon/BDD/%s.old ; \
#mv /opt/zope/sites/jalon/BDD/%s /opt/zope/sites/jalon/BDD/%s.old ; \
#mv /opt/zope/sites/jalon/BDD/%s.mole /opt/zope/sites/jalon/BDD/%s" %(nom_fichier,nom_fichier, nom_fichier, nom_fichier, nom_fichier))

print "".join(stdout.readlines())
print "".join(stderr.readlines())

print  "-------------- Commande terminée --------------"

os.system("rsync -e ssh -av SOURCE_FILESYSTEM USER_TRANSFERT@HOST_JALON:DESTINATION_FILESYSTEM ")

print  "-------------- Synchro Trombino terminée --------------"
