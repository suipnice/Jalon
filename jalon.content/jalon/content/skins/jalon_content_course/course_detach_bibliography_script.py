## Script (Python) "course_detach_bibliography_script"
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

context.detachBibliographyItem(form["item_id"])

context.REQUEST.RESPONSE.redirect(context.absolute_url())
