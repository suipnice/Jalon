##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
form = request.form

etu_libre = form["etu_libre"] if "etu_libre" in form else []
context.deletePasswordStudent(etu_libre)
request.RESPONSE.redirect(context.absolute_url())
