## Controller Python Script "create_course_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

param = {}
REQUEST = context.REQUEST

course_user_folder = context.getCourseUserFolder(REQUEST.form["user_id"])
course_id = course_user_folder.invokeFactory(type_name='JalonCours', id="Cours-%s-%s" % (REQUEST["user_id"], DateTime().strftime("%Y%m%d%H%M%S")))

course_object = getattr(course_user_folder, course_id)
param = {
    "Title": context.supprimerMarquageHTML(REQUEST["title"]),
    "Description": REQUEST["description"]
}

course_object.setCourseProperties(param)
course_object.invokeFactory(type_name='Folder', id="annonce")
course_object.invokeFactory(type_name='Ploneboard', id="forum")

forum_folder_object = getattr(course_object, "forum")
forum_folder_object.setTitle("Liste des forums du cours")

course_object.addCourseForum("Discussion générale", "Discutez ici librement du cours.", REQUEST["user_id"])

course_object.setCourseProperties({"DateDerniereModif": DateTime()})

context.REQUEST.RESPONSE.redirect("%s?tab=2" % context.absolute_url())
