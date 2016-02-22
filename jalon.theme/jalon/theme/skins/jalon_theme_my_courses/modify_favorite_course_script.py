## Controller Python Script "modify_favorite_course_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

tab = context.modifyFavoriteCourse(context.REQUEST.form["user_id"], context.REQUEST.form["course_id"])

context.REQUEST.RESPONSE.redirect("%s/mes_cours?tab=1" % context.absolute_url())
