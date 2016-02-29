## Script (Python) "detach_object_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
if request.has_key("listeCours"):
    idElement = request["ressource"]
    objet = getattr(context, idElement)
    relatedItems = objet.getRelatedItems()

    brains = context.portal_catalog(path={"query": request["listeCours"], "depth": 0})

    isBiblioOrGlo = False
    if objet.portal_type in ["JalonRessourceExterne", "JalonTermeGlossaire"]:
        isBiblioOrGlo = True
    for brain in brains:
        cours = brain.getObject()
        relatedItems.remove(cours)
        if "." in idElement:
            idElement = idElement.replace(".", "*-*")
        if cours.portal_type == "JalonCours":
            try:
                if request.form["type"] == "Catalogue BU":
                    cours.tagBU("remove", idElement)
            except:
                pass
            cours.retirerElementPlan(idElement, None)
            if isBiblioOrGlo:
                cours.retirerElement(idElement)
        else:
            cours.retirerElement(idElement, "sujets")

    objet.setRelatedItems(relatedItems)
    objet.reindexObject()

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.restrictedTraverse(context.getMySpaceFolder())()
