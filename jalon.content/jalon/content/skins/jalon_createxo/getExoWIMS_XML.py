##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=format
##title=
##
#import OEF_to_OLX

u"""  Script (Python) "getExoWIMS_XML".

Fournit un fichier XML de l'exo WIMS courant, selon le format demandé (QTI ou EDX)

"""

request = context.REQUEST

#request n'est pas un veritable dico, donc pas de "in"
if request.has_key("format"):
    formatXML = request["format"]
else:
    #par défaut, on exporte en QTI
    formatXML = "OLX"
request.RESPONSE.setHeader('content-type', "application/xml")
request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=exo_WIMS_%s.xml' % formatXML)

# Ici, context doit etre un jalonexercicewims
return context.getExoXML(formatXML)
