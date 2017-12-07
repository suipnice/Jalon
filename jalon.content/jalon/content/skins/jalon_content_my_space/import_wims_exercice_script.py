# -*- coding: utf-8 -*-
## Controller Python Script "import_wims_exercice_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=import d'exercices WIMS a partir d'un fichier
##

# Le contexte est un jalonfolder
# context = context
REQUEST = context.REQUEST
form = context.REQUEST.form

context.importExercicesWIMS(form["type"], form["format"], form["member_auth"], form["file"], form["model_filter"])

REQUEST.RESPONSE.redirect(context.absolute_url())
