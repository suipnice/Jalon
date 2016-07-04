# Controller Python Script "redo_deposit_box_criteria_script"
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

criteria_id = form["criteria_id"]
criteria_dict[criteria_id]["coefficient"] = form["coefficient"]
context.setCriteriaDict(criteria_dict)

redirection = "%s/deposit_box_criteria_view?criteria_id=%s" % (context.absolute_url(), criteria_id)

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection