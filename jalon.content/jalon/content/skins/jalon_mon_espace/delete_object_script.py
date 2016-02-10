## Controller Python Script "delete_object_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##

from Products.CMFPlone import PloneMessageFactory as _
#from OFS.ObjectManager import BeforeDeleteException

req = context.REQUEST
paths = req.get('paths', [])
nonSup = req.get("nonSup", [])

for p in paths:
    if p in nonSup:
        paths.remove(p)

putils = context.plone_utils

status = 'failure'
message = _(u'Please select one or more items to delete.')

# a hint to the link integrity code to indicate the number of events to
# expect, so that all integrity breaches can be handled in a single form
# only;  normally the adapter (LinkIntegrityInfo) should be used here, but
# this would make CMFPlone depend on an import from LinkIntegrity, which
# it shouldn't...
context.REQUEST.set('link_integrity_events_to_expect', len(paths))

#Dans un cours
listeClasses = []
if "/cours/" in context.absolute_url():
    for path in paths:
        idcours = path.split("/")[-1]
        cours = getattr(context, idcours)
        #On recupere la liste des classes WIMS du cours.
        for dico in cours.getListeClasses():
            for key in dico.keys():
                listeClasses.append(dico[key])
        items = cours.getRelatedItems()
        for item in items:
            links = item.getRelatedItems()
            try:
                links.remove(cours)
                item.setRelatedItems(links)
                item.reindexObject()
            except:
                pass
        #suppression des tabBU sur les ressources
        cours.tagBU("remove")

# On supprime les exos coté Wims avant de le faire coté jalon
if context.getId() == "Wims":
    context.delExoWims(paths)
    #Ici il faudrait analyser le retour de Wims, et ne pas continuer à supprimer coté jalon en cas d'erreur.

success, failure = putils.deleteObjectsByPaths(paths, REQUEST=req)

if success:
    status = 'success'
    #Le message "elements supprimés" est maintenant géré en ajax
    #message = _(u'Item(s) deleted.')
    # Possible lenteur quand bcp d'objets dans le catalogue
    #catalog = context.portal_catalog
    #err = catalog.refreshCatalog(clear=True)
    #Suppressions suplementaires (sur les serveurs tiers)
    if listeClasses:
        context.delClassesWims(listeClasses, context.REQUEST)
    if context.getId() in ["Webconference", "Sonorisation"]:
        context.delEnregistrementConnect(paths)

if failure:
    # we want a more descriptive message when trying
    # to delete locked item
    from Products.CMFDefault.exceptions import ResourceLockedError
    other = []
    locked = []
    message = str(failure)
    for key, value in failure.items():
        # below is a clever way to check exception type
        try:
                raise value
        except ResourceLockedError:
                locked.append(key)
        except:
                other.append(key)
        else:
                other.append(key)
    # locked contains ids of items that cannot be deleted,
    # because they are locked; other contains ids of items
    # that cannot be deleted for other reasons;
    # now we need to construct smarter error message
    msgs = []
    mapping = {}

    if locked:
        mapping[u'lockeditems'] = ', '.join(locked)
        message = _(u'These items are locked for editing: ${lockeditems}.', mapping=mapping)
    else:
        mapping[u'items'] = ', '.join(other)
        message = _(u'${items} could not be deleted.', mapping=mapping)

    context.plone_utils.addPortalMessage(message)

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.restrictedTraverse(context.getMySpaceFolder())()
