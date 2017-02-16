# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonConnect

import copy
import jalon_utils

JalonConnectSchema = ATDocumentSchema.copy() + atpublic.Schema((
    atpublic.StringField(
        'dateAjout',
        required = False,
        accessor = 'getDateAjout',
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"Date de création sur Adobe Connect")
            )),
    atpublic.StringField(
        "duree",
        required = False,
        accessor = "getDuree",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"Durée"),
            )),
    atpublic.StringField(
        "dateUS",
        required = False,
        accessor = "getDateUS",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"La date US"),
            )),
    atpublic.StringField(
        "urlEnr",
        required = False,
        accessor = "getUrlEnr",
        searchable = False,
        widget = atpublic.StringWidget(
            label = _(u"URL de l'enregistrement Connect"),
            )),
    ))


class JalonConnect(ATDocumentBase):
    """ Un enregistrement Adobe Connect
    """

    implements(IJalonConnect)
    meta_type = 'JalonConnect'
    schema = JalonConnectSchema
    schema['description'].required = False
    schema['description'].mode = "r"
    schema['text'].required = False
    schema['text'].mode = "r"

    def ajouterTag(self, tag):
        return jalon_utils.setTag(self, tag)

    def setProperties(self, dico):
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        self.reindexObject()
        items = self.getRelatedItems()
        for item in items:
            if item.portal_type in ["JalonCours"]:
                #modification du titre dans le cours
                element_cours = copy.deepcopy(item.getCourseItemProperties())
                if self.getId() in element_cours:
                    element_cours[self.getId()]["titreElement"] = self.Title()
                    item.setCourseItemsProperties(element_cours)
            if item.portal_type in ["JalonBoiteDepot", "JalonCoursWims"]:
                #modification du titre dans les boite de depots
                dico = copy.deepcopy(item.getDocumentsProperties())
                if self.getId() in dico:
                    dico[self.getId()]["titreElement"] = self.Title()
                    #item.setInfos_element(dico)
                    item.setDocumentsProperties(dico)

registerATCT(JalonConnect, PROJECTNAME)
