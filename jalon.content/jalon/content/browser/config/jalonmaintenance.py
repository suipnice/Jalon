# -*- coding: utf-8 -*-
from zope.schema import Bool, Text, TextLine
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import Interface, implements

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel.form import ControlPanelForm


from jalon.content import contentMessageFactory as _


class IJalonMaintenanceControlPanel(Interface):
    """
    fields for jalon maintenance control panel
    """
    annoncer_maintenance = Bool(title=_(u"Annonce maintenance du site"),
                                description=_(u"Affiche un message d'annonce de la prochaine maintenance du site."),
                                default=False,
                                required=False)

    activer_maintenance = Bool(title=_(u"Mise en maintenance du site"),
                               description=_(u"Empêche les utilisateurs de se connecter au site."),
                               default=False,
                               required=False)

    date_debut = TextLine(title=_(u"Date de début de maintenance"),
                          description=_(u"Date du début de la maintenance dans le texte informatif."),
                          required=True)

    date_fin = TextLine(title=_(u"Date de fin de maintenance"),
                        description=_(u"Date de fin de la maintenance dans le texte informatif."),
                        required=True)

    texte_maintenance = Text(title=_(u"Texte de la maintenance"),
                             description=_(u"Texte informatif pour la maintenance du site."),
                             required=True)

    activer_information = Bool(title=_(u"Afficher une information sur le site"),
                               description=_(u"Affiche une information sur le site."),
                               default=False,
                               required=False)

    texte_information = Text(title=_(u"Texte d'information"),
                             description=_(u"Texte informatif pour le site."),
                             required=True)

    annoncer_vider_cache = Bool(title=_(u"Annonce « Vider son cache »"),
                                description=_(u"Affiche un message demandant de vider son cache suite à une mise à jour."),
                                default=False,
                                required=False)


class JalonMaintenanceControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IJalonMaintenanceControlPanel)

    def __init__(self, context):
        super(JalonMaintenanceControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.jiProps = pprop.jalonmaintenance_properties

    def get_annoncer_maintenance(self):
        return self.jiProps.getProperty('annoncer_maintenance')

    def set_annoncer_maintenance(self, value):
        self.jiProps._updateProperty('annoncer_maintenance', value)

    annoncer_maintenance = property(get_annoncer_maintenance, set_annoncer_maintenance)

    def get_activer_maintenance(self):
        return self.jiProps.getProperty('activer_maintenance')

    def set_activer_maintenance(self, value):
        self.jiProps._updateProperty('activer_maintenance', value)

    activer_maintenance = property(get_activer_maintenance, set_activer_maintenance)

    def get_date_debut(self):
        return self.jiProps.getProperty('date_debut')

    def set_date_debut(self, value):
        self.jiProps._updateProperty('date_debut', value)

    date_debut = property(get_date_debut, set_date_debut)

    def get_date_fin(self):
        return self.jiProps.getProperty('date_fin')

    def set_date_fin(self, value):
        self.jiProps._updateProperty('date_fin', value)

    date_fin = property(get_date_fin, set_date_fin)

    def get_texte_maintenance(self):
        return self.jiProps.getProperty('texte_maintenance')

    def set_texte_maintenance(self, value):
        self.jiProps._updateProperty('texte_maintenance', value)

    texte_maintenance = property(get_texte_maintenance, set_texte_maintenance)

    def get_activer_information(self):
        return self.jiProps.getProperty('activer_information')

    def set_activer_information(self, value):
        self.jiProps._updateProperty('activer_information', value)

    activer_information = property(get_activer_information, set_activer_information)

    def getMaintenance(self):
        return {"annoncer_maintenance": self.get_annoncer_maintenance(),
                "activer_maintenance": self.get_activer_maintenance(),
                "date_debut": self.get_date_debut(),
                "date_fin": self.get_date_fin(),
                "texte_maintenance": self.get_texte_maintenance().replace("\n", "<br/>"),
               }

    def get_texte_information(self):
        return self.jiProps.getProperty('texte_information')

    def set_texte_information(self, value):
        self.jiProps._updateProperty('texte_information', value)

    texte_information = property(get_texte_information, set_texte_information)

    def getInformation(self):
        return {"activer_information": self.get_activer_information(),
                "texte_information": self.get_texte_information().replace("\n", "<br/>"),
               }

    def get_annoncer_vider_cache(self):
        return self.jiProps.getProperty('annoncer_vider_cache')

    def set_annoncer_vider_cache(self, value):
        self.jiProps._updateProperty('annoncer_vider_cache', value)

    annoncer_vider_cache = property(get_annoncer_vider_cache, set_annoncer_vider_cache)

    def getViderCache(self):
        return {"annoncer_vider_cache": self.get_annoncer_vider_cache()
               }


class JalonMaintenanceControlPanel(ControlPanelForm):

    label = _(u"Jalon maintenance settings")
    description = _(u"Mise en maintenance de Jalon")
    form_name = _(u"Jalon maintenance settings")
    form_fields = FormFields(IJalonMaintenanceControlPanel)
