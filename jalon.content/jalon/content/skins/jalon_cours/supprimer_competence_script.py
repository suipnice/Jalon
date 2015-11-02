## Controller Python Script "supprimer_competence_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

if "competence_id" in form:
    competences = dict(context.getCompetences())
    for competence_id in form["competence_id"]:
        del competences[competence_id]

    context.setCompetences(competences)
context.REQUEST.RESPONSE.redirect("%s?menu=competences" % context.absolute_url())