## Controller Python Script "add_course_coauthor_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute un coauteur au cours
##

context.addCoAuteurs(context.REQUEST.form)
context.REQUEST.RESPONSE.redirect(context.absolute_url())
