## Controller Python Script "add_deposit_box_skill_script"
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

competences = dict(context.getCompetences())
clefs = competences.keys()
clefs.sort(lambda x, y: cmp(int(x), int(y)))

index = "1"
if competences:
    index = str(int(clefs[-1]) + 1)

competences[index] = {"titre"       : form["title"],
                      "evaluation"  : form["evaluation"],
                      "description" : form["description"]}

if form["evaluation"] == "note":
    competences[index]["note_max"] = form["note_max"]
    competences[index]["note_partielle"] = form["note_partielle"]
    competences[index]["note_acquise"] = form["note_acquise"]

context.setCompetences(competences)

redirection = "%s?tab=skills" % context.absolute_url()

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection
