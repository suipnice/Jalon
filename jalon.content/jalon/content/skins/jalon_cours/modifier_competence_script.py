## Controller Python Script "modifier_competence_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

competences = dict(context.getCompetences())
for competence in form["competences"]:
    if competence["titre"]:
        competences[competence["id"]]["titre"] = competence["titre"]
    if competences[competence["id"]]["evaluation"] == "note":
        competences[competence["id"]]["note_max"] = competence["note_max"]
        competences[competence["id"]]["note_partielle"] = competence["note_partielle"]
        competences[competence["id"]]["note_acquise"] = competence["note_acquise"]
    competences[competence["id"]]["description"] = competence["description"]

context.setCompetences(competences)
context.REQUEST.RESPONSE.redirect("%s?menu=competences" % context.absolute_url())