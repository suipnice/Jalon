## Controller Python Script "ajoutercours_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

#context.plone_log("---------- ajoutercours_script (Debut) ----------")

param = {}
REQUEST = context.REQUEST

idobj = context.invokeFactory(type_name='JalonCours', id="Cours-%s-%s" % (REQUEST["authMember"], DateTime().strftime("%Y%m%d%H%M%S")))
#context.plone_log("---------- ajoutercours_script (invoke JalonCours) ----------")

obj = getattr(context, idobj)
param = {"Title": REQUEST["title"], "Description": REQUEST["description"]}

obj.setProperties(param)
#context.plone_log("---------- ajoutercours_script (setProperties) ----------")
obj.invokeFactory(type_name='Folder', id="annonce")
obj.invokeFactory(type_name='Ploneboard', id="forum")
forum = getattr(obj, "forum")
forum.setTitle("Liste des forums du cours")
obj.creerSousObjet("Forum", "Discussion générale", "Discutez ici librement du cours.", REQUEST["authMember"], "", "")

obj.setProperties({"DateDerniereModif" : DateTime()})
#context.plone_log("---------- ajoutercours_script (Fin) ----------")

context.REQUEST.RESPONSE.redirect("%s" % context.absolute_url())