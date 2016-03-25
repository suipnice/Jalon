## Script (Python) "course_delete_item_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

context.deleteCourseMapItem(form["item_id"], None)
context.deleteCourseActuality(form["item_id"])

context.REQUEST.RESPONSE.redirect(context.absolute_url())
