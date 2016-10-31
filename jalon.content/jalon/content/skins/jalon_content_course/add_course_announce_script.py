##Python Script "add_course_announce_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute une annonce au cours
##

form = context.REQUEST.form

announce_publics = tuple(form["publicsElement"]) if form.has_key("publicsElement") else ()
mail_announce = tuple(form["mailAnnonce"]) if form.has_key("mailAnnonce") else None

context.createAnnounce(form["user_id"], form["title"], form["description"], announce_publics, mail_announce)

HTTP_X_REQUESTED_WITH = True if context.REQUEST.HTTP_X_REQUESTED_WITH == 'XMLHttpRequest' else False
if not HTTP_X_REQUESTED_WITH:
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.absolute_url()
