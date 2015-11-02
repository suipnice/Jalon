## Controller Python Script "cours_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cours edit
##

form = context.REQUEST.form

redirection = context.absolute_url()
if "page" in form and form["key"] not in ["title", "description", "acces", "libre"]:
    redirection = "%s/%s" % (redirection, form["page"])

HTTP_X_REQUESTED_WITH = False
#if form["key"] in ["catiTunesU"]:
#    redirection = "%s?onglet=gestion-acces-etu" % redirection
#elif not form["key"] in ["title", "description", "acces", "libre"]:
#    redirection = "%s?onglet=gestion-preferences" % redirection

context.setAttributCours({form["key"]: form[form["key"]]})

if not form["key"] in ["description", "acces", "libre", "catiTunesU", "categorie", "activer_email_forum", "activer_dll_fichier"] and context.REQUEST.HTTP_X_REQUESTED_WITH == 'XMLHttpRequest':
    HTTP_X_REQUESTED_WITH = True

if not HTTP_X_REQUESTED_WITH:
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection
