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
idobj = course_user_folder.invokeFactory(type_name='JalonCours', id="Cours-%s-%s" % (REQUEST["user_id"], DateTime().strftime("%Y%m%d%H%M%S")))

obj = getattr(course_user_folder, idobj)
param = {"Title": REQUEST["title"], "Description": REQUEST["description"]}

obj.setProperties(param)
obj.invokeFactory(type_name='Folder', id="annonce")
obj.invokeFactory(type_name='Ploneboard', id="forum")
forum = getattr(obj, "forum")
forum.setTitle("Liste des forums du cours")
obj.creerSousObjet("Forum", "Discussion générale", "Discutez ici librement du cours.", REQUEST["user_id"], "", "")

obj.setProperties({"DateDerniereModif": DateTime()})

context.REQUEST.RESPONSE.redirect("%s?tab=2" % context.absolute_url())
