## Controller Python Script "check_course_password_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Inscrire un étudiant à un cours après vérification du mot de passe
##

REQUEST = context.REQUEST

context.addPasswordStudent(REQUEST["member_id"])

context.REQUEST.RESPONSE.redirect(context.absolute_url())
