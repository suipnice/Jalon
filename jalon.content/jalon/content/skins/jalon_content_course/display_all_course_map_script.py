## Controller Python Script "display_all_course_map_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
context.editAllCourseMapVisibility(request["display_or_hide"])
request.RESPONSE.redirect(context.absolute_url())
