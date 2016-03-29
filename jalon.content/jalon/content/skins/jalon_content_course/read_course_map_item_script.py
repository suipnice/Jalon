## Controller Python Script "read_course_map_item_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Activite edit
##

item_id = context.REQUEST["item_id"]

context.readCourseMapItem(item_id)

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect("%s?mode_etudiant=true" % context.absolute_url())
