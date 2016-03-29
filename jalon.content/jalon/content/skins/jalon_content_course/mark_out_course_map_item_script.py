## Controller Python Script "mark_out_course_map_item_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

context.setCourseProperties({"AvancementPlan": [form["mark_out_item_id"], form["mark_out_item_text"]]})

context.REQUEST.RESPONSE.redirect(context.absolute_url())
