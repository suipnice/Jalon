# -*- coding: utf-8 -*-
"""Controller Python Script "create_wims_exercice_group_script"."""
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajout et/ou modification d'un groupe d'exercices WIMS
##

from Products.CMFPlone import PloneMessageFactory as _
#context = context
form = context.REQUEST.form

wims_exercice_model = form["modele"]
user_id = context.supprimerCaractereSpeciaux(form["authMember"])
wims_exercice_folder = context.getMySubSpaceFolder(user_id, "Wims")

if "idobj" not in form:
    # Ajouter un nouveau groupe
    object_id = wims_exercice_folder.invokeFactory(type_name='JalonExerciceWims', id="%s-%s-%s" % (wims_exercice_model, user_id, DateTime().strftime("%Y%m%d%H%M%S")))
    message = "groupe_added"
else:
    # Modifier un groupe (pour plus tard...)
    object_id = form["idobj"]

# obj est un element de type "jalonexercicewims"
obj = getattr(wims_exercice_folder, object_id)

group_title = ""
if form["title"] != "":
    if "paths" in form:
        listeIdsExos = []
        for path in form["paths"]:
            if "groupe-" not in path:
                listeIdsExos.append(path.split("/")[-1])
        obj.setProperties({"Title": form["title"],
                           "Modele": wims_exercice_model,
                           "Qnum": form["qnum"],
                           "ListeIdsExos": listeIdsExos})
        rep = obj.ajouterSerie(user_id)
    else:
        rep = {"status": "ERROR", "err_code": "no_exercice_selected", "message": _(u"Aucun exercice selectionné")}
    group_title = u"« %s »" % obj.Title().decode("utf-8")
else:
    rep = {"status": "ERROR", "err_code": "no_title", "message": _(u"Le titre est obligatoire")}


if not("status" in rep):
    # La creation a planté (Cause ?)
    wims_exercice_folder.manage_delObjects(ids=[object_id])
    message = "unknown_error"
else:
    if rep["status"] != "OK":
        if "err_code" in rep:
            message = rep["message"]
        else:
            # Comment se retrouver ici ? ajouterSerie() ne fait aucun appel au serveur WIMS...
            # Ici il faudrait envoyer un mail auto à l'admin.
            message = "Une erreur inconnue est survenue. merci de de contacter l'administrateur du site svp..."
        context.plone_utils.addPortalMessage(_(u"Votre groupe d'exercices %s n'a pas été créé.<div><strong>%s</strong></div>" % (group_title, message)), 'error')
        # La creation n'a pas aboutit coté WIMS, on supprime l'objet que l'on vient de créer sur Jalon.
        wims_exercice_folder.manage_delObjects(ids=[object_id])
    else:
        context.plone_utils.addPortalMessage(_(u"Votre groupe d'exercices %s a bien été créé." % group_title), 'success')

# Tant qu'il n'y a pas de page de modification des groupes d'exos, on retourne sur la page precedente.
return context.REQUEST.RESPONSE.redirect(context.absolute_url())
