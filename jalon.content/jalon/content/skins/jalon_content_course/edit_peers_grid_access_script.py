## Controller Python Script "edit_peers_grid_access_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Activite edit
##

#context = context
form = context.REQUEST.form

context.setProperties({"AccesGrille": form["grid_access"]})

redirection = "%s?tab=%s" % (context.absolute_url(), "peers")

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection
