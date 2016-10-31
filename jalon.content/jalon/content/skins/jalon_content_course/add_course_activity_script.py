## Controller Python Script "add_course_activity_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute une activité au cours
##

form = context.REQUEST.form
context.addCourseActivity(form["user_id"], form["activity_type"], form["title"], form["description"], form["map_position"])

return "%s/display_course_map_page" % context.absolute_url()