##Python Script "forum_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute une annonce au cours
##

form = context.REQUEST.form

context.ajouterForum(form["user_id"], form["title"], form["description"])

HTTP_X_REQUESTED_WITH = True if context.REQUEST.HTTP_X_REQUESTED_WITH == 'XMLHttpRequest' else False
if not HTTP_X_REQUESTED_WITH:
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.absolute_url()
