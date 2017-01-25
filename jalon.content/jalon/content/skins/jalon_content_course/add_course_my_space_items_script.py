## Controller Python Script "add_course_my_space_items_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute un élément ou un sous-element au cours
##

# context = context
request = context.REQUEST
form = request.form

user_id = form["user_id"]
portal = context.portal_url.getPortalObject()
portal_workflow = portal.portal_workflow
folder_object = context.getMySubSpaceFolder(user_id, form["folder_id"], portal)

display_item = DateTime() if "display_item" in form and form["display_item"] == "1" else ""
display_in_plan = True if "display_in_plan" in form and form["display_in_plan"] == "1" else False
map_items_position = form["map_position"] if form.has_key("map_position") else None

if form.has_key("glossary_or_bibliography"):
    if form["glossary_or_bibliography"] == "glossary":
        for item in request.form["paths"]:
            item_id, item_type = item.split("/")
            context.addMySpaceItemGlossary(folder_object, item_id, item_type, user_id)
    if form["glossary_or_bibliography"] == "bibliography":
        for item in request.form["paths"]:
            item_id, item_type = item.split("/")
            context.addMySpaceItemBibliography(folder_object, item_id, item_type, user_id)
    request.RESPONSE.redirect(context.absolute_url())
else:
    for item in request.form["paths"]:
        item_id, item_type = item.split("/")
        context.addMySpaceItem(folder_object, item_id, item_type, user_id, display_item, map_items_position, display_in_plan, portal_workflow)

if context.getId().startswith("Cours-"):
    return "%s/display_course_map_page" % context.absolute_url()
else:
    if form.has_key("tab"):
        request.RESPONSE.redirect("%s?tab=%s" % (context.absolute_url(), form["tab"]))
    else:
        request.RESPONSE.redirect("%s?tab=documents" % context.absolute_url())
