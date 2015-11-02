# -*- coding: utf-8 -*-
##Script (Python) "valider_form"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validation des formulaires
##

from Products.CMFPlone import PloneMessageFactory as _

#context.plone_log("[valider_form]")
error = False
form = context.REQUEST.form
formulaire = str(form["formulaire"])

if "ajout_espace" in form:
    formulaire = "-".join([formulaire, form["ajout_espace"]])

if "annexe" in form:
    formulaire = "-".join([formulaire, form["annexe"]])

dicoObligatoire = {"ajout-activite":                     ["title"],
                   "ajout-annonce":                      ["title", "description"],
                   "ajout-forum":                        ["title", "description"],
                   "ajout-cours":                        ["title"],
                   "ajout-depot":                        ["title", "file_file"],
                   "ajout-competence":                   ["title", "evaluation"],
                   "ajout-externe":                      ["title"],
                   "ajout-glossaire":                    ["title", "description"],
                   "ajout-video":                        ["title", "lecteur"],
                   "ajout-web":                          ["title", "urlbiblio"],
                   "ajout-wims":                         ["title"],
                   "ajout-elements-fichiers":            ["file_file"],
                   "ajout-elements-ressources-externes": ["title", "lien"],
                   "ajout-conversation":                 ["title", "text"],
                   "ajout-reponse":                      ["text"],
                   "importer-exercices":                 ["file"],
                   "modifier-activite":                  ["title"],
                   "modifier-annonce":                   ["title", "description"],
                   "modifier-boite-info":                ["title"],
                   "modifier-boite-date":                [],
                   "modifier-competences":               [],
                   "modifier-correction":                [],
                   "modifier-note":                      [],
                   "modifier-externe-cataloguebu":       ["description"],
                   "modifier-externe-lecteur":           ["title", "lecteur"],
                   "modifier-externe-pod":               ["title", "description"],
                   "modifier-externe-lien":              ["title", "urlbiblio"],
                   "modifier-externe-reference":         ["title", "description", "auteurs"],
                   "modifier-forum":                     ["title", "description"],
                   "modifier-conversation":              ["title", "text"],
                   "modifier-glossaire":                 ["title", "description"],
                   "modifier-plan":                      ["description"],
                   "modifier-libre":                     [],
                   "modifier-itunesu":                   ["catiTunesU"],
                   "modifier-fichier":                   ["title"],
                   "modifier-titre":                     ["title"],
                   "ajouter-invitations-email":          [],
                   "supprimer-competences":              [],
                   "ecrire":                             ["objet", "message"],
                   "creer_categorie":                    ["title"],
                   "renommer_categorie":                 ["title"],
                   "modifier_categorie":                 ["categorie"],
                   "etiqueter":                          [],
                   "creer-seance":                       ["intitule"],
                   "inscription-cours":                  ["motdepasse"],
                   "maj-photo":                          ["file_file"],
                   "tag":                                ["title"]
                  }

retour = context.absolute_url()
numeriques_Obligatoires = []

#Cas des activités
if formulaire in ["modifier-activite", "ajout-activite"]:

    # Les parenthèses doivent être placées par paires correctement fermées pour WIMS.
    listeReplace_desc_wims = [["{", "}", u"Accolades"],
                              ["(", ")", u"Parenthèses"],
                              ["[", "]", u"Crochets"]]
    desc = form["description"]
    incoherence = []
    typ_parenthese = ""
    for couple in listeReplace_desc_wims:
        nb_ouvre = desc.count(couple[0])
        nb_ferme = desc.count(couple[1])
        if nb_ouvre != nb_ferme:
            incoherence.append("%s '%s' contre %s '%s'" % (nb_ouvre, couple[0], nb_ferme, couple[1]))
            typ_parenthese = couple[2]
    if len(incoherence) > 0:
        incoherence = " et ".join(incoherence)
        state.setError("description", _(u"%s mal fermées : %s" % (typ_parenthese, incoherence)), "bad_parenthesis")
        state.set(status='failure')
        error = True

    #Cas de l'examen
    if "duree" in form:
        numeriques_Obligatoires = ["note_max", "duree", "attempts"]
    #Cas de l'autoevaluation
    elif "note_max" in form:
        numeriques_Obligatoires = ["note_max"]

    dicoObligatoire[formulaire].extend(numeriques_Obligatoires)

if formulaire == "modifier-invitations":
    if "invitation" in form and form["invitation"]:
        if not "," in form["invitation"]:
            listeInvitations = [form["invitation"]]
        else:
            listeInvitations = form["invitation"].split(",")
        for invitation in listeInvitations:
            if " " in invitation:
                nameInvit, emailInvit = invitation.rsplit(" ", 1)
            else:
                emailInvit = invitation
            emailInvit = emailInvit.replace("<", "")
            emailInvit = emailInvit.replace(">", "")
            if not "@" in emailInvit:
                state.setError("invitation", _(u"Un courriel saisi est non valide, merci de corriger"), "invitation_required")
                state.set(status='failure')
                error = True
            else:
                base, extension = emailInvit.rsplit("@", 1)
                if not "." in extension:
                    state.setError("invitation", _(u"Un courriel saisi est non valide, merci de corriger"), "invitation_required")
                    state.set(status='failure')
                    error = True
                else:
                    domain, pays = emailInvit.rsplit(".", 1)
                    if len(pays) < 2:
                        state.setError("invitation", _(u"Un courriel saisi est non valide, merci de corriger"), "invitation_required")
                        state.set(status='failure')
                        error = True

for obligatoire in dicoObligatoire[formulaire]:
    if not obligatoire in form:
        state.setError(obligatoire, _(u"Champ obligatoire"), "%s_required" % obligatoire)
        state.set(status='failure')
        error = True
    elif (not form[obligatoire]) or form[obligatoire] in ["", " ", None]:
        state.setError(obligatoire, _(u"Champ obligatoire"), "%s_required" % obligatoire)
        state.set(status='failure')
        error = True

for obligatoire in numeriques_Obligatoires:
    if not form[obligatoire].isdigit():
        state.setError(obligatoire, _(u"Vous devez taper un nombre"), "%s_required" % obligatoire)
        state.set(status='failure')
        error = True

if formulaire == "inscription-cours" and not error:
    cours = getattr(getattr(context.aq_parent, form["createur"]), form["idcours"], None)
    if not cours:
        cours = getattr(getattr(context.aq_parent, form["auteur"]), form["idcours"], None)
    if form["motdepasse"] != cours.getLienMooc():
        state.setError(obligatoire, _(u"Mot de passe incorrect"), "%s_required" % obligatoire)
        state.set(status='failure')
        error = True

if formulaire == "ajout-competence" and "evaluation" in form and form["evaluation"] == "note":
    obligatoires = ["note_max", "note_partielle", "note_acquise"]
    for obligatoire in obligatoires:
        if form[obligatoire] == "":
            state.setError(obligatoire, _(u"Champ obligatoire"), "%s_required" % obligatoire)
            state.set(status='failure')
            error = True
    if not error:
        if int(form["note_max"]) < int(form["note_partielle"]):
            state.setError("note_partielle", _(u"La note partielle doit être inférieure ou égale à la note maximale"), "%s_required" % obligatoire)
            state.set(status='failure')
            error = True
        if int(form["note_max"]) < int(form["note_acquise"]):
            state.setError("note_acquise", _(u"La note d'acquisition doit être inférieure ou égale à la note maximale"), "%s_required" % obligatoire)
            state.set(status='failure')
            error = True
        if int(form["note_acquise"]) < int(form["note_partielle"]):
            state.setError("note_acquise", _(u"La note d'acquisition doit être supérieure ou égale à la note \"en cours d'acquisition à partir de\""), "%s_required" % obligatoire)
            state.set(status='failure')
            error = True

if not error:
    state.set(status="success-%s" % formulaire)

#context.REQUEST.set("retour", retour)
return state
