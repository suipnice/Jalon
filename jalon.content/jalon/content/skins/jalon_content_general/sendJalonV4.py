##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid=None, entry=None
##title=
##

portal = context.portal_url.getPortalObject()
serveur = portal.getProperty("title")
portal.etudiants.envoyerMailErreur({"objet"   : "%s : Erreur [%s]" % (serveur, userid)
                                   ,"entry"   : entry})

return "envoie"