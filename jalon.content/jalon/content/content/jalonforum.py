# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.component import getMultiAdapter

from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT
from Products.CMFCore.utils import getToolByName

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonForum

import jalon_utils

JalonForumSchema = ATDocumentSchema.copy() + atpublic.Schema((
    atpublic.StringField("dateAff",
                         required=False,
                         accessor="getDateAff",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Date d'affichage"),
                                                      description=_(u"Description de la date d'affichage"),)
                         ),
    atpublic.StringField("dateMasq",
                         required=False,
                         accessor="getDateMasq",
                         searchable=False,
                         widget=atpublic.StringWidget(label=_(u"Date à laquelle cette activité est masquée"),
                                                      description=_(u"Date servant à masquer cette activité"),)
                         ),
))


class JalonForum(ATDocumentBase):
    """ un forum pour Jalon
    """

    implements(IJalonForum)
    meta_type = 'JalonForum'
    schema = JalonForumSchema
    schema['description'].required = True
    schema['description'].widget.label = "Sujet"
    schema['text'].required = False
    schema['text'].mode = "r"

    """
    def setAttributCours(self, form):
        self.setProperties(form)
        if "Title" in form:
            self.aq_parent.modifierInfosElementPlan(self.getId(), form["Title"])
        self.reindexObject()
    """

    def setProperties(self, dico):
        keys = dico.keys()
        if "Title" in keys:
            self.aq_parent.modifierInfosElementPlan(self.getId(), dico["Title"])
        for key in keys:
            self.__getattribute__("set%s" % key)(dico[key])
        self.reindexObject()

    def isAfficherElement(self):
        return jalon_utils.isAfficherElement(self.getDateAff(), self.getDateMasq())

    def afficherRessource(self, idElement, dateAffichage, attribut):
        if attribut == "affElement":
            self.dateAff = dateAffichage
            self.dateMasq = ""
            portal = self.portal_url.getPortalObject()
            portal_workflow = getToolByName(portal, "portal_workflow")
            if portal_workflow.getInfoFor(self, "review_state", wf_id="jalon_workflow") != "pending":
                portal_workflow.doActionFor(self, "submit", "jalon_workflow")
        else:
            self.dateMasq = dateAffichage
        self.aq_parent.modifierInfosBoitePlan(idElement, {"affElement": self.getDateAff(), "masquerElement": self.getDateMasq()})
        self.reindexObject()

    def getVue(self, request):
        forum_view = getMultiAdapter((self, request), name=u'forum_view')
        return forum_view

    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

registerATCT(JalonForum, PROJECTNAME)
