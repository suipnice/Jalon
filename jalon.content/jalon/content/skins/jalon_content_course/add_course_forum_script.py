##Python Script "add_course_announce_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute un forum au cours
##

form = context.REQUEST.form

context.addCourseForum(form["title"], form["description"], form["user_id"])

HTTP_X_REQUESTED_WITH = True if context.REQUEST.HTTP_X_REQUESTED_WITH == 'XMLHttpRequest' else False
if not HTTP_X_REQUESTED_WITH:
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.absolute_url()
