# -*- coding: utf-8 -*-
## Controller Python Script "delete_tag"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajout et/ou modification d'un exercice WIMS
##
#context = context

# Suppression de l'étiquette
tag_id = context.REQUEST.form["tag_id"]
context.deleteTagFolder(tag_id)

context.REQUEST.RESPONSE.redirect(context.absolute_url())
