## Controller Python Script "activate_webconference_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# context = context
request = context.REQUEST
form = request.form

context.addItemInCourseMap(form["meeting_id"], "fin_racine")
context.addItemProperty(form["meeting_id"], "SalleVirtuelle", form["meeting_title"], form["meeting_owner"], "", None)

request.RESPONSE.redirect(context.absolute_url())
#return "%s/display_course_map_page" % context.absolute_url()
