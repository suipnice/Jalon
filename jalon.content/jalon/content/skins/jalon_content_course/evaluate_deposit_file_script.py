## Controller Python Script "evaluate_deposit_file_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

context.setEvaluatePeer(form)

context.REQUEST.RESPONSE.redirect("%s?tab=peers" % context.absolute_url())
