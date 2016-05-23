# Controller Python Script "add_deposit_box_criteria_script"
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
keys = criteria_dict.keys()
keys.sort(lambda x, y: cmp(int(x), int(y)))

index = "1"
if criteria_dict:
    index = str(int(keys[-1]) + 1)

criteria_dict[index] = {"title":       form["title"],
                        "description": form["description"],
                        "notation":    form["notation"],
                        "coefficient": form["coefficient"]}

context.setCriteriaDict(criteria_dict)

redirection = "%s?tab=peers" % context.absolute_url()

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection