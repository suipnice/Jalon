##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
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
    formatXML = "QTI"

if request.has_key("version"):
    version = request["version"]
else:
    #par défaut, on exporte dans la derniere version
    version = "latest"

if formatXML == "QTI":
    filename = "exo_WIMS_%s.zip" % formatXML
    zipfile = context.getExoZIP("questionDB.xml", context.getExoXML(formatXML, version))
    request.RESPONSE.setHeader('content-type', "application/zip")
    request.RESPONSE.setHeader('content-length', zipfile["length"])
    request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
    # Ici, context doit etre un jalonexercicewims
    return zipfile["data"]

else:
    filename = "exo_WIMS_%s.xml" % formatXML
    request.RESPONSE.setHeader('content-type', "application/xml")
    request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s' % filename)
    # Ici, context doit etre un jalonexercicewims
    return context.getExoXML(formatXML, version)
