## Controller Python Script "add_course_glossary_term_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute une activité au cours
##

form = context.REQUEST.form

if form["title"] in ["", " ", None] or form["description"] in ["", " ", None]:
    redirection = "%s/create_and_add_course_glossary_term_form" % context.absolute_url()
else:
    redirection = context.absolute_url()
    user_id = form["user_id"]
    portal = context.portal_url.getPortalObject()
    portal_workflow = portal.portal_workflow
    folder_object = context.getMySubSpaceFolder(user_id, "Glossaire", portal)

    external_id = "Glossaire-%s-%s" % (user_id, DateTime().strftime("%Y%m%d%H%M%S"))
    folder_object.invokeFactory(type_name="JalonTermeGlossaire", id=external_id)
    external_object = getattr(folder_object, external_id)

    external_object.setProperties({"Title":       form["title"],
                                   "Description": form["description"]})

    context.addMySpaceItemGlossary(folder_object, external_id, "TermeGlossaire", user_id)

    #context.REQUEST.RESPONSE.redirect(context.absolute_url())

context.REQUEST.RESPONSE.redirect(redirection)
