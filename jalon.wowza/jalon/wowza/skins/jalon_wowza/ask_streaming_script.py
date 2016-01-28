##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=ask_streaming_script
##

form = context.REQUEST.form
context.askStreaming(form["pod"], form["member_id"])
context.REQUEST.RESPONSE.redirect(context.absolute_url())
