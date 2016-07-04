## Script (Python) "course_delete_item_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

redirection = context.absolute_url()
if context.meta_type == "JalonCours":
    context.deleteCourseMapItem(form["item_id"], None)
    context.deleteCourseActuality(form["item_id"])
else:
    context.detachDocument(form["item_id"])
    redirection = "%s?tab=documents" % context.absolute_url()

context.REQUEST.RESPONSE.redirect(redirection)
