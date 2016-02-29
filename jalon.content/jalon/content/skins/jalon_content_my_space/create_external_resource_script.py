## Controller Python Script "create_external_resource_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
form = REQUEST.form

user_id = form["member_id"]
external_resources_folder = context.getMySubSpaceFolder(user_id, "Externes")
object_id = external_resources_folder.invokeFactory(type_name='JalonRessourceExterne', id="Externe-%s-%s" % (user_id, DateTime().strftime("%Y%m%d%H%M%S")))

object_new = getattr(external_resources_folder, object_id)

properties_dict = {"Title":                form["title"],
                   "TypeRessourceExterne": "",
                   "Description":          form["description"]}

if "iframe" in form["urlbiblio"] or "embed" in form["urlbiblio"]:
    properties_dict["TypeRessourceExterne"] = "Lecteur exportable"
    properties_dict["Lecteur"] = form["urlbiblio"]
else:
    properties_dict["TypeRessourceExterne"] = "Lien web"
    properties_dict["Urlbiblio"] = form["urlbiblio"]

object_new.setProperties(properties_dict)

context.REQUEST.RESPONSE.redirect(context.absolute_url())
