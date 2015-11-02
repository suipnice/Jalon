## Controller Python Script "forum_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Forum edit
##

form = context.REQUEST.form

if "parent" in form:
    redirection = context.aq_parent.absolute_url()
else:
    redirection = context.absolute_url()


context.setTitle(form["title"])

if "description" in form:
    context.setDescription(form["description"])

if "text" in form:
    context.setText(form["text"])

context.reindexObject()


if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection
