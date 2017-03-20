## Controller Python Script "edit_course_map_item_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Edite un élément du plan interactif
##
from DateTime import DateTime

now = DateTime()
# context = context
form = context.REQUEST.form

if form["item_type"] == "Titre":
    # Supp. marquage HTML éventuellement saisi.
    form["title"] = context.supprimerMarquageHTML(form["title"])

if not form.has_key("item_id"):
    item_id = "%s-%s-%s" % (form["item_type"], form["user_id"], ''.join([now.strftime('%Y%m%d'), now.strftime('%H%M%S')]))
    context.addItemInCourseMap(item_id, form["map_position"])
    context.addItemProperty(item_id, form["item_type"], form["title"], form["user_id"], "", None)
else:
    item_display_in_course_map = True if form.has_key("display_in_plan") else False
    context.editCourseMapItem(form["item_id"], form["title"], item_display_in_course_map)
    if form["typeElement"] in ["BoiteDepot", "AutoEvaluation", "Examen"]:
        activite = getattr(context, form["item_id"])
        activite.setProperties({"Title": form["title"]})
context.setCourseProperties({"DateDerniereModif": DateTime()})

return "%s/display_course_map_page" % context.absolute_url()
