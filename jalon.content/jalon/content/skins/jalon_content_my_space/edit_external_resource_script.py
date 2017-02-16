## Controller Python Script "edit_external_resource_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
properties_dict = {}
properties_editable_dict = context.getAttributsTypeMod()

for property_form_id in form.keys():
    if property_form_id in properties_editable_dict:
        properties_dict[properties_editable_dict[property_form_id]] = form[property_form_id]

context.setProperties(properties_dict)

context.REQUEST.RESPONSE.redirect("%s/mes_ressources/mes_ressources_externes" % context.portal_url.getPortalObject().absolute_url())
