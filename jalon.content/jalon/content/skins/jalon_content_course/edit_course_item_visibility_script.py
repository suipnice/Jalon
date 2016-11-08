## Controller Python Script "edit_course_item_visibility_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# context = context
context_object = context
form = context.REQUEST.form
redirection = context.absolute_url()

is_activity = False
object_type = form["item_id"].split("-", 1)[0]
if object_type in ["BoiteDepot", "AutoEvaluation", "Examen"]:
    is_activity = True
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

# Cas ou on affiche un document d'une activité
if context.meta_type in ["JalonBoiteDepot", "JalonCoursWims"] and not is_activity:
    redirection = "%s?tab=documents" % context_object.absolute_url()

context.REQUEST.RESPONSE.redirect(redirection)
