# -*- coding: utf-8 -*-
## Controller Python Script "ajouterexercicewims_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajout et/ou modification d'un exercice WIMS
##
#context = context

# PloneMessageFactory permet d'utiliser le systeme i18n
from Products.CMFPlone import PloneMessageFactory as _

REQUEST = context.REQUEST
form = REQUEST.form

modele = form["modele"]

if not "idobj" in form:
    #--ajouter un nouvel exo--
    idobj = context.invokeFactory(type_name='JalonExerciceWims',
                                  id="%s-%s-%s" % (modele, context.supprimerCaractereSpeciaux(REQUEST["authMember"]), DateTime().strftime("%Y%m%d%H%M%S")))
    message = "exercice_added"
    page_url = "%s/%s/exercicewims_edit?" % (context.absolute_url(), idobj)
    param = None
else:
   #--modifier un exo existant --
    param = form
    idobj = form["idobj"]
    message = "exercice_modified"
    context = context.aq_parent
    # url de retour vers la liste des exercices :
    # page_url = "%s?" % (context.absolute_url())
    if "save_and_test" in form:
        # url de test direct de l'exercice actuel :
        page_url = "%s/%s/view?" % (context.absolute_url(), idobj)
    else:
        # url de modification de l'exercice
        page_url = "%s/%s/exercicewims_edit?" % (context.absolute_url(), idobj)

#obj est un element de type "jalonexercicewims"
obj = getattr(context, idobj)

# Cas des Modules externes
if modele == "externe":
    permalink = REQUEST.get("permalink", '')
    obj.setProperties({"Title": form["title"],
                       "Modele": modele,
                       "Permalink": permalink,
                       })

# Cas classique : on ajoute l'exercice côté WIMS
else:
    rep = obj.addExoWims(idobj, form["title"], REQUEST["authMember"], modele, param)
    #print rep
    if not("status" in rep):
        # La creation a planté (Cause : modele inconnu ?)
        context.manage_delObjects(ids=[idobj])
        message = "unknown_model"
    else:
        #L'appel à WIMS s'est bien passé, on applique les modifications à l'objet Jalon
        if rep["status"] == "OK":
            obj.setProperties({"Title": form["title"],
                               "Modele": modele,
                               })
        else:
            # La creation a planté coté WIMS
            if "idobj" in REQUEST:
                #en cas de modification, on suppose que la creation a planté suite a une erreur de syntaxe.
                message = "wims_syntax_error"
                page_url = "%s/%s/exercicewims_edit?" % (context.absolute_url(), idobj)
            else:
                # En cas de creation, on supprime l'objet que l'on vient de créer sur Jalon.
                context.manage_delObjects(ids=[idobj])
                message = "wims_unavailable"
                page_url = "%s/?" % context.absolute_url()

#On encode le titre pour qu'il passe correctement dans l'url
title = obj.Title().replace("&", "%26").replace(";", "%3B").replace(" ", "%20")

redirection = "%smessage=%s&title=%s" % (page_url, message, title)

if message == "exercice_added":
    context.plone_utils.addPortalMessage(_(u"L'exercice « %s » a été ajouté. Construisez-le ci-dessous." % obj.Title().decode("utf-8")), 'success')
elif message == "exercice_modified":
    context.plone_utils.addPortalMessage(_(u"Votre exercice « %s » a bien été modifié." % obj.Title().decode("utf-8")),'success')


if "formulaire" in form:
    return redirection
else:
    context.REQUEST.RESPONSE.redirect(redirection)
