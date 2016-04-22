## Script (Python) "delete_all_course_announce_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.deleteAllAnnounce()

context.REQUEST.RESPONSE.redirect(context.absolute_url())
