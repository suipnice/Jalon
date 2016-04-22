## Controller Python Script "edit_course_announce_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

announce_publics = tuple(form["publicsElement"]) if form.has_key("publicsElement") else ()
mail_announce = form["mailAnnonce"] if form.has_key("mailAnnonce") else False

context.setProperties({"Title":       form["title"],
                       "Description": form["description"],
                       "Publics":     announce_publics})

if mail_announce:
    context.envoyerAnnonce()

context.REQUEST.RESPONSE.redirect(context.aq_parent.aq_parent.absolute_url())
