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

redirection = "%s?tab=peers" % context.absolute_url()
if "teacher" in form:
    redirection = "%s/deposit_box_details_evaluations_view" % context.absolute_url()

context.REQUEST.RESPONSE.redirect(redirection)
