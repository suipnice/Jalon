## Controller Python Script "edit_deposit_box_date_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute un élément ou un sous-element au cours
##

form = context.REQUEST.form

context.setAttributActivite({"DateDepot": DateTime(form["datetime-depot"]), "DateRetard": DateTime(form["datetime-retard"])})

redirection = "%s?tab=%s" % (context.absolute_url(), form["tab"])
if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection