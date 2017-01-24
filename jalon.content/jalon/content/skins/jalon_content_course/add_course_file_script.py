## Controller Python Script "add_course_file_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute une activité au cours
##

form = context.REQUEST.form

if not "file_file" in form or form["file_file"].filename in ["", " ", None]:
    redirection = "%s/create_and_add_course_file_form" % context.absolute_url()
else:
    user_id = form["user_id"]
    portal = context.portal_url.getPortalObject()
    portal_workflow = portal.portal_workflow
    folder_object = context.getMySubSpaceFolder(user_id, "Fichiers", portal)

    file_name = context.get_id_from_filename(form["file_file"].filename, context)
    file_extension = file_name.split(".")[-1]
    file_type = "Image" if file_extension in ["png", "jpg", "jpeg", "bmp", "svg", "gif"] else "File"

    file_object = getattr(folder_object, file_name, None)
    if not file_object:
        folder_object.invokeFactory(type_name=file_type, id=file_name)
        file_object = getattr(folder_object, file_name)

    title_file = form["title"] if form["title"] else file_name.rsplit('.', 1)[0]
    file_object.setTitle(title_file)
    file_object.setDescription(form["description"])

    if file_type == "Image":
        file_object.setImage(form["file_file"])
    else:
        file_object.setFile(form["file_file"])

    display_item = DateTime() if "display_item" in form and form["display_item"] == "1" else ""
    display_in_plan = True if "display_in_plan" in form and form["display_in_plan"] == "1" else False
    map_items_position = form["map_position"] if form.has_key("map_position") else None

    context.addMySpaceItem(folder_object, file_name, file_type, user_id, display_item, map_items_position, display_in_plan, portal_workflow)

    if context.getId().startswith("Cours-"):
        redirection = context.absolute_url()
    else:
        redirection = "%s?tab=documents" % context.absolute_url()
context.REQUEST.RESPONSE.redirect(redirection)
#return "%s/display_course_map_page" % context.absolute_url()
