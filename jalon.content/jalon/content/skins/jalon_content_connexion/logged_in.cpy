## Controller Python Script "logged_in"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Initial post-login actions
##

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST
# context = context
# state = state

membership_tool = getToolByName(context, 'portal_membership')
if membership_tool.isAnonymousUser():

    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    email_login = getToolByName(context, 'portal_properties').site_properties.getProperty('use_email_as_login')
    if email_login:
        context.plone_utils.addPortalMessage(_(u'Login failed. Both email address and password are case sensitive, check that caps lock is not enabled.'), 'error')
    else:
        context.plone_utils.addPortalMessage(_(u'Login failed. Both login name and password are case sensitive, check that caps lock is not enabled.'), 'error')
    return state.set(status='failure')

member = membership_tool.getAuthenticatedMember()
login_time = member.getProperty('login_time', '2000/01/01')
initial_login = int(str(login_time) == '2000/01/01')
state.set(initial_login=initial_login)

must_change_password = member.getProperty('must_change_password', 0)
state.set(must_change_password=must_change_password)

location = member.getProperty('location', '')
if not location:
    if not REQUEST.form.has_key("ticket"):
        member.setProperties({"location": "jalon"})
    else:
        if "univ-tln" in REQUEST.form["ticket"]:
            member.setProperties({"location": "ustv"})
        else:
            member.setProperties({"location": "unice"})

if initial_login:
    state.set(status='initial_login')
elif must_change_password:
    state.set(status='change_password')

memberid = member.getId()
if (not hasattr(context.Members, memberid)) and (not member.has_role(["Etudiant", "EtudiantJalon"])):
    context.Members.invokeFactory(type_name='JalonFolder', id=memberid)
    home = getattr(context.Members, memberid)
    home.addSubJalonFolder(memberid)

if not hasattr(context.cours, memberid):
    context.cours.invokeFactory(type_name='JalonFolder', id=memberid)
    cours = getattr(context.cours, memberid)
    cours.setTitle("Mes cours")
    cours.setPortlets()
    # context.portal_catalog.refreshCatalog(clear=True)

# if REQUEST.form.has_key("action"):
#    if REQUEST.form["action"] == "mooc":
#        cours = getattr(getattr(context.cours, REQUEST.form["auteur"]), REQUEST.form["idcours"])
#        cours.inscrireMOOC(memberid)

membership_tool.loginUser(REQUEST)

portal_jalon_bdd = getToolByName(context, 'portal_jalon_bdd')
portal_jalon_properties = getToolByName(context, 'portal_jalon_properties')
infos_user = portal_jalon_bdd.getIndividuLITE(memberid)
if not infos_user:
    if portal_jalon_properties.getPropertiesDonneesUtilisateurs("activer_ldap"):
        acl_users = getattr(context.acl_users, "ldap-plugin").acl_users
        for user in acl_users.findUser(search_param="supannAliasLogin", search_term=memberid, exact_match=True):
            if "supannAliasLogin" in user:
                LIB_PR1_IND, LIB_NOM_PAT_IND = user["displayName"].decode("iso-8859-1").split(" ", 1)
                portal_jalon_bdd.creerUtilisateur({"SESAME_ETU"      : user["supannAliasLogin"],
                                                   "DATE_NAI_IND"    : "Non renseignée",
                                                   "LIB_NOM_PAT_IND" : LIB_NOM_PAT_IND,
                                                   "LIB_NOM_USU_IND" : "Non renseignée",
                                                   "LIB_PR1_IND"     : LIB_PR1_IND,
                                                   "TYPE_IND"        : "Personnel",
                                                   "COD_ETU"         : "",
                                                   "EMAIL_ETU"       : user["mail"].decode("iso-8859-1"),
                                                   "ADR1_IND"        : "Non renseignée",
                                                   "ADR2_IND"        : "Non renseignée",
                                                   "COD_POST_IND"    : "Non renseignée",
                                                   "VIL_IND"         : "Non renseignée",
                                                   "UNIV_IND"        : "Non renseignée",
                                                   "PROMO_IND"       : ""})
        infos_user = portal_jalon_bdd.getIndividuLITE(memberid)

if member.has_role("EtudiantJalon"):
    LIB_PR1_IND, LIB_NOM_PAT_IND = member.getProperty("fullname", "Non renseigné").rsplit(" ", 1)
    portal_jalon_bdd.creerUtilisateur({"SESAME_ETU":      memberid,
                                       "DATE_NAI_IND":    "",
                                       "LIB_NOM_PAT_IND": LIB_NOM_PAT_IND,
                                       "LIB_NOM_USU_IND": "Non renseignée",
                                       "LIB_PR1_IND":     LIB_PR1_IND,
                                       "TYPE_IND":        "Etudiant",
                                       "COD_ETU":         "",
                                       "EMAIL_ETU":       member.getId(),
                                       "ADR1_IND":        "Non renseignée",
                                       "ADR2_IND":        "Non renseignée",
                                       "COD_POST_IND":    "Non renseignée",
                                       "VIL_IND":         "Non renseignée",
                                       "UNIV_IND":        "Invité",
                                       "PROMO_IND":       ""})

try:
    portal_jalon_bdd.addConnexionUtilisateur(memberid)
except:
    # infos_user = portal_jalon_bdd.getIndividuLITE(memberid)
    portal_jalon_bdd.creerUtilisateurMySQL({"SESAME_ETU":      memberid,
                                            "DATE_NAI_IND":    "",
                                            "LIB_NOM_PAT_IND": infos_user["LIB_NOM_PAT_IND"],
                                            "LIB_NOM_USU_IND": "Non renseignée",
                                            "LIB_PR1_IND":     infos_user["LIB_PR1_IND"],
                                            "TYPE_IND":        infos_user["TYPE_IND"],
                                            "COD_ETU":         infos_user["COD_ETU"],
                                            "EMAIL_ETU":       infos_user["EMAIL_ETU"]})
    portal_jalon_bdd.addConnexionUtilisateur(memberid)

if portal_jalon_bdd.isUtilisateurNotActif(memberid):
    state.set(status="failure")

return state
