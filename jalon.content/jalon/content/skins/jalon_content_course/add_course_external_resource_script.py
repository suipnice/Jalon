## Controller Python Script "add_course_external_resource_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute une activité au cours
##

form = context.REQUEST.form

if form["title"] in ["", " ", None] or form["lien"] in ["", " ", None]:
    if "biblio" in form:
        redirection = "%s/create_and_add_course_external_resource_form?biblio=true" % context.absolute_url()
    else:
        redirection = "%s/create_and_add_course_external_resource_form" % context.absolute_url()
else:
    user_id = form["user_id"]
    portal = context.portal_url.getPortalObject()
    portal_workflow = portal.portal_workflow
    folder_object = context.getMySubSpaceFolder(user_id, "Externes", portal)

    external_id = "Externe-%s-%s" % (user_id, DateTime().strftime("%Y%m%d%H%M%S"))
    folder_object.invokeFactory(type_name="JalonRessourceExterne", id=external_id)
    external_object = getattr(folder_object, external_id)

    properties = {"Title":       form["title"],
                  "Description": form["description"]}

    if "iframe" in form["lien"] or "embed" in form["lien"]:
        external_type = "Lecteur exportable"
        properties["Lecteur"] = form["lien"]
    else:
        external_type = "Lien web"
        properties["Urlbiblio"] = form["lien"]
    properties["TypeRessourceExterne"] = external_type

    external_object.setProperties(properties)

    if "biblio" in form:
        context.addMySpaceItemBibliography(folder_object, external_id, external_type, user_id)
    else:
        display_item = DateTime() if "display_item" in form and form["display_item"] == "1" else ""
        display_in_plan = True if "display_in_plan" in form and form["display_in_plan"] == "1" else False
        map_items_position = form["map_position"] if form.has_key("map_position") else None

        context.addMySpaceItem(folder_object, external_id, external_type, user_id, display_item, map_items_position, display_in_plan, portal_workflow)

    if context.getId().startswith("Cours-"):
        redirection = context.absolute_url()
    else:
        redirection = "%s?tab=documents" % context.absolute_url()
    #context.REQUEST.RESPONSE.redirect(context.absolute_url())
    #return "%s/display_course_map_page" % context.absolute_url()

context.REQUEST.RESPONSE.redirect(redirection)