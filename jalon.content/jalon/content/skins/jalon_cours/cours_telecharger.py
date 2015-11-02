## Controller Python Script "cours_telecharger"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Telecharge les fichiers du cours
##

request = context.REQUEST
zipfile = context.telecharger(request["HTTP_USER_AGENT"], request.form["elements"])
#si un seul est coché, l'envoyer directement sauf s'il s'agit d'une image
if len(request.form["elements"]) == 1 and zipfile["situation"] == 1:
    request.RESPONSE.redirect(zipfile["data"])
#elif zipfile["situation"] == 2:
#	return zipfile["data"]
else:
    request.RESPONSE.setHeader('content-type', 'application/zip')
    request.RESPONSE.setHeader('content-length', zipfile["length"])
    request.RESPONSE.setHeader('Content-Disposition',' attachment; filename=%s.zip' % context.supprimerCaractereSpeciaux(context.Title()))
    return zipfile["data"]

