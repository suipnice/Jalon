## Controller Python Script "deposit_file_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

context.addDepositFile(form["title"], form["description"], form["file_file"], form["user_id"])

context.REQUEST.RESPONSE.redirect(context.absolute_url())
