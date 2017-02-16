# -*- coding: utf-8 -*-

from zope.interface import implements
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT

from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonTermeGlossaire

import jalon_utils
import copy

JalonTermeGlossaireSchema = ATDocumentSchema.copy()


class JalonTermeGlossaire(ATDocumentBase):
    """ Un terme de glossaire sous Jalon
    """

    implements(IJalonTermeGlossaire)
    meta_type = 'JalonTermeGlossaire'
    schema = JalonTermeGlossaireSchema
    schema['description'].required = True
    schema['description'].widget.label = "Définition"
    schema['text'].required = False
    schema['text'].mode = "r"

    def ajouterTag(self, tag):
        return jalon_utils.setTag(self, tag)

    def getAttributsType(self):
        return ["title", "description"]

    def getAttributsTypeMod(self):
        return {"title": "Title", "description": "Description"}

    def setProperties(self, dico):
        for key in dico.keys():
            self.__getattribute__("set%s" % key)(dico[key])
        self.reindexObject()
        items = self.getRelatedItems()
        #modification dans le cours
        for item in items:
            if item.portal_type in ["JalonCours"]:
                #modification du titre dans le cours
                element_cours = copy.deepcopy(item.getCourseItemProperties())
                if self.getId() in element_cours:
                    element_cours[self.getId()]["titreElement"] = self.Title()
                    item.setCourseItemsProperties(element_cours)

registerATCT(JalonTermeGlossaire, PROJECTNAME)
