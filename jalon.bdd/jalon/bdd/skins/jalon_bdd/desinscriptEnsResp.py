##Python Script "desinscriptEnsResp"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=desinscriptEnsResp
##

form = context.REQUEST.form
redirection = context.absolute_url()
if "redirection" in form.keys():
    redirection = form["redirection"]

context.desinscrireEnsResp(form)

context.REQUEST.RESPONSE.redirect(redirection)
