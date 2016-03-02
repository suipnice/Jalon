## Controller Python Script "create_glossary_term_script"
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
glossary_terms_folder = context.getMySubSpaceFolder(user_id, "Glossaire")
object_id = glossary_terms_folder.invokeFactory(type_name='JalonTermeGlossaire', id="Glossaire-%s-%s" % (user_id, DateTime().strftime("%Y%m%d%H%M%S")))

object_new = getattr(glossary_terms_folder, object_id)

properties_dict = {"Title":                form["title"],
                   "Description":          form["description"]}

object_new.setProperties(properties_dict)

context.REQUEST.RESPONSE.redirect(context.absolute_url())
