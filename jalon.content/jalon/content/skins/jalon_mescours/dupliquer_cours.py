## Controller Python Script "dupliquer_cours"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=idcours, creator, manager, orig_template
##title=Dupliquer un cours
##
""" Duplique le cours "idcours", et renvoit vers la page orig_template."""

context.dupliquerCours(idcours, creator, manager)
return context.REQUEST.RESPONSE.redirect(orig_template)
