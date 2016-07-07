## Controller Python Script "edit_course_item_visibility_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

context_object = context
if context.meta_type in ["JalonBoiteDepot", "JalonCoursWims"]:
    context_object = getattr(context, form["item_id"])

item_date = DateTime() if form.has_key("date-affichage-now") else DateTime(form["datetime"])

is_update_from_title = False
if form["item_property_name"] == "affElement" and form.has_key("item_parent_title_id"):
    is_update_from_title = True
    context_object.editCourseParentTitleVisibility(form["item_parent_title_id"], item_date)

if form.has_key("is_item_title"):
    context_object.editCourseTitleVisibility(form["item_id"], item_date, form["item_property_name"])
else:
    context_object.editCourseItemVisibility(form["item_id"], item_date, form["item_property_name"], is_update_from_title)

redirection = context_object.absolute_url()
if context.meta_type in ["JalonBoiteDepot", "JalonCoursWims"] and not (form["item_id"].startswith("BoiteDepot-") or form["item_id"].startswith("AutoEvaluation-") or form["item_id"].startswith("Examen-")):
    redirection = "%s?tab=documents" % redirection

context.REQUEST.RESPONSE.redirect(redirection)
