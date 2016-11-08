## Controller Python Script "create_external_bu_script"
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

for recordid in form["recordsid"]:
    object_id = "Externe-%s-%s" % (user_id, recordid)
    object_exist = getattr(external_resources_folder, object_id, None)
    if not object_exist:
        external_resources_folder.invokeFactory(type_name='JalonRessourceExterne', id=object_id)
        object_new = getattr(external_resources_folder, object_id)
        object_new.editFromBUCatalogBU(recordid)

context.REQUEST.RESPONSE.redirect(context.absolute_url())
