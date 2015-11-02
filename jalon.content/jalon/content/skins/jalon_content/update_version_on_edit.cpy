## Script (Python) "update_version_on_edit"
##title=Edit Content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##

from Products.CMFCore.utils import getToolByName
from Products.CMFEditions import CMFEditionsMessageFactory as _
from Products.CMFEditions.utilities import isObjectChanged, maybeSaveVersion
from Products.CMFEditions.interfaces.IModifier import FileTooLargeToVersionError

putils = getToolByName(context, 'plone_utils')
REQUEST = context.REQUEST
comment = REQUEST.get('cmfeditions_version_comment', '')
force = REQUEST.get('cmfeditions_save_new_version', None) is not None

if not (isObjectChanged(context) or force):
    return state.set(status='success')

try:
    maybeSaveVersion(context, comment=comment, force=force)
except FileTooLargeToVersionError:
    putils.addPortalMessage(
        _("Versioning for this file has been disabled because it is too large"),
        type="warn"
        )

#if "Members" in REQUEST["ACTUAL_URL"]:
#    try:
#        context.setTagDefaut()
#    except:
#        context.aq_parent.setTagDefaut(context)

modItems = False
listeItems = []
items = context.getRelatedItems()
#return "items %s" % str(items)
for item in items:
    # à refaire pour "AutoEvaluation-Examen",  "Boite de depots"
    if item.Type() == "Jalon Cours":
        dico = dict(item.getInfosElement())
        if dico:
            idObj = context.getId().replace(".", "*-*")
            if idObj in dico:
                dico[idObj]["titreElement"] = context.REQUEST.form["title"]
                item.setElementsCours(dico)
                listeItems.append(item)
            else:
                modItems = True
#if modItems:
#    context.setRelatedItems(listeItems)


return state.set(status='success')
