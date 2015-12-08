## Controller Python Script "cours_modifier_exercice"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cours edit
##

form = context.REQUEST.form
redirection = "%s/%s?menu=%s" % (context.absolute_url(), form["page"], form["menu"])

context.modifierExoFeuille(form)
return context.REQUEST.RESPONSE.redirect(redirection)
