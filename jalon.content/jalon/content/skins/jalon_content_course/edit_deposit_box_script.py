## Controller Python Script "edit_deposit_box_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Activite edit
##

# context = context
form = context.REQUEST.form

if "title" in form:
    context.setProperties({"Title": form["title"]})
    # Met à jour le titre dans le plan du cours
    context.aq_parent.editCourseMapItem(context.getId(), form["title"], False)
else:
    context.setProperties({"Profile": form["profile"]})

# tab n'existe pas si on modifie l'activite depuis le plan du cours
if "tab" in form:
    redirection = "%s?tab=%s" % (context.absolute_url(), form["tab"])
else:
    redirection = context.aq_parent.absolute_url()

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection
