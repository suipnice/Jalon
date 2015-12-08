## Controller Python Script "activite_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Activite edit
##

#context = context
form = context.REQUEST.form

dico = {}

#Cas de la boite de depot
if form["formulaire"] == "modifier-boite-info":
    dico = {"Title":                  form["title"],
            "Description":            form["description"]}

if form["formulaire"] == "modifier-boite-date":
    #dico = {"DateDepot": "%s/%s/%s %s:%s" % (form["dateDepot_year"], form["dateDepot_month"], form["dateDepot_day"], form["dateDepot_hour"], form["dateDepot_minute"]),
    #        "DateRetard": "%s/%s/%s %s:%s" % (form["dateRetard_year"], form["dateRetard_month"], form["dateRetard_day"], form["dateRetard_hour"], form["dateRetard_minute"])}
    dico = {"DateDepot": DateTime(form["datetime-depot"]), "DateRetard": DateTime(form["datetime-retard"])}

#if form["formulaire"].startswith("modifier-boite") and not "boite" in form["page"]:
#    redirection = "%s/%s" % (context.aq_parent.absolute_url(), form["page"])

#Cas de l'examen
if "duree" in form:
    dico = {"Title":       form["title"],
            "Description": form["description"],
            "note_max":    form["note_max"],
            "duree":       form["duree"],
            "attempts":    form["attempts"],
            "verrou":      form["verrou"],
            "wims_lang":   form["wims_lang"]}

elif "note_max" in form:
   #Cas de l'autoevaluation
    dico = {"Title":       form["title"],
            "Description": form["description"],
            "note_max":    form["note_max"],
            "wims_lang":   form["wims_lang"]}


context.setAttributActivite(dico)

# menu n'existe pas si on modifie l'activite depuis le plan du cours
if "menu" in form:
    redirection = "%s?menu=%s" % (context.absolute_url(), form["menu"])
else:
    redirection = context.aq_parent.absolute_url()

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection
