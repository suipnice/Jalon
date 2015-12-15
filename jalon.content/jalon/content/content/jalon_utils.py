# -*- coding: utf-8 -*-
""" Jalon utilities. """

from zope.component import getUtility

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from jalon.content.browser.config.jalonconfig import IJalonConfigControlPanel
from jalon.content.browser.config.jalonconfiguration import IJalonConfigurationControlPanel
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
import feedparser
import locale
import json
import re
import copy

# Messages de debug :
from logging import getLogger
LOG = getLogger('[jalon_utils]')
"""
# Log examples :
LOG.debug('debug message')
LOG.info('info message')
LOG.warn('warn message')
LOG.error('error message')
LOG.critical('critical message')
"""


def authUser(context, quser=None, qclass=None, request=None, session_keep=False):
    u""" AuthUser WIMS : permet d'authentifier "quser" dans une classe wims "qclass".

    # request représente les parametres envoyés à la page (GET/POST)
    # session_keep permet de définir si on réutilise une eventuelle session wims existante ou pas.

    """
    remote_addr = None
    url_connexion = context.wims("getAttribut", "url_connexion")
    if request:
        # HTTP_X_REAL_IP n'existe que si la configuration de Nginx fournit bien ce parametre à Zope.
        remote_addr = request.get('HTTP_X_REAL_IP', None)
        if not remote_addr:
            remote_addr = request['REMOTE_ADDR']

        if session_keep == True:
            #Si session_keep=True et qu'une session wims était déjà ouverte, on la conserve.
            # Attention : ici il faudrait vérifier sur WIMS que la session ouverte était bien celle de l'utilisateur courant.
            wims_session = request.get('wims_session', None)
            if wims_session:
                return {'wims_session': wims_session,
                        'status':       'OK',
                        'home_url':     "%s?session=%s" % (url_connexion, wims_session)}
    dico = {"qclass": qclass, "quser": quser, "code": quser, "option": "lightpopup", "data1": remote_addr}
    rep = context.wims("authUser", dico)
    try:
        rep = json.loads(rep)
        #rep = context.wims("verifierRetourWims", {"rep": rep, "fonction": "jalon.content/jalon_utils.py/authUser", "message": "1ere identification de l'utilisateur %s." % quser, "requete": dico})
    except ValueError, e:
            rep = '{"status":"ERROR","exception_raised":"%s","message":"%s"}' % (string_for_json(rep), e)
            rep = json.loads(rep)

    if rep["status"] == "ERROR":
        # On prépare un éventuel message d'erreur à renvoyer
        message = _(u"Le serveur WIMS est actuellement injoignable. Merci de réessayer ultérieurement svp...")
        mess_type = "error"
        if quser != 'supervisor':

            dico_ETU = getInfosMembre(quser)

            """
            dico_ETU = getIndividu(quser, type="dict")
            if dico_ETU:
                firstname = dico_ETU["prenom"]
                lastname = dico_ETU["nom"]
            else:
                fullname = getDisplayName(quser, request)
                firstname, lastname = fullname.split(" ", 1)
            """

            # Sur une premiere erreur, on considere que l'utilisateur est inexistant. on tente alors de le créer.
            user = context.wims("creerUser", {"quser": quser, "qclass": qclass, "firstname": dico_ETU["prenom"], "lastname": dico_ETU["nom"]})
            if user["status"] == "ERROR":
                # Si la creation de l'utilisateur plante, alors WIMS doit être indisponible.
                context.plone_utils.addPortalMessage(message, type=mess_type)
                return None
            rep = context.wims("authUser", {"qclass": qclass, "quser": quser, "code": quser, "option": "lightpopup", "remote_addr": remote_addr})
            rep = context.wims("verifierRetourWims", {"rep": rep, "fonction": "jalon.content/jalon_utils.py/authUser", "message": "impossible d'authentifier l'utilisateur %s. (Sur 2e essai)" % quser, "requete": dico})
        else:
            # L'authentification du supervisor a planté => WIMS doit être indisponible.
            context.plone_utils.addPortalMessage(message, type=mess_type)
            return None
    rep["url_connexion"] = url_connexion
    return rep


def string_for_json(self, chaine):
    """string_for_json : Supprime tous les caracteres indesirables d'une chaine pour l'integrer au format JSON (quotes, retour chariot, barre oblique )."""
    return chaine.replace('\"', "'").replace('\n', "").replace("\\", "")


def convertirDate(date):
    """ convertir Date."""
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


def envoyerMail(form):
    u""" envoie un email selon les parametres spécifiés."""
    portal = getUtility(IPloneSiteRoot)
    jalon_properties = getToolByName(portal, "portal_jalon_properties")
    mail_properties = jalon_properties.getPropertiesCourriels()
    if "auteur" in form:
        message = "Message envoyé par %s depuis le cours %s\n\n%s" % (form["auteur"], form["cours"], form["message"])
    else:
        message = form["message"]

    if not "de" in form:
        form["de"] = portal.getProperty("email_from_address")
    if not "a" in form:
        if mail_properties["activer_email_erreur"]:
            form["a"] = mail_properties["adresse_email_erreur"]
        else:
            form["a"] = portal.getProperty("email_from_address")

    my_message = message_from_string(message)
    my_message.set_charset('utf-8')
    my_message['Subject'] = Header("[%s] %s" % (portal.Title(), form["objet"]), charset="utf-8")
    my_message['To'] = form["a"]
    my_message['From'] = portal.getProperty("email_from_address")
    my_message['Reply-To'] = form["de"]
    my_message['Date'] = email.Utils.formatdate(localtime=True)

    portal.MailHost.send(my_message,
                         mto=form["a"],
                         mfrom=portal.getProperty("email_from_address"),
                         subject="[%s] %s" % (portal.Title(), form["objet"]),
                         encode=None, immediate=False, charset='utf8', msg_type="text/html")


def envoyerMailErreur(form):
    u""" envoie un email de signalement d'erreur à l'administrateur."""
    portal = getUtility(IPloneSiteRoot)
    jalon_properties = getToolByName(portal, "portal_jalon_properties")
    mail_properties = jalon_properties.getPropertiesCourriels()
    if mail_properties["activer_erreur"]:
        if not "de" in form:
            if mail_properties["activer_email_erreur"]:
                form["de"] = mail_properties["adresse_email_erreur"]
            else:
                form["de"] = portal.getProperty("email_from_address")
        if not "a" in form:
            if mail_properties["activer_email_erreur"]:
                form["a"] = mail_properties["adresse_email_erreur"]
            else:
                form["a"] = portal.getProperty("email_from_address")

        if "entry" in form:
            #error_log = portal.error_log
            #entries = error_log.getLogEntries()

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
            if (not "__ac" in text) or (not "__accas" in text):
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


def getAttributConf(attribut):
    portal = getUtility(IPloneSiteRoot)
    jalon_conf = IJalonConfigControlPanel(portal)
    return jalon_conf.__getattribute__("get_%s" % attribut)()


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


""" [DEPRECATED]

def getDisplayName(user_id, request=None, portal=None):
    #""
    getDisplayName permet d'obtenir le nom (+prenom) d'un utilisateur.

    maintenant, il faut utiliser getInfosMembre(user_id)
    # nb : request est utilisé dans le cas d'utilisateurs sygefor

    #""
    if portal == None:
        portal = getUtility(IPloneSiteRoot)
    member = portal.portal_membership.getMemberById(user_id)
    fullname = None
    if member:
        if member.has_role(["Personnel", "Etudiant", "Manager"]):
            fullname = member.getProperty("fullname")
        if (not fullname) and member.has_role(["Personnel", "Etudiant"]):
            fullname = member.getProperty("displayName")
        if not fullname:
            sygefor = getattr(portal.acl_users, "sygefor", None)
            if sygefor:
                result = sygefor.getPropertiesForUser(user_id, request)
                if result:
                    fullname = result.getProperty("fullname")
            if not fullname:
                fullname = "%s %s" % (user_id, user_id)
    else:
        fullname = "utilisateur introuvable"
    return fullname
"""


def getIndividu(sesame, type=None, portal=None):
    u""" getIndividu renvoie l'ensemble des infos disponibles (nom, prenom, mail, etc...) pour un sesame (login) en entree.

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
            #individu = individu[0]
            dico = {"sesame": sesame,
                    "nom": individu["LIB_NOM_PAT_IND"],
                    "prenom": individu["LIB_PR1_IND"],
                    "num_etu": individu["COD_ETU"],
                    "email": individu["EMAIL_ETU"]}
            return dico
        return None

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
    #bdd = portal.portal_apogee
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
    return DateTime(date).strftime(format)


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
    #here.portal_membership.getPersonalPortrait(creator)
    # à mettre en config admin
    req = urllib2.Request("http://camus.unice.fr/unicampus/images/Photos/%sApog0060931E.jpg" % login)
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


def getInfosConnexion():
    portal = getUtility(IPloneSiteRoot)
    jalon_configuration = IJalonConfigurationControlPanel(portal)
    return {"site":          portal.Title(),
            "lien_sesame":   jalon_configuration.get_lien_sesame(),
            "etablissement": jalon_configuration.get_etablissement()}


def getInfosMembre(username):
    """ Fournit un dico des infos du membre 'username'."""
    portal = getUtility(IPloneSiteRoot)
    portal_membership = getToolByName(portal, "portal_membership")
    member = portal_membership.getMemberById(username)
    if member:
        #LOG.info("member ok")
        fullname = member.getProperty("fullname")
        #LOG.info("fullname : %s" % fullname)
        if not fullname:
            fullname = username
        email = member.getProperty("email")
        if not email:
            email = username
    else:
        #LOG.info("not member")
        fullname = email = str(username)
        if isLDAP():
            portal_jalon_properties = getToolByName(portal, 'portal_jalon_properties')
            schema = portal_jalon_properties.getJalonProperty("schema_ldap")
            if schema == "supann":
                ldap = "ldap-plugin"
                member = rechercherUserLDAPSupann(username, "supannAliasLogin", ldap, True)
            if schema == "eduPerson":
                member = rechercherUserLDAPEduPerson(username, "supannAliasLogin", "ldap-plugin", True)
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


def rechercherUtilisateur(username, typeUser, match=False, isJson=True):
    u"""recherche des utilisateurs du type 'typeUser' correspondant au critère 'username'."""
    portal = getUtility(IPloneSiteRoot)
    retour = []

    portal_jalon_bdd = getToolByName(portal, "portal_jalon_bdd")
    retour = portal_jalon_bdd.rechercherUtilisateursByName(username, typeUser)

    #Dans le cas ou l'enseignant n'existe pas dans la base de données,
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

    #LOG.info("retour = %s" % retour)

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
                           "name":  user["displayName"].decode("iso-8859-1"),
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


def getShortText(text, limit=75, suffix='…'):
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
    text = re.sub(r'\s+', r' ', text.strip())
    if len(text) > limit:
        text = text[:limit + 1]
        if text.find(' ') > -1:
            text = ' '.join(text.split(' ')[:-1])
            limit = len(text)
        return text[0:limit].rstrip('?!:;.,-" “”«» ') + suffix
    else:
        return text


def getPlainShortText(html, limit=75):
    u"""
        Troncature de contenu CKEditor (HTML).

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
    if not tag in context.Subject():
        tags = list(context.Subject())
        tags.append(tag)
        context.setSubject(tuple(tags))
        context.reindexObject()


def supprimerMarquageHTML(chaine):
    """Suppression marquage HTML."""
    return re.sub('<[^<]+?>', '', chaine)


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


def jalon_rss():
    portal = getUtility(IPloneSiteRoot)
    jalon_conf = IJalonConfigControlPanel(portal)
    url_maj = jalon_conf.get_url_maj()
    try:
        f = feedparser.parse(url_maj)
    except:
        print "Une erreur"
        return None

    if len(f['entries']) > 0:
        return f['entries'][0]
    print "Aucune entrées"
    return None


def isAfficherElement(affElement, masquerElement):
    if not affElement:
        return {"val": 0, "icon": "fa-eye-slash", "icon2": "", "legende": "affichage non programmé"}
    if cmp(DateTime(), affElement) == -1:
        return {"val": 0, "icon": "fa-eye-slash", "icon2": "fa-calendar-o success", "legende": "affichage programmé au %s" % getLocaleDate(affElement, format="%d/%m/%Y à %Hh%M")}
    if not masquerElement:
        return {"val": 1, "icon": "", "icon2": "", "legende": "masquage non programmé"}
    if cmp(masquerElement, DateTime()) == -1:
        return {"val": 0, "icon": "fa-eye-slash", "icon2": "", "legende": "masquage programmé et depassé"}
    return {"val": 1, "icon": "", "icon2": "fa-calendar-o alert", "legende": "masquage programmé au %s" % getLocaleDate(masquerElement, format="%d/%m/%Y à %Hh%M")}


def retirerEspace(mot):
    motSansEspace = mot.strip()
    motSansEspace = motSansEspace.replace(" ", "")
    motSansEspace = motSansEspace.replace("%20", "")
    return motSansEspace


def getFilAriane(portal, folder, authMemberId, page=None):
    url_portal = portal.absolute_url()
    #print "jalon_utils/getFilAriane folder.getId() = %s" %folder.getId()

    if authMemberId != None:
        # Cas d'un utilisateur connecté
        dico_mes_cours = {"titre": _(u"Mes cours"),
                          "icone": "fa fa-university",
                          "url":   "%s/cours/%s" % (url_portal, authMemberId)}
    else:
        # Cas d'un utilisateur anonyme dans un cours public
        dico_mes_cours = {"titre": portal.Title(),
                          "icone": "fa fa-university",
                          "url":   url_portal}

    if folder.getId().startswith("Cours"):
        if not page:
            return [dico_mes_cours,
                    {"titre": folder.Title(),
                     "icone": "fa fa-book"}]
        if page == "pref":
            return [dico_mes_cours,
                    {"titre": folder.Title(),
                     "icone": "fa fa-book",
                     "url"  : folder.absolute_url()},
                    {"titre": "Accès et options",
                     "icone": "fa fa-cogs"}]
        if page == "annonces":
            return [dico_mes_cours,
                    {"titre": folder.Title(),
                     "icone": "fa fa-book",
                     "url"  : folder.absolute_url()},
                    {"titre": "Toutes les annonces",
                     "icone": "fa fa-bullhorn"}]
        if page == "actualites":
            return [dico_mes_cours,
                    {"titre": folder.Title(),
                     "icone": "fa fa-book",
                     "url"  : folder.absolute_url()},
                    {"titre": "Toutes les nouveautés",
                     "icone": "fa fa-bell-o"}]

    liste = [dico_mes_cours,
             {"titre": folder.aq_parent.title_or_id(),
              "icone": "fa fa-book",
               "url":   folder.aq_parent.absolute_url()}]

    if folder.getId().startswith("BoiteDepot"):
        liste.append({"titre": folder.Title(),
                      "icone": "fa fa-inbox"})
        return liste

    if folder.getId().startswith("AutoEvaluation"):
        if page == "auto":
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-gamepad",
                          "url"  : folder.absolute_url()})
            liste.append({"titre": "Exercice(s)",
                          "icone": "fa fa-random"})
        if not page:
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-gamepad"})
        return liste

    if folder.getId().startswith("Examen"):
        #print "jalon_utils/getFilAriane page = %s" % page
        if page in ["examen", "auto"]:
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-graduation-cap",
                          "url"  : folder.absolute_url()})
            liste.append({"titre": "Examen en cours",
                          "icone": "fa fa-graduation-cap"})
        if not page:
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-graduation-cap"})
        return liste

    if folder.meta_type == "Ploneboard":
        if page == "jalon_forum_search":
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-comments",
                          "url":   folder.absolute_url()})
            liste.append({"titre": "Recherche",
                          "icone": "fa fa-search"})
            return liste
        if page == "ploneboard_recent":
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-comments",
                          "url":   folder.absolute_url()})
            liste.append({"titre": "Activité récente",
                          "icone": "fa fa-comment"})
            return liste
        if page == "ploneboard_unanswered":
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-comments",
                          "url":   folder.absolute_url()})
            liste.append({"titre": "Conversations sans réponse",
                          "icone": "fa fa-comment-o"})
            return liste
        liste.append({"titre": folder.Title(),
                      "icone": "fa fa-comments"})
        return liste

    if folder.meta_type == "PloneboardForum":
        if page == "ploneboard_unanswered":
            liste.append({"titre": folder.aq_parent.aq_parent.title_or_id(),
                          "icone": "fa fa-book",
                          "url"  : folder.aq_parent.aq_parent.absolute_url()})
            liste.append({"titre": folder.Title(),
                          "icone": "fa fa-comments",
                          "url"  : folder.absolute_url()})
            liste.append({"titre": "Conversations sans réponse",
                          "icone": "fa fa-comment-o"})
            return liste
        return [dico_mes_cours,
                {"titre": folder.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-book",
                 "url":   folder.aq_parent.aq_parent.absolute_url()},
                {"titre": folder.aq_parent.title_or_id(),
                 "icone": "fa fa-comments",
                 "url":   folder.aq_parent.absolute_url()},
                {"titre": folder.Title(),
                 "icone": "fa fa-comments"}]

    if folder.meta_type == "PloneboardConversation":
        return [dico_mes_cours,
                {"titre": folder.aq_parent.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-book",
                 "url":   folder.aq_parent.aq_parent.aq_parent.absolute_url()},
                {"titre": folder.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-comments",
                 "url":   folder.aq_parent.aq_parent.absolute_url()},
                {"titre": folder.aq_parent.title_or_id(),
                 "icone": "fa fa-comments",
                 "url":   folder.aq_parent.absolute_url()},
                {"titre": folder.Title(),
                 "icone": "fa fa-comments-o"}]

    if folder.meta_type == "PloneboardComment":
        return [dico_mes_cours,
                {"titre": folder.aq_parent.aq_parent.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-book",
                 "url":   folder.aq_parent.aq_parent.aq_parent.aq_parent.absolute_url()},
                {"titre": folder.aq_parent.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-comments",
                 "url":   folder.aq_parent.aq_parent.aq_parent.absolute_url()},
                {"titre": folder.aq_parent.aq_parent.title_or_id(),
                 "icone": "fa fa-comments",
                 "url":   folder.aq_parent.absolute_url()},
                {"titre": folder.Title(),
                 "icone": "fa fa-comments-o"}]

    if folder.meta_type == "JalonExerciceWims":
        return [{"titre": _(u"Mon espace"),
                 "icone": "fa fa-home",
                 "url":   url_portal},
                {"titre": _(u"Exercices Wims"),
                 "icone": "fa fa-random",
                 "url":   folder.aq_parent.absolute_url()},
                {"titre": folder.Title(),
                 "icone": "fa fa-random"}]

    if folder.getId() == "portal_jalon_properties":
        liste = []
        if not page:
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs"})
        if page == "gestion_connexion":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Connexion à Jalon"),
                          "icone": "fa fa-key"})
        if page == "gestion_mon_espace":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Gestion \"Mon Espace\""),
                          "icone": "fa fa-home"})
        if page == "gestion_mes_cours":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Gestion des Cours"),
                          "icone": "fa fa-university"})
        if page == "gestion_infos":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Liens d'informations"),
                          "icone": "fa fa-external-link-square"})
        if page == "gestion_didacticiels":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Didacticiels"),
                          "icone": "fa fa-life-ring"})
        if page == "gestion_messages":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Diffusion de messages"),
                          "icone": "fa fa-bullhorn"})
        if page == "gestion_email":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Courriels"),
                          "icone": "fa fa-envelope-o"})
        if page == "gestion_donnees_utilisateurs":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Données utilisateurs"),
                          "icone": "fa fa-users"})
        if page == "gestion_ga":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Google Analytics"),
                          "icone": "fa fa-line-chart"})
        if page == "gestion_maintenance":
            liste.append({"titre": _(u"Configuration de Jalon"),
                          "icone": "fa fa-cogs",
                          "url"  : "%s/@@jalon-configuration" % folder.absolute_url()})
            liste.append({"titre": _(u"Maintenance"),
                          "icone": "fa fa-umbrella"})
        return liste

    if folder.getId() == "portal_jalon_bdd":
        liste = []
        if page:
            authMember = portal.portal_membership.getAuthenticatedMember()
            redirection = "@@jalon-bdd?gestion=gestion_bdd"
            if authMember.has_role("Secretaire"):
                redirection = "gestion_utilisateurs"
            liste.append({"titre": _(u"Gestion pédagogique"),
                          "icone": "fa fa-database",
                          "url":   "%s/%s" % (folder.absolute_url(), redirection)})
            liste.append({"titre": page.encode("utf-8"),
                          "icone": "fa fa-database"})
        if not page:
            liste.append({"titre": _(u"Gestion pédagogique"),
                          "icone": "fa fa-database"})
        return liste

    fil = {portal.getId():  [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home"}],
           "Fichiers":      [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Fichiers"),
                              "icone": "fa fa-files-o"}],
           "Sonorisation":  [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Présentations sonorisées"),
                              "icone": "fa fa-microphone"}],
           "Wims":          [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Exercices Wims"),
                              "icone": "fa fa-random"}],
           "Externes":      [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Ressources externes"),
                              "icone": "fa fa-external-link"}],
           "Glossaire":     [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Terme de glossaire"),
                              "icone": "fa fa-font"}],
           "Webconference": [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Webconférences"),
                              "icone": "fa fa-headphones"}],
           "Video":         [{"titre": _(u"Mon espace"),
                              "icone": "fa fa-home",
                              "url":   url_portal},
                             {"titre": _(u"Vidéos"),
                              "icone": "fa fa-youtube-play"}],
           authMemberId:   [{"titre": _(u"Mes cours"),
                             "icone": "fa fa-university"}],
           "etudiants":    [{"titre": _(u"Mes étudiants"),
                             "icone": "fa fa-users"}],
           "portal_jalon_properties": [{"titre": _(u"Configuration du site"),
                                        "icone": "fa fa-wrench"}]}

    if page == "videos_pod":
        return [{"titre": _(u"Mon espace"),
                 "icone": "fa fa-home",
                 "url":   url_portal},
                {"titre": _(u"Vidéos"),
                 "icone": "fa fa-youtube-play",
                 "url": folder.absolute_url()},
                {"titre": _(u"Rechercher une vidéo"),
                 "icone": "fa fa-search"}]

    if not folder.getId() in fil:
        return [dico_mes_cours]
    return fil[folder.getId()]


def getElementView(context, typeContext, idElement, createurElement=None, typeElement=None, indexElement=None, mode_etudiant=None):
    portal = context.portal_url.getPortalObject()
    retour = {"titreElement":       "",
              "descriptionElement": "",
              "urlElement":         ""}

    if "*-*" in idElement:
        idElement = idElement.replace("*-*", ".")

    if typeContext == "Cours":
        retour["indexElement"] = indexElement

        typeElement = typeElement.replace("%20", "")
        typeElement = typeElement.replace(" ", "")

        if typeElement in ["AutoEvaluation", "BoiteDepot", "Examen", "Forum"]:
            boite = getattr(context, idElement)
            retour["titreElement"] = boite.Title()
            retour["descriptionElement"] = boite.Description().replace("\n", "<br/>")
            if typeElement == "AutoEvaluation":
                retour["urlElement"] = "%s/%s/cours_wims_view?mode_etudiant=%s" % (context.absolute_url(), idElement, mode_etudiant)
            if typeElement == "BoiteDepot":
                retour["urlElement"] = "%s/%s?mode_etudiant=%s" % (context.absolute_url(), idElement, mode_etudiant)
            if typeElement == "Examen":
                retour["urlElement"] = "%s/%s/cours_wims_view?mode_etudiant=%s" % (context.absolute_url(), idElement, mode_etudiant)
            if typeElement == "Forum":
                retour["urlElement"] = "%s/%s?section=forum" % (context.absolute_url(), idElement)
            return retour
        if typeElement == "SalleVirtuelle":
            infos_element = context.getElementCours(idElement)
            retour["titreElement"] = infos_element["titreElement"]
            retour["urlElement"] = context.getWebconferenceUrlById(createurElement, idElement)
            return retour
        if typeElement == "Glossaire":
            retour["idElement"] = context.getId()
            retour["titreElement"] = "Glossaire"
            retour["urlElement"] = "%s/cours_glossaire_view" % context.absolute_url()
            return retour

        dicoRep = {"File":                    "Fichiers",
                   "Image":                   "Fichiers",
                   "Page":                    "Fichiers",
                   "ExercicesWims":           "Wims",
                   "Lienweb":                 "Externes",
                   "Lecteurexportable":       "Externes",
                   "CatalogueBU":             "Externes",
                   "Video":                     "Video",
                   "Presentationssonorisees": "Sonorisation",
                   "TermeGlossaire":          "Glossaire"}

        if typeElement in dicoRep:
            rep = dicoRep[typeElement]
        else:
            rep = typeElement

        home = getattr(getattr(portal.Members, createurElement), rep, None)
    else:
        home = context

    if home:
        element = getattr(home, idElement, None)
        if not typeElement:
            typeElement = element.portal_type
            if typeElement == "JalonRessourceExterne":
                typeElement = element.getTypeRessourceExterne()
                typeElement = typeElement.replace("%20", "")
                typeElement = typeElement.replace(" ", "")
            if typeElement == "JalonTermeGlossaire":
                typeElement = "TermeGlossaire"
        if element:
            retour["idElement"] = element.getId()
            retour["titreElement"] = element.Title()
            retour["descriptionElement"] = element.Description().replace("\n", "<br/>")
            retour["urlElement"] = element.absolute_url()
            retour["typeElement"] = typeElement
            if typeElement == 'File':
                retour["urlElement"] = '%s/at_download/file' % element.absolute_url()
            if typeElement == 'Page':
                retour["urlElement"] = element.getText()
            if typeElement in ["Presentationssonorisees", "Webconference"]:
                retour["urlElement"] = element.getUrlEnr()
            if typeElement == "ExercicesWims":
                retour["urlElement"] = "cours_autoevaluation_view?qexo=%s" % (int(indexElement) + 1)
            if typeElement in ["Lecteurexportable", "Video"]:
                retour["urlElement"] = element.getLecteurExportable()
                retour["auteurVideoElement"] = element.getVideoauteurname()
            if typeElement == "Lienweb":
                urlWEB = element.getURLWEB()
                if not "://" in urlWEB:
                    urlWEB = "http://%s" % urlWEB
                retour["urlElement"] = urlWEB
            if typeElement == "CatalogueBU":
                ressource = element.getRessourceCatalogueBU()
                retour["image"] = ressource["image"]
                retour["publisher"] = ressource["publisher"]
                retour["creationdate"] = ressource["creationdate"]
                retour["urlcatalogue"] = ressource["urlcatalogue"]
    return retour


def getJalonMenu(context, portal_url, user, request):
    #context.plone_log("***** getJalonMenu")
    member_id = user.getId()
    is_etudiant = user.has_role(["Etudiant", "EtudiantJalon"])
    is_manager = user.has_role(["Manager"])
    is_secretaire = user.has_role(["Secretaire"])
    is_personnel = user.has_role(["Personnel"]) or is_secretaire or is_manager

    jalon_properties = getToolByName(context, "portal_jalon_properties")
    jalon_categories = dict(jalon_properties.getCategorie())
    liste_id_categorie = jalon_categories.keys()
    liste_id_categorie.sort()

    class_cours = ""
    sub_menu_mes_cours = []
    if is_etudiant:
        for id_categorie in liste_id_categorie:
            sub_menu_mes_cours.append({"id":      "cat%s" % id_categorie,
                                       "icone":   "fa fa-book",
                                       "title":   jalon_categories[id_categorie]['title'],
                                       "href":    "%s/cours/%s?categorie=%s" % (portal_url, member_id, id_categorie),
                                       "activer": True})
        if sub_menu_mes_cours:
            class_cours = "has-dropdown not-click"

    activer = jalon_properties.getPropertiesMonEspace()
    menu = {"left_menu": [{"id":        "mon_espace",
                           "class":     "has-dropdown not-click",
                           "icone":     "fa fa-home",
                           "title":     _(u"Mon espace"),
                           "href":      portal_url,
                           "sub_menu":  [{"id":      "fichiers",
                                          "icone":   "fa fa-files-o",
                                          "title":   _(u"Fichiers"),
                                          "href":    "%s/Members/%s/Fichiers" % (portal_url, member_id),
                                          "activer": activer["activer_fichiers"]},
                                         {"id":      "sonorisation",
                                          "icone":   "fa fa-microphone",
                                          "title":   _(u"Présentations sonorisées"),
                                          "href":    "%s/Members/%s/Sonorisation" % (portal_url, member_id),
                                          "activer": activer["activer_presentations_sonorisees"]},
                                         {"id":      "wims",
                                          "icone":   "fa fa-random",
                                          "title":   _(u"Exercices Wims"),
                                          "href":    "%s/Members/%s/Wims" % (portal_url, member_id),
                                          "activer": activer["activer_exercices_wims"]},
                                         {"id":      "liens",
                                          "icone":   "fa fa-external-link",
                                          "title":   _(u"Ressources externes"),
                                          "href":    "%s/Members/%s/Externes" % (portal_url, member_id),
                                          "activer": activer["activer_liens"]},
                                         {"id":      "glossaire",
                                          "icone":   "fa fa-font",
                                          "title":   _(u"Termes de glossaire"),
                                          "href":    "%s/Members/%s/Glossaire" % (portal_url, member_id),
                                          "activer": activer["activer_termes_glossaire"]},
                                         {"id":      "connect",
                                          "icone":   "fa fa-headphones",
                                          "title":   _(u"Webconférences"),
                                          "href":    "%s/Members/%s/Webconference" % (portal_url, member_id),
                                          "activer": activer["activer_webconferences"]},
                                         {"id":      "video",
                                          "icone":   "fa fa-youtube-play",
                                          "title":   _(u"Vidéos"),
                                          "href":    "%s/Members/%s/Video" % (portal_url, member_id),
                                          "activer": True}],
                           "is_visible": is_personnel},
                          {"id"      : "mes-cours",
                           "class"   : class_cours,
                           "icone"   : "fa fa-university",
                           "title"   :  _(u"Mes cours"),
                           "href"    :   "%s/cours/%s" % (portal_url, member_id),
                           "sub_menu": sub_menu_mes_cours,
                           "is_visible": True},
                          {"id"      : "mes_etudiants",
                           "class"   : "",
                           "icone"   : "fa fa-users",
                           "title"   : _(u"Mes étudiants"),
                           "href"    : "%s/etudiants" % portal_url,
                           "sub_menu": [],
                           "is_visible": is_personnel},
                          {"id"      : "gestion_pedagogique",
                           "class"   : "has-dropdown not-click",
                           "icone"   : "fa fa-database",
                           "title"   : _(u"Gestion pédagogique"),
                           "href"    : "%s/portal_jalon_bdd/@@jalon-bdd" % portal_url,
                           "sub_menu": [{"id"     : "gestion_bdd",
                                         "icone"  : "fa fa-list",
                                         "title"  : _(u"Offre de formations"),
                                         "href"   : "%s/portal_jalon_bdd/@@jalon-bdd?gestion=gestion_bdd" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_utilisateurs",
                                         "icone"  : "fa fa-users",
                                         "title"  : _(u"Utilsateurs"),
                                         "href"   : "%s/portal_jalon_bdd/@@jalon-bdd?gestion=gestion_utilisateurs" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_connexion_bdd",
                                         "icone"  : "fa fa-key",
                                         "title"  : _(u"Connexion"),
                                         "href"   : "%s/portal_jalon_bdd/@@jalon-bdd?gestion=gestion_connexion_bdd" % portal_url,
                                         "activer": True},
                                       ],
                          "is_visible": is_manager},
                          {"id"      : "gestion_pedagogique",
                           "class"   : "",
                           "icone"   : "fa fa-database",
                           "title"   : _(u"Gestion pédagogique"),
                           "href"    : "%s/portal_jalon_bdd/gestion_utilisateurs" % portal_url,
                           "sub_menu": [],
                           "is_visible": is_secretaire},
                          {"id"      : "configuration",
                           "class"   : "has-dropdown not-click",
                           "icone"   : "fa fa-cogs",
                           "title"   : _(u"Configuration"),
                           "href"    : "%s/portal_jalon_properties/@@jalon-configuration" % portal_url,
                           "sub_menu": [{"id"   : "gestion_connexion",
                                         "icone": "fa fa-key",
                                         "title": _(u"Connexion à Jalon"),
                                         "href" : "%s/portal_jalon_properties/gestion_connexion" % portal_url,
                                         "activer": True},
                                        {"id"   : "gestion_mon_espace",
                                         "icone": "fa fa-home",
                                         "title": _(u"Gestion \"Mon Espace\""),
                                         "href" : "%s/portal_jalon_properties/gestion_mon_espace" % portal_url,
                                         "activer": True},
                                        {"id"   : "gestion_mes_cours",
                                         "icone": "fa fa-university",
                                         "title": _(u"Gestion des cours"),
                                         "href" : "%s/portal_jalon_properties/gestion_mes_cours" % portal_url,
                                         "activer": True},
                                        {"id"   : "gestion_infos",
                                         "icone": "fa fa-external-link-square",
                                         "title": _(u"Liens d'informations"),
                                         "href" : "%s/portal_jalon_properties/gestion_infos" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_didacticiels",
                                         "icone"  : "fa fa-life-ring",
                                         "title"  : _(u"Didacticiels"),
                                         "href"   : "%s/portal_jalon_properties/gestion_didacticiels" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_messages",
                                         "icone"  : "fa fa-bullhorn",
                                         "title"  : _(u"Diffusion de messages"),
                                         "href"   : "%s/portal_jalon_properties/gestion_messages" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_email",
                                         "icone"  : "fa fa-envelope-o",
                                         "title"  : _(u"Courriels"),
                                         "href"   : "%s/portal_jalon_properties/gestion_email" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_donnees_utilisateurs",
                                         "icone"  : "fa fa-users",
                                         "title"  : _(u"Données utilisateurs"),
                                         "href"   : "%s/portal_jalon_properties/gestion_donnees_utilisateurs" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_ga",
                                         "icone"  : "fa fa-line-chart",
                                         "title"  : _(u"Google Analytics"),
                                         "href"   : "%s/portal_jalon_properties/gestion_ga" % portal_url,
                                         "activer": True},
                                        {"id"     : "gestion_maintenance",
                                         "icone"  : "fa fa-umbrella",
                                         "title"  : _(u"Maintenance"),
                                         "href"   : "%s/portal_jalon_properties/gestion_maintenance" % portal_url,
                                         "activer": True}
                                       ],
                          "is_visible": is_manager},
                         ],
            "right_menu" : [{"id"      : "deconnexion",
                             "class"   : "",
                             "icone"   : "fa fa-sign-out fa-fw",
                             "title"   : _(u"Deconnexion"),
                             "href"    : "%s/logout" % portal_url,
                             "sub_menu": []}
                           ]
           }
    request.SESSION.set("topBar", menu)
    return menu


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
