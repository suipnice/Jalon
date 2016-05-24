## Controller Python Script "edit_deposit_box_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Activite edit
##

form = context.REQUEST.form

context.setAttributActivite({"Description": form["description"]})

redirection = "%s?tab=%s" % (context.absolute_url(), form["tab"])
if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection