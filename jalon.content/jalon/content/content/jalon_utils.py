# -*- coding: utf-8 -*-
from zope.component import getUtility

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from jalon.content import contentMessageFactory as _
from jalon.content.content import jalon_encode

from datetime import datetime
from DateTime import DateTime

import smtplib

from email import message_from_string
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Header import Header
import email.Utils

from urlparse import urlparse
import urllib
import urllib2
import locale
import json
import re
import copy

# Messages de debug :
# from logging import getLogger
# LOG = getLogger('[jalon_utils]')


def authUser(context, quser=None, qclass=None, request=None, session_keep=False):
    u"""AuthUser WIMS : permet d'authentifier "quser" dans une classe wims "qclass".

    # request représente les parametres envoyés à la page (GET/POST)
    # session_keep permet de définir si on réutilise une eventuelle session wims existante ou pas.

    """
    # LOG.info("----- authUser -----")
    remote_addr = None
    url_connexion = context.wims("getAttribut", "url_connexion")
    # error_dict = {"status": "ERROR"}
    if request:
        # HTTP_X_REAL_IP n'existe que si la configuration de Nginx fournit bien ce
        # parametre à Zope.
        remote_addr = request.get('HTTP_X_REAL_IP', None)
        if not remote_addr:
            remote_addr = request['REMOTE_ADDR']

        if session_keep is True:
            # Si session_keep=True et qu'une session wims était déjà ouverte, on la conserve.
            # Attention : ici il faudrait vérifier sur WIMS que la session ouverte
            # était bien celle de l'utilisateur courant.
            wims_session = request.get('wims_session', None)
            if wims_session:
                return {'wims_session': wims_session,
                        'status':       'OK',
                        'home_url':     "%s?session=%s" % (url_connexion, wims_session)}
    dico = {"qclass": qclass, "quser": quser, "code": quser,
            "option": "lightpopup", "data1": remote_addr}
    rep = context.wims("authUser", dico)
    try:
        rep = json.loads(rep)
        # rep = context.wims("verifierRetourWims", {"rep": rep, "fonction": "jalon.content/jalon_utils.py/authUser", "message": "1ere identification de l'utilisateur %s." % quser, "requete": dico})
    except ValueError, e:
            rep = '{"status":"ERROR","exception_raised":"%s","message":"%s"}' % (
                string_for_json(rep), e)
            rep = json.loads(rep)

    if rep["status"] == "ERROR":
        # On prépare un éventuel message d'erreur à renvoyer
        message = _(
            u"Le serveur WIMS est actuellement injoignable. Merci de réessayer ultérieurement svp...")
        mess_type = "error"
        if quser != 'supervisor':

            if "in an exam session started on another IP" in rep["message"]:
                message = _(u"Vous tentez de vous connecter à un examen commencé sur une machine différente.<br/>\n\
                Veuillez retourner sur la machine où vous avez commencé votre examen pour pouvoir le finir.")
                # mess_title = "Impossible d'accéder à cet examen."
                context.plone_utils.addPortalMessage(message, type=mess_type)
                return None

            dico_ETU = getIndividu(quser, "dict")

            """
            dico_ETU = getIndividu(quser, type="dict")
            if dico_ETU:
                firstname = dico_ETU["prenom"]
                lastname = dico_ETU["nom"]
            else:
                fullname = getDisplayName(quser, request)
                firstname, lastname = fullname.split(" ", 1)
            """

            # Sur une premiere erreur, on considere que l'utilisateur est inexistant.
            # on tente alors de le créer.
            user = context.wims("creerUser", {"quser": quser, "qclass": qclass,
                                              "firstname": dico_ETU["prenom"],
                                              "lastname":  dico_ETU["nom"]})
            if user["status"] == "ERROR":
                # Si la creation de l'utilisateur plante, alors WIMS doit être indisponible.
                context.plone_utils.addPortalMessage(message, type=mess_type)
                return None
            # dico = {"qclass": qclass, "quser": quser, "code": quser, "option": "lightpopup", "data1": remote_addr}
            rep = context.wims("authUser", dico)
            rep = context.wims("verifierRetourWims", {"rep": rep, "fonction": "jalon_utils/authUser",
                               "message": "impossible d'authentifier l'utilisateur %s. (Sur 2e essai)" % quser, "requete": dico})
        else:
            # L'authentification du supervisor a planté.
            # => WIMS doit être indisponible. (Ou WIMS a refusé la connexion.)
            # Cas possible : supervisor is in an exam session started on another IP
            context.plone_utils.addPortalMessage(message, type=mess_type)
            context.wims("verifierRetourWims", {"rep": rep, "fonction": "jalon_utils/authUser",
                         "message": "impossible d'authentifier le supervisor", "requete": dico})
            # LOG.info("**** authUser | Impossible d'authentifier le supervisor : %s" % rep)
            return None
    rep["url_connexion"] = url_connexion
    # LOG.info("**** authUser | rep = %s" % rep)
    return rep


def string_for_json(chaine):
    """string_for_json : Supprime tous les caracteres indesirables d'une chaine pour l'integrer au format JSON (quotes, retour chariot, barre oblique )."""
    return chaine.replace('\"', "'").replace('\n', "").replace("\\", "")


def convertirDate(date):
    """convertir Date."""
    return DateTime(date, datefmt='international').strftime("%d/%m/%Y %H:%M")


def convertLangToWIMS(portal_lang):
    """convertLangToWIMS : Converti un code de langue Plone en code de langue WIMS."""
    if portal_lang == "zh-cn":
        # Sur Wims, "cn" doit remplacer le code "zh-cn" de Jalon
        portal_lang = "cn"
    return portal_lang


def encodeUTF8(itemAEncoder):
    """encode itemAEncoder en UTF8."""
    try:
        return [str(encoder).encode("utf-8") for encoder in itemAEncoder]
    except:
        return itemAEncoder


def convertUTF8ToHTMLEntities(source):
    u"""iso-8859-1 ne permet pas d'encoder certains caracteres speciaux comme œ ou €."""
    source = source.replace("€", "&euro;")
    source = source.replace("œ", "&oelig;")
    source = source.replace("’", "&rsquo;")
    return source


def convertHTMLEntitiesToUTF8(source):
    u"""Pour éviter d'avoir des erreur XML 'unrecognized entity', on reconvertit en UTF-8."""
    source = source.replace("&euro;", "€")
    source = source.replace("&oelig;", "œ")
    source = source.replace("&rsquo;", "’")
    return source


def envoyerMail(form):
    u"""envoie un email selon les parametres spécifiés."""
    portal = getUtility(IPloneSiteRoot)
    jalon_properties = getToolByName(portal, "portal_jalon_properties")
    mail_properties = jalon_properties.getPropertiesCourriels()
    if "auteur" in form:
        message = "Message envoyé par %s depuis le cours %s\n\n%s" % (
            form["auteur"], form["cours"], form["message"])
    else:
        message = form["message"]

    if "de" not in form:
        form["de"] = portal.getProperty("email_from_address")
    if "a" not in form:
        if mail_properties["activer_email_erreur"]:
            form["a"] = mail_properties["adresse_email_erreur"]
        else:
            form["a"] = portal.getProperty("email_from_address")

    my_message = message_from_string(message)
    my_message.set_charset('utf-8')
    my_message['Subject'] = Header("[%s] %s" % (portal.Title(), form["objet"]), charset="utf-8")
    my_message['To'] = form["a"]
    my_message['From'] = "Jalon <no-reply@unice.fr>"  # portal.getProperty("email_from_address")
    my_message['Reply-To'] = form["de"]
    my_message['Date'] = email.Utils.formatdate(localtime=True)

    portal.MailHost.send(my_message,
                         mto=form["a"],
                         mfrom="Jalon <no-reply@unice.fr>",
                         subject="[%s] %s" % (portal.Title(), form["objet"]),
                         encode=None, immediate=False, charset='utf8', msg_type="text/html")


def envoyerMailErreur(form):
    # LOG.info("----- envoyerMailErreur -----")
    u"""envoie un email de signalement d'erreur à l'administrateur."""
    portal = getUtility(IPloneSiteRoot)
    jalon_properties = getToolByName(portal, "portal_jalon_properties")
    mail_properties = jalon_properties.getPropertiesCourriels()
    if mail_properties["activer_erreur"]:
        # LOG.info("Mail Erreur actif")
        if "de" not in form:
            if mail_properties["activer_email_erreur"]:
                form["de"] = mail_properties["adresse_email_erreur"]
            else:
                form["de"] = portal.getProperty("email_from_address")
        if "a" not in form:
            if mail_properties["activer_email_erreur"]:
                form["a"] = mail_properties["adresse_email_erreur"]
            else:
                form["a"] = portal.getProperty("email_from_address")

        # LOG.info("De : %s" % form["de"])
        # LOG.info("A  : %s" % form["a"])
        if "entry" in form:
            # error_log = portal.error_log
            # entries = error_log.getLogEntries()

            dico = {}
            entry = portal.error_log.getLogEntryById(form["entry"])
            if not entry:
                text = ""
            else:
                dico['date'] = DateTime(entry['time'])
                dico['username'] = "%s (%s)" % (entry['username'], entry['userid'])
                dico['url'] = entry['url']
                dico['type'] = entry['value']
                dico['value'] = entry['value']

                try:
                    dico['traceback'] = entry['tb_html']
                except:
                    dico['traceback'] = entry['tb_text']
                dico['request'] = entry['req_html']

                text = "\n\n".join(["Traceback", dico['traceback'], "Request", dico['request']])
            if ("__ac" not in text) or ("__accas" not in text):
                text = None
        else:
            text = form["message"]
        if text:
            # Create the enclosing (outer) message
            outer = MIMEMultipart()
            outer['Subject'] = Header(form["objet"], charset="utf-8")
            outer['To'] = form["a"]
            outer['From'] = form["de"]
            outer['Reply-To'] = form["de"]
            outer['Date'] = email.Utils.formatdate(localtime=True)
            outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
            # To guarantee the message ends with a newline
            outer.epilogue = ''

            # définition du message du mail
            msg = MIMEText(text, 'html', _charset="UTF-8")
            outer.attach(msg)

            # Now send the message
            s = smtplib.SMTP()
            s.connect(portal.MailHost.smtp_host, portal.MailHost.smtp_port)
            if portal.MailHost.smtp_uid:
                s.starttls()
                s.login(portal.MailHost.smtp_uid, portal.MailHost.smtp_pwd)

            s.sendmail(form["de"], form["a"], outer.as_string())

            s.close()


def getJalonProperty(key):
    portal = getUtility(IPloneSiteRoot)
    jalon_properties = getToolByName(portal, "portal_jalon_properties")
    if key.startswith("activer_"):
        return int(jalon_properties.getJalonProperty(key))
    return jalon_properties.getJalonProperty(key)


def flatten(lst):
    """ flatten. """
    for elem in lst:
        if type(elem) in (tuple, list):
            for i in flatten(elem):
                yield i
        else:
            yield elem


def getClefsDico(dico):
    """get Clefs Dico."""
    clefs = dico.keys()
    clefs.sort()
    return clefs


def getIndividu(sesame, type=None, portal=None):
    u"""getIndividu renvoie l'ensemble des infos disponibles (nom, prenom, mail, etc...) pour un sesame (login) en entree.

    # Si l'individu n'existe pas dans la base, il ne sera pas renvoyé.
    # si type="dict", les infos sont retraitées sous forme de dico.

    """
    if portal is None:
        portal = getUtility(IPloneSiteRoot)
    bdd = getToolByName(portal, 'portal_jalon_bdd')
    # retour de  getIndividuLITE :[[IND.LIB_NOM_PAT_IND,
    #                               IND.LIB_PR1_IND,
    #                               IND.SESAME_ETU,
    #                               IND.COD_ETU,
    #                               IND.EMAIL_ETU]]
    individu = bdd.getIndividuLITE(sesame)
    if type == "dict":
        if individu:
            dico = {"sesame":   sesame,
                    "id":       sesame,
                    "nom":      individu["LIB_NOM_PAT_IND"],
                    "prenom":   individu["LIB_PR1_IND"],
                    "fullname": ("%s %s" % (individu["LIB_NOM_PAT_IND"], individu["LIB_PR1_IND"])).encode("utf-8"),
                    "num_etu":  individu["COD_ETU"],
                    "email":    individu["EMAIL_ETU"]}
            return dico
        return {"sesame":   sesame,
                "id":       sesame,
                "nom":      sesame,
                "prenom":   sesame,
                "fullname": sesame,
                "num_etu":  sesame,
                "email":    sesame}

    return individu


def getIndividus(listeSesames, type=None, portal=None):
    u"""
    # getIndividus renvoie l'ensemble des infos disponibles (nom, prenom, mail, etc...) pour la liste des sesames (logins) en entree.

    # Si un individu n'existe pas dans la base, il ne sera pas renvoyé.
    # si type="dict", les infos sont retraitées sous forme de dico.

    """
    if portal is None:
        portal = getUtility(IPloneSiteRoot)
    bdd = getToolByName(portal, 'portal_jalon_bdd')
    # bdd = portal.portal_apogee
    recherche = bdd.getIndividus(listeSesames)
    if not type:
        return recherche
    if type == "dict":
        retour = {}
        for individu in recherche:
            retour[individu[2]] = {"nom":     individu[0],
                                   "prenom":  individu[1],
                                   "num_etu": individu[3],
                                   "email":   individu[4],
                                   "type":    individu[5]}
    if type == "listdict":
        retour = []
        for individu in recherche:
            retour.append({"sesame":  individu[2],
                           "nom":     individu[0],
                           "prenom":  individu[1],
                           "num_etu": individu[3],
                           "email":   individu[4],
                           "type":    individu[5]})
    return retour


def getLocaleDate(date, format="%d/%m/%Y"):
    locale.setlocale(locale.LC_ALL, 'fr_FR')
    return DateTime(date).strftime(format).decode("iso-8859-1")


def getConnectDate(data, sortable=False):
    if not sortable:
        return data.split(' - ')[0].replace('.', '/')
    else:
        dateList = data.replace('h', '').split(' - ')
        return ''.join(dateList[0].split('.')[::-1]) + dateList[1]


def isSameServer(url1, url2):
    u"""Renvoit TRUE si le serveur de l'url "url1" est identique à celui de l'URL "url2"."""
    server1 = urlparse(url1)
    server2 = urlparse(url2)
    return server1.netloc == server2.netloc


def getDepotDate(data, sortable=False):
    if not sortable:
        return data.replace(' -', '')
    else:
        dateList = data.replace('h', '').split(' - ')
        return ''.join(dateList[0].split('/')[::-1]) + dateList[1]


def getPhotoTrombi(login):
    # here.portal_membership.getPersonalPortrait(creator)
    # à mettre en config admin
    req = urllib2.Request(
        "http://camus.unice.fr/unicampus/images/Photos/%sApog0060931E.jpg" % login)
    req.add_header("Expires", "Mon, 26 Jul 1997 05:00:00 GMT")
    req.add_header("Last-Modified", datetime.today())
    req.add_header("Cache-Control", "no-store, no-cache, must-revalidate, post-check=0, pre-check=0")
    req.add_header("Pragma", "no-cache")
    req.add_header("Content-type", "image/jpeg")

    try:
        r = urllib2.urlopen(req)
        return r.read()
    except:
        return None


def getBaseAnnuaire():
    """get Base Annuaire."""
    portal = getUtility(IPloneSiteRoot)
    portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
    fiche_ldap = portal_jalon_properties.getPropertiesDonneesUtilisateurs("fiche_ldap")
    # fiche_ldap correspond au champ "Chemin vers une fiche de votre annuaire" des configs Jalon
    if "*-*" in fiche_ldap:
        liste = fiche_ldap.split("*-*")
        if len(liste) > 2:
            return {"base": liste[0],
                    "variable": liste[1],
                    "fin": liste[2]}
        return {"base": liste[0],
                "variable": liste[1],
                "fin": ""}

    return {"base": fiche_ldap,
            "variable": "",
            "fin": ""}


def getFicheAnnuaire(valeur, base=None):
    if not base:
        base = getBaseAnnuaire()
    return "".join([base['base'], valeur[base["variable"]], base["fin"]])

"""
def getInfosMembre(username):
    # Fournit un dico des infos du membre 'username'.
    portal = getUtility(IPloneSiteRoot)
    portal_membership = getToolByName(portal, "portal_membership")
    member = portal_membership.getMemberById(username)
    if member:
        # LOG.info("member ok")
        fullname = member.getProperty("fullname")
        # LOG.info("fullname : %s" % fullname)
        if not fullname:
            fullname = username
        email = member.getProperty("email")
        if not email:
            email = username
    else:
        # LOG.info("not member")
        fullname = email = str(username)
        if isLDAP():
            portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
            schema = portal_jalon_properties.getJalonProperty("schema_ldap")
            if schema == "supann":
                ldap = "ldap-plugin"
                member = rechercherUserLDAPSupann(username, "supannAliasLogin", ldap, True)
            if schema == "eduPerson":
                member = rechercherUserLDAPEduPerson(
                    username, "supannAliasLogin", "ldap-plugin", True)
            try:
                fullname = member[0]["name"]
                email = member[0]["email"]
            except:
                pass
    try:
        fullname = fullname.encode('utf-8')
    except:
        pass
    splitted_fullname = fullname.strip().rsplit(" ", 1)
    if len(splitted_fullname) > 1:
        prenom, nom = splitted_fullname
    else:
        prenom = "*UNDEFINED*"
        nom = fullname
    return {"id":       username,
            "fullname": fullname,
            "email":    email,
            "prenom":   prenom,
            "nom":      nom}
"""


def getCourseUserFolder(context, user_id):
    # LOG.info("----- getUserFolder -----")
    portal = context.portal_url.getPortalObject()
    return getattr(portal.cours, user_id)


def rechercherUtilisateur(username, typeUser, match=False, isJson=True):
    u"""recherche des utilisateurs du type 'typeUser' correspondant au critère 'username'."""
    portal = getUtility(IPloneSiteRoot)
    retour = []

    portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")
    retour = portal_jalon_bdd.rechercherUtilisateursByName(username, typeUser)

    # Dans le cas ou l'enseignant n'existe pas dans la base de données,
    # on effectue tout de même une recherche LDAP (si possible)
    if len(retour) < 1 and isLDAP() and typeUser == "Personnel":
        portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
        schema = portal_jalon_properties.getJalonProperty("schema_ldap")
        if schema == "supann":
            ldap = "ldap-plugin"
            if typeUser == "Etudiant":
                ldap = "ldap-plugin-etu"
            retour = rechercherUserLDAPSupann(username, "displayName", ldap, match)
        if schema == "eduPerson":
            retour = rechercherUserLDAPEduPerson(username, "displayName", "ldap-plugin", match)

    # LOG.info("retour = %s" % retour)

    if isJson:
        return json.dumps(retour)
    return retour


def rechercherUserLDAPSupann(username, attribut, ldap="ldap-plugin", match=False):
    retour = []
    portal = getUtility(IPloneSiteRoot)
    acl_users = getattr(getattr(getattr(portal, "acl_users"), ldap), "acl_users")
    for user in acl_users.findUser(search_param=attribut, search_term=username, exact_match=match):
        if "supannAliasLogin" in user:
            email = user["supannAliasLogin"]
            if "mail" in user:
                email = user["mail"].decode("iso-8859-1")
            retour.append({"id":    user["supannAliasLogin"],
                           "name":  "%s (%s)" % (user["displayName"].decode("iso-8859-1"), user["supannAliasLogin"]),
                           "email": email})
    return retour


def rechercherUserLDAPEduPerson(username, attribut, ldap="ldap-plugin", match=False):
    retour = []
    portal = getUtility(IPloneSiteRoot)
    eduPersonAffiliation = ["employee", "faculty"]
    if ldap == "ldap-plugin-etu":
        eduPersonAffiliation = ["student"]
    acl_users = getattr(getattr(getattr(portal, "acl_users"), ldap), "acl_users")
    for user in acl_users.findUser(search_param=attribut, search_term=username, exact_match=match):
        if "login" in user and user["eduPersonAffiliation"] in eduPersonAffiliation:
            email = user["login"]
            if "mail" in user:
                email = user["mail"].decode("iso-8859-1")
            retour.append({"id":    user["login"],
                           "name":  user["displayName"].decode("iso-8859-1"),
                           "email": email})
    return retour


def getShortText(text, limit=75, suffix=u'…'):
    u"""
        Troncature de texte.

    Remplace les espaces multiples, sauts de ligne, retours chariot et
    tabulations par des espaces.
    Coupe entre les mots avec prise en compte de la ponctuation et des espaces
    insécables.
    Effectue un tronçonnage simple si la partie à conserver de la chaîne ne
    contient aucun espace.

    Args:
        text (str):             le texte a tronquer
        limit (optional[int]):  la longueur maxi souhaitée
        suffix (optional[str]): le caractère à ajouter à la fin

    Returns:
        text (str):             le texte tronqué

    """
    text = re.sub(r'\s+', r' ', text.decode('utf8').strip())
    if len(text) > limit:
        text = text[:limit + 1]
        if text.find(u' ') > -1:
            text = u' '.join(text.split(u' ')[:-1])
            limit = len(text)
        return "".join([text[0:limit].rstrip(u'?!:;.,-" “”«» '), suffix]).encode("utf-8")
    else:
        return text.encode("utf-8")


def getPlainShortText(html, limit=75):
    u"""
        Troncature de contenu HTML.

    Renvoie le retour de getShortText() ci-dessus appliqué au contenu texte brut.

    Args:
        html (str):             le contenu HTML à tronquer
        limit (optional[int]):  la longueur maxi souhaitée

    Returns:
        (str):                  le contenu brut tronqué

    """
    return getShortText(supprimerMarquageHTML(html), limit)


def isLDAP():
    portal = getUtility(IPloneSiteRoot)
    portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
    return portal_jalon_properties.getPropertiesDonneesUtilisateurs("activer_ldap")


def setTag(context, tag):
    if tag not in context.Subject():
        tags = list(context.Subject())
        tags.append(tag)
        context.setSubject(tuple(tags))
        context.reindexObject()


def supprimerMarquageHTML(chaine):
    """Suppression marquage HTML."""
    return re.sub('<[^<]+?>', '', chaine)


def remplaceChaine(chaine, elements):
    """Remplacement d'éléments dans une chaîne."""
    for prev, new in elements.iteritems():
        chaine = chaine.replace(prev, new)
    return chaine


def supprimerCaractereSpeciaux(chaine):
    u"""
        "Nettoyage" d'une chaîne de caractères.

    Remplace les caractères accentués par leur équivalent alphanumérique,
    supprime tous les autres caractères non alphanumériques ainsi que les
    tabulations, retours chariot et espaces multiples.

    Args:
        chaine (str):   la chaîne à traiter

    Returns:
        (str):          le résultat du traitement

    """
    accents = { 'a': ['à', 'ã', 'á', 'â', '@', 'ª'],
                'A': ['À', 'Á', 'Â', 'Ä'],
                'AE':['Æ'],
                'ae':['æ'],
                'B': ['ß'],
                'c': ['ç', '¢'],
                'C': ['Ç', '©'],
                'e': ['é', 'è', 'ê', 'ë', '&'],
                'E': ['È', 'É', 'Ê', 'Ë', '€'],
                'i': ['î', 'ï', 'ì', 'í'],
                'I': ['Ì', 'Í', 'Î', 'Ï'],
                'L': ['£'],
                'n': ['ñ'],
                'N': ['Ñ'],
                'o': ['ô', 'ö', 'ò', 'ó', 'ø', 'õ'],
                'O': ['Ò', 'Ó', 'Ô', 'Õ', 'Ö', 'Ø'],
                'oe':['œ'],
                'OE':['Œ'],
                'R': ['®'],
                'u': ['ù', 'ü', 'û', 'µ', 'ú'],
                'U': ['Ù', 'Ú', 'Û', 'Ü'],
                'S': ['$', 'š', 'Š'],
                'x': ['×'],
                'y': ['¥', 'Ý','Ÿ', 'ý', 'ÿ'],
                '_': [' '] }
    chaine = re.sub(r'\s+', r' ', chaine.strip())
    for (char, accentedChars) in accents.iteritems():
        for accentedChar in accentedChars:
            chaine = chaine.replace(accentedChar, char)
    return re.sub('[^\w]', '', chaine)


def test(condition, valeurVrai, valeurFaux):
    return valeurVrai if condition else valeurFaux


def tagFormat(tagSet):
    tagList = tagSet.split(',')
    if 'last' in tagList:
        tagList.remove('last')
    if len(tagList) > 0:
        return ','.join(tagList)
    else:
        return None


def jalon_quote(encode):
    return urllib.quote(encode)


def jalon_unquote(decode):
    """
    Replace %xx escapes by their single-character equivalent.

    Example: unquote('/%7Econnolly/') yields '/~connolly/'.

    """
    return urllib.unquote(decode)


def jalon_urlencode(chaine):
    return urllib.urlencode(chaine)


def isAfficherElement(affElement, masquerElement):
    # LOG.info("***** affElement : %s" % affElement)
    if not affElement:
        return {"val": 0, "icon": "fa-eye-slash", "legende": "Masqué"}
    if cmp(DateTime(), affElement) == -1:
        return {"val": 0, "icon": "fa-calendar-o success", "legende": u"Affichage programmé au %s à %s." % (getLocaleDate(affElement, format="%d/%m/%Y"), getLocaleDate(affElement, format="%Hh%M"))}
    if not masquerElement:
        return {"val": 1, "icon": "", "legende": "Masquage non programmé"}
    if cmp(masquerElement, DateTime()) == -1:
        return {"val": 0, "icon": "fa-eye-slash", "legende": "Date de masquage programmé depassée."}
    return {"val": 1, "icon": "", "icon2": "fa-calendar-o alert", "legende": u"Masquage programmé au %s à %s." % (getLocaleDate(masquerElement, format="%d/%m/%Y"), getLocaleDate(masquerElement, format="%Hh%M"))}


"""
def isAfficherElement(affElement, masquerElement):
    if not affElement:
        return {"val": 0, "icon": "fa-eye-slash", "legende": "masqué"}
    if cmp(DateTime(), affElement) == -1:
        return {"val": 0, "icon": "fa-calendar-o success", "legende": "affichage programmé au %s" % getLocaleDate(affElement, format="%d/%m/%Y à %Hh%M")}
    if not masquerElement:
        return {"val": 1, "icon": "",, "legende": "affiché"}
    if cmp(masquerElement, DateTime()) == -1:
        return {"val": 0, "icon": "fa-eye-slash", "legende": "masquage programmé et depassé"}
    return {"val": 1, "icon": "", "icon2": "fa-calendar-o alert", "legende": "masquage programmé au %s" % getLocaleDate(masquerElement, format="%d/%m/%Y à %Hh%M")}
"""


def retirerEspace(mot):
    motSansEspace = mot.strip()
    motSansEspace = motSansEspace.replace(" ", "")
    motSansEspace = motSansEspace.replace("%20", "")
    return motSansEspace


def getFooter():
    portal = getUtility(IPloneSiteRoot)
    jalon_properties = getToolByName(portal, "portal_jalon_properties")
    dico = copy.copy(jalon_properties.getPropertiesInfos())
    dico["site"] = portal.Title()
    dico["activer_aide"] = jalon_properties.getJalonProperty("activer_aide")
    dico["lien_aide"] = jalon_properties.getJalonProperty("lien_aide")
    return dico


def gaEncodeTexte(chemin, texte):
    return jalon_encode.encodeTexte(chemin, texte)


class MissingExtension(Exception):
    """Exception when the filename has no extension."""


def get_id_from_filename(filename, context):
    from zope import component
    from plone.i18n.normalizer.interfaces import IIDNormalizer
    charset = getattr(context, 'getCharset', None) and context.getCharset()\
        or 'utf-8'
    name = filename.decode(charset).rsplit('.', 1)
    if len(name) != 2:
        raise MissingExtension('It seems like the file extension is missing.')
    normalizer = component.getUtility(IIDNormalizer)
    newid = '.'.join((normalizer.normalize(name[0]), name[1]))
    newid = newid.replace('_', '-').replace(' ', '-').lower()
    return newid
