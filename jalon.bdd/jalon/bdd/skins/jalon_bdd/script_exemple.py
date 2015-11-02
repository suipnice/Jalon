##Python Script "script_exemple"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Un script d'exemple
##

request = context.REQUEST
# appel de fonctions
#context.purgerActivitesWims()
#context.purgerDepots()

redirection = context.absolute_url()
if "redirection" in request.form:
    redirection = request.form["redirection"]

context.REQUEST.RESPONSE.redirect(redirection)