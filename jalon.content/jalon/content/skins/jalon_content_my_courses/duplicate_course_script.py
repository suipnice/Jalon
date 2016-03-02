## Controller Python Script "dupliquer_cours"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Dupliquer un cours
##

request = context.REQUEST
course_id = request.form["course_id"]
course_user_folder = context.getCourseUserFolder(request.form["user_id"])

course_user_folder.dupliquerCours(course_id, course_user_folder)

request.RESPONSE.redirect("%s?tab=%s" % (context.absolute_url(), request.form["tab"]))
