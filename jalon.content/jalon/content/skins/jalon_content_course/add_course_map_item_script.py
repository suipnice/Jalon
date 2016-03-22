## Controller Python Script "add_course_map_item_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute un élément au plan intéractif
##
from DateTime import DateTime

now = DateTime()
form = context.REQUEST.form

item_id = "%s-%s-%s" % (form["item_type"], form["user_id"], ''.join([now.strftime('%Y%m%d'), now.strftime('%H%M%S')]))

context.addItemInCourseMap(item_id, form["map_position"])
context.addItemProperty(item_id, form["item_type"], form["title"], form["user_id"], "", None)

context.setProperties({"DateDerniereModif": DateTime()})

return "%s/display_course_map_page" % context.absolute_url()
