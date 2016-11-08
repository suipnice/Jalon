##Python Script "add_course_coreader_registration_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute un lecteur enseignant au cours
##

form = context.REQUEST.form

context.addCourseReader(form["username"].split(","))

HTTP_X_REQUESTED_WITH = False
if context.REQUEST.HTTP_X_REQUESTED_WITH == 'XMLHttpRequest':
    HTTP_X_REQUESTED_WITH = True

if not HTTP_X_REQUESTED_WITH:
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.absolute_url()
