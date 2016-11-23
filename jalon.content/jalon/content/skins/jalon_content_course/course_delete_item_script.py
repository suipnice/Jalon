## Script (Python) "course_delete_item_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Supprime ou détache un element ou sous-element du cours
##

# context = context

form = context.REQUEST.form

redirection = context.absolute_url()
if context.meta_type == "JalonCours":
    context.deleteCourseMapItem(form["item_id"], None)
    context.deleteCourseActuality(form["item_id"])
else:
    if "tab" not in form:
        form["tab"] = "documents"

    if form["tab"] == "exercices":
        context.detachExercice(form["item_id"], form["item_order"])
    else:
        context.detachDocument(form["item_id"])

    redirection = "%s?tab=%s" % (context.absolute_url(), form["tab"])

context.REQUEST.RESPONSE.redirect(redirection)
