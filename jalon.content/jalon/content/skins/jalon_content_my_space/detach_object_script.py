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

    for brain in brains:
        parent = brain.getObject()
        relatedItems.remove(parent)
        if "." in idElement:
            idElement = idElement.replace(".", "*-*")
        if parent.portal_type == "JalonCours":
            try:
                if request.form["type"] == "Catalogue BU":
                    parent.tagBU("remove", idElement)
            except:
                pass
            if objet.portal_type == "JalonTermeGlossaire":
                parent.detachGlossaryItem(idElement)
            elif objet.portal_type == "JalonRessourceExterne":
                parent.detachBibliographyItem(idElement)
                parent.deleteCourseMapItem(idElement, None)
            else:
                parent.deleteCourseMapItem(idElement, None)
        else:
            parent.detachDocument(idElement)

    objet.setRelatedItems(relatedItems)
    objet.reindexObject()

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.restrictedTraverse(context.getMySpaceFolder())()
