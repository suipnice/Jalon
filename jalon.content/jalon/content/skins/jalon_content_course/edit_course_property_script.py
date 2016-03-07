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

context.setAttributCours({form["course_property"]: form[form["course_property"]]})

return context.absolute_url()
