## Controller Python Script "edit_course_property_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cours edit
##

form = context.REQUEST.form

context.setCoursePublicAccess(form["course_public_access"])

context.REQUEST.RESPONSE.redirect(context.absolute_url())
