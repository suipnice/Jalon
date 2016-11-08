## Controller Python Script "edit_wims_activity_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Activity WIMS edit script
##

# context = context
form = context.REQUEST.form

# dico = {}

# Cas de l'examen
if "duree" in form:
    dico = {"Title":       form["title"],
            "Description": form["description"],
            "Note_max":    form["note_max"],
            "Duree":       form["duree"],
            "Attempts":    form["attempts"],
            "Verrou":      form["verrou"],
            "Wims_lang":   form["wims_lang"]}

# Cas de l'autoevaluation
elif "note_max" in form:
    dico = {"Title":       form["title"],
            "Description": form["description"],
            "Note_max":    form["note_max"],
            "Wims_lang":   form["wims_lang"]}

# context.setAttributActivite(dico)
context.setProperties(dico)

# Met à jour le titre dans le plan du cours, et la date de dernière modif du cours.
if "Title" in dico:
    context.aq_parent.editCourseMapItem(context.getId(), dico["Title"], False)
    context.aq_parent.setCourseProperties({"DateDerniereModif": DateTime()})

# tab n'existe pas si on modifie l'activite depuis le plan du cours
if "tab" in form:
    redirection = "%s?tab=%s" % (context.absolute_url(), form["tab"])
else:
    redirection = context.aq_parent.absolute_url()

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection
