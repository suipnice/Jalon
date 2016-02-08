# -*- coding: utf-8 -*-
# Controller Python Script "add_tag_object_script"
# bind container=container
# bind context=context
# bind namespace=
# bind script=script
# bind subpath=traverse_subpath
# parameters=
# title=
##

try:
    tags_list = tuple(context.REQUEST.form["listeTag"])
except:
    tags_list = ()
context.setSubject(tags_list)
context.reindexObject()

redirection = context.absolute_url()
# context.REQUEST.RESPONSE.redirect(redirection)

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return context.restrictedTraverse("mon_espace/mes_fichiers")()
