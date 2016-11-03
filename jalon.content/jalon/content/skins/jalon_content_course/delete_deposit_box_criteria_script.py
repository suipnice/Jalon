# Controller Python Script "delete_deposit_box_criteria_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

param = {}
form = context.REQUEST.form

criteria_dict = dict(context.getCriteriaDict())

del criteria_dict[form["criteria_id"]]

context.setCriteriaDict(criteria_dict)

if "deposit_box_criteria_view" in context.REQUEST.HTTP_REFERER:
    redirection = "%s/deposit_box_criteria_view" % context.absolute_url()
else:
    redirection = "%s?tab=peers" % context.absolute_url()

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection