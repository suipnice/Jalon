## Script (Python) "getConnexionRequire"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=CAS Logout
##

from Products.CMFCore.utils import getToolByName

portal = context.portal_url.getPortalObject()
portal_jalon_properties = getToolByName(context, 'portal_jalon_properties')

return {"site": portal.Title(),
        "maintenance":              portal_jalon_properties.getPropertiesMaintenance(),
        "activer_message_general":  portal_jalon_properties.getJalonProperty("activer_message_general"),
        "message_general":          portal_jalon_properties.getJalonProperty("message_general"),
        "activer_lien_sesame":      portal_jalon_properties.getJalonProperty("activer_lien_sesame"),
        "lien_sesame":              portal_jalon_properties.getJalonProperty("lien_sesame"),
        "lien_bug":                 portal_jalon_properties.getJalonProperty("lien_assitance"),
        "etablissement":            portal_jalon_properties.getJalonProperty("etablissement"),
        "activer_cas":              portal_jalon_properties.getJalonProperty("activer_cas"),
        "activer_creationcompte":   portal_jalon_properties.getJalonProperty("activer_creationcompte"),
       }