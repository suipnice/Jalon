## Controller Python Script "edit_peers_penality_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute un élément ou un sous-element au cours
##

form = context.REQUEST.form

context.setAttributActivite({"Penalite": form["penalite"], "AdjustementPoints": form["adjustementPoints"]})

redirection = "%s?tab=peers" % context.absolute_url()
if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection