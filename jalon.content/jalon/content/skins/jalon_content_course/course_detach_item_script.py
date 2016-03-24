## Script (Python) "course_detach_item_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

context.detachCourseMapItem(form["item_id"], None)
context.deleteActuality(form["item_id"])

context.REQUEST.RESPONSE.redirect(context.absolute_url())
