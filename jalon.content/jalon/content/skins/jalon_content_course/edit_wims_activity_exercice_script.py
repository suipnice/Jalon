## Controller Python Script "edit_wims_activity_exercice_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Modifie les propriétés d'un exercice dans une activité WIMS
##

context = context
form = context.REQUEST.form

context.modifierExoFeuille(form)

redirection = "%s?tab=%s" % (context.absolute_url(), "exercices")
if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection
