## Controller Python Script "erreurWIMS"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=erreur
##title=Gestion d'erreurs WIMS
##

from Products.CMFPlone import PloneMessageFactory as _

#en parametre, la fonction attend une liste (d'exercices). Si elle recoit une chaine de caracteres, c'est alors un message d'erreur.
try:
    if erreur.has_key("erreur"):
        #message = "Une tentative de connexion au serveur WIMS n'a pas abouti.\n Utilisateur : %s \n Code d'erreur : %s" % user.getId(),erreur
        #message = _(u"Une tentative de connexion au serveur WIMS n'a pas aboutit.")
        #context.envoyerMail({"message":message ,"de":"", "objet":"erreur WIMS", "a":"administrateur_jalon"})

        # On effectue un redirect pour éviter d'afficher le bouton de creation d'exercice et les etiquettes, qui apparaissent en dehors de macro_wims
        return context.REQUEST.response.redirect("%s?message=%s" % (context.portal_url.getPortalObject().absolute_url(), erreur["erreur"]))
except:
    pass
