## Script (Python) "delete_course_announce_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.deleteAnnounce(context.REQUEST.form["announce_id"])

context.REQUEST.RESPONSE.redirect(context.absolute_url())
