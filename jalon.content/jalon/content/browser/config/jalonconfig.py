# -*- coding: utf-8 -*-

from zope.schema import List, TextLine, Bool
from zope.component import adapts
from zope.interface import Interface, implements

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets

from jalon.content import contentMessageFactory as _


class IJalonConfigFichiersControlPanel(Interface):

    """fields for jalon Config Fichiers control panel."""

    activer_fichiers = Bool(title=_(u"Activer la section Fichiers dans mon espace."),
                            description=_(u"Cocher pour activer la section Fichiers dans mon espace."),
                            default=False, required=False)
    fichiers = List(title=_(u"Fichiers : définition des étiquettes par défaut."),
                    description=_(u"Exemple : les types de fichiers"),
                    value_type=TextLine(), default=[], required=False)


class IJalonConfigSonorisationControlPanel(Interface):

    """fields for jalon Config Sonorisation control panel."""

    activer_sonorisation = Bool(title=_(u"Activer la section Présentation sonorisée dans mon espace."),
                            description=_(u"Cocher pour activer la section Présentation sonorisée dans mon espace, seulement possible si le produit jalon.connect est installé."),
                            default=False, required=False)
    sonorisation_connecteur = TextLine(title=_(u"Identifiant du connecteur connect."),
                             description=_(u"Pour la configuration par défaut de jalon.connect laisser portal_connect."),
                             default=u"portal_connect", required=False)
    sonorisation = List(title=_(u"Présentation sonorisée : définition des étiquettes par défaut."),
                         description=_(u"Exemple : le champ de date du portal_connect 'dateUS'"),
                         value_type=TextLine(), default=[], required=False)

    activer_webconference = Bool(title=_(u"Activer la section Webconférence dans mon espace."),
                            description=_(u"Cocher pour activer section la Webconference dans mon espace, seulement possible si le produit jalon.connect est installé."),
                            default=False, required=False)
    webconference_connecteur = TextLine(title=_(u"Identifiant du connecteur connect."),
                             description=_(u"Pour la configuration par défaut de jalon.connect laisser portal_connect."),
                             default=u"portal_connect", required=False)
    webconference = List(title=_(u"Webconférence : définition des étiquettes par défaut."),
                         description=_(u"Exemple : le champ de date du portal_connect 'dateUS'"),
                         value_type=TextLine(), default=[], required=False)


class IJalonConfigWimsControlPanel(Interface):

    """fields for jalon Config Wims control panel."""

    activer_wims = Bool(title=_(u"Activer la section Exercices Wims dans mon espace."),
                        description=_(u"Cocher pour activer la section Exercices Wims dans mon espace, seulement possible si le produit jalon.wims est installé."),
                        default=False, required=False)
    wims_connecteur = TextLine(title=_(u"Identifiant du connecteur wims."),
                             description=_(u"Pour la configuration par défaut de jalon.wims laisser portal_wims."),
                             default=u"portal_wims", required=False)
    wims = List(title=_(u"Exercices Wims : définition des étiquettes par défaut."),
                         description=_(u"Exemple : le modèle des exercices Wims 'modele'"),
                         value_type=TextLine(), default=[], required=False)
    wims_modele = List(title=_(u"Modèle Wims"),
                               description=_(u"Lister ici les modèles (du Wims Connector) que vous souhaitez utiliser pour la création d'exercices dans 'Mon espace'. Format : 'id*-*Titre du Modele*-*Categorie'  . Exemple : qcmsimple*-*Question simple*-*1 Modeles simples"),
                               value_type=TextLine(), default=[], required=False)


class IJalonConfigExterneControlPanel(Interface):

    """fields for jalon Config Externe control panel."""

    activer_externes = Bool(title=_(u"Activer la section Ressources externes dans mon espace."),
                            description=_(u"Cocher pour activer la section Ressources externes dans mon espace."),
                            default=False, required=False)
    externes = List(title=_(u"Externes : définition des étiquettes par défaut."),
                    description=_(u"Exemple : les types de ressources externes"),
                    value_type=TextLine(), default=[], required=False)
    activer_cataloguebu = Bool(title=_(u"Activer la section Catalogue BU dans mon espace."),
                               description=_(u"Cocher pour activer la section Catalogue BU dans mon espace."),
                               default=False, required=False)


class IJalonConfigGlossaireControlPanel(Interface):

    """fields for jalon Config Glossaire control panel."""

    activer_glossaire = Bool(title=_(u"Activer la section Glossaire dans mon espace."),
                            description=_(u"Cocher pour activer la section Glossaire dans mon espace."),
                            default=False, required=False)
    glossaire = List(title=_(u"Glossaire : définition des étiquettes par défaut."),
                     description=_(u"Exemple : les lettres de l'alphabet, une par case"),
                     value_type=TextLine(), default=[], required=False)

"""
class IJalonConfigWebconferenceControlPanel(Interface):

    \"""fields for jalon ConfigWebconference control panel.\"""

    activer_webconference = Bool(title=_(u"Activer la section Webconférence dans mon espace."),
                            description=_(u"Cocher pour activer la Webconference dans mon espace, seulement possible si le produit jalon.connect est installé."),
                            default=False, required=False)
    webconference_connecteur = TextLine(title=_(u"Identifiant du connecteur connect."),
                             description=_(u"Pour la configuration par défaut de jalon.connect laisser portal_connect."),
                             default=u"portal_connect", required=False)
    webconference = List(title=_(u"Webconference : définition des étiquettes par défaut."),
                         description=_(u"Exemple : le champ de date du portal_connect 'dateUS'"),
                         value_type=TextLine(), default=[], required=False)
"""


class IJalonConfigMAJControlPanel(Interface):

    """fields for jalon Config MAJ control panel."""

    activer_maj = Bool(title=_(u"Activer les notes de mise à jour de Jalon"),
                             description=_(u"Cocher pour activer les notes de mise à jour depuis la page mon espace"),
                             default=False, required=False)
    url_maj = TextLine(title=_(u"Url du RSS des notes de mise à jour de Jalon"),
                             description=_(u"Indiquez ici l'adresse du flux RSS utilisez pour les mises à jour de Jalon"),
                             default=u"http://wiki.unice.fr/createrssfeed.action?types=blogpost&sort=created&showContent=true&showDiff=true&spaces=JALON&labelString=maj_jalonv4&rssType=rss2&maxResults=1000&timeSpan=1000&publicFeed=true&title=Mises+à+jour+de+l%27Environnement+Pédagogique+Jalon", required=False)


class IJalonConfigControlPanel(IJalonConfigFichiersControlPanel,
                               IJalonConfigSonorisationControlPanel,
                               IJalonConfigWimsControlPanel,
                               IJalonConfigExterneControlPanel,
                               IJalonConfigGlossaireControlPanel,
                               IJalonConfigMAJControlPanel,):

    """Combined schema for the adapter lookup."""


class JalonConfigControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IJalonConfigControlPanel)

    def __init__(self, context):
        super(JalonConfigControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.jiProps = pprop.jalonconfig_properties

    def exclureNavigation(self, repertoire, exclure):
        recherche = {"portal_type" : "JalonFolder",
                     "id" : repertoire}
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        for result in portal_catalog.searchResults(recherche):
            objet = result.getObject()
            objet.setExcludeFromNav(exclure)
            objet.reindexObject()

    def get_activer_fichiers(self):
        return self.jiProps.getProperty('activer_fichiers')

    def set_activer_fichiers(self, value):
        self.jiProps._updateProperty('activer_fichiers', value)
        if not value:
            exclure = True
        else:
            exclure = False
        self.exclureNavigation("Fichiers", exclure)

    activer_fichiers = property(get_activer_fichiers, set_activer_fichiers)

    def get_fichiers(self):
        return self.jiProps.getProperty('fichiers')

    def set_fichiers(self, value):
        self.jiProps._updateProperty('fichiers', value)

    fichiers = property(get_fichiers, set_fichiers)

    def get_activer_sonorisation(self):
        return self.jiProps.getProperty('activer_sonorisation')

    def set_activer_sonorisation(self, value):
        self.jiProps._updateProperty('activer_sonorisation', value)
        if not value:
            exclure = True
        else:
            exclure = False
        self.exclureNavigation("Sonorisation", exclure)

    activer_sonorisation = property(get_activer_sonorisation, set_activer_sonorisation)

    def get_sonorisation_connecteur(self):
        return self.jiProps.getProperty('sonorisation_connecteur')

    def set_sonorisation_connecteur(self, value):
        self.jiProps._updateProperty('sonorisation_connecteur', value)

    sonorisation_connecteur = property(get_sonorisation_connecteur, set_sonorisation_connecteur)

    def get_sonorisation(self):
        return self.jiProps.getProperty('sonorisation')

    def set_sonorisation(self, value):
        self.jiProps._updateProperty('sonorisation', value)

    sonorisation = property(get_sonorisation, set_sonorisation)

    def get_activer_wims(self):
        return self.jiProps.getProperty('activer_wims')

    def set_activer_wims(self, value):
        self.jiProps._updateProperty('activer_wims', value)
        if not value:
            exclure = True
        else:
            exclure = False
        self.exclureNavigation("Wims", exclure)

    activer_wims = property(get_activer_wims, set_activer_wims)

    def get_wims_connecteur(self):
        return self.jiProps.getProperty('wims_connecteur')

    def set_wims_connecteur(self, value):
        self.jiProps._updateProperty('wims_connecteur', value)

    wims_connecteur = property(get_wims_connecteur, set_wims_connecteur)

    def get_wims(self):
        return self.jiProps.getProperty('wims')

    def set_wims(self, value):
        self.jiProps._updateProperty('wims', value)

    wims = property(get_wims, set_wims)

    def get_wims_modele(self):
        return self.jiProps.getProperty('wims_modele')

    def set_wims_modele(self, value):
        self.jiProps._updateProperty('wims_modele', value)

    wims_modele = property(get_wims_modele, set_wims_modele)

    def get_activer_externes(self):
        return self.jiProps.getProperty('activer_externes')

    def set_activer_externes(self, value):
        self.jiProps._updateProperty('activer_externes', value)
        if not value:
            exclure = True
        else:
            exclure = False
        self.exclureNavigation("Externes", exclure)

    activer_externes = property(get_activer_externes, set_activer_externes)

    def get_externes(self):
        return self.jiProps.getProperty('externes')

    def set_externes(self, value):
        self.jiProps._updateProperty('externes', value)

    externes = property(get_externes, set_externes)

    def get_activer_cataloguebu(self):
        return self.jiProps.getProperty('activer_cataloguebu')

    def set_activer_cataloguebu(self, value):
        self.jiProps._updateProperty('activer_cataloguebu', value)
        if not value:
            exclure = True
        else:
            exclure = False
        self.exclureNavigation("CatalogueBU", exclure)

    activer_cataloguebu = property(get_activer_cataloguebu, set_activer_cataloguebu)

    def get_cataloguebu(self):
        return []

    def get_activer_glossaire(self):
        return self.jiProps.getProperty('activer_glossaire')

    def set_activer_glossaire(self, value):
        self.jiProps._updateProperty('activer_glossaire', value)
        if not value:
            exclure = True
        else:
            exclure = False
        self.exclureNavigation("Glossaire", exclure)

    activer_glossaire = property(get_activer_glossaire, set_activer_glossaire)

    def get_glossaire(self):
        return self.jiProps.getProperty('glossaire')

    def set_glossaire(self, value):
        self.jiProps._updateProperty('glossaire', value)

    glossaire = property(get_glossaire, set_glossaire)

    def get_activer_webconference(self):
        return self.jiProps.getProperty('activer_webconference')

    def set_activer_webconference(self, value):
        self.jiProps._updateProperty('activer_webconference', value)
        if not value:
            exclure = True
        else:
            exclure = False
        self.exclureNavigation("Webconference", exclure)

    activer_webconference = property(get_activer_webconference, set_activer_webconference)

    def get_webconference_connecteur(self):
        return self.jiProps.getProperty('webconference_connecteur')

    def set_webconference_connecteur(self, value):
        self.jiProps._updateProperty('webconference_connecteur', value)

    webconference_connecteur = property(get_webconference_connecteur, set_webconference_connecteur)

    def get_webconference(self):
        return self.jiProps.getProperty('webconference')

    def set_webconference(self, value):
        self.jiProps._updateProperty('webconference', value)

    webconference = property(get_webconference, set_webconference)

    def get_activer_maj(self):
        return self.jiProps.getProperty('activer_maj')

    def set_activer_maj(self, value):
        self.jiProps._updateProperty('activer_maj', value)

    activer_maj = property(get_activer_maj, set_activer_maj)

    def get_url_maj(self):
        return self.jiProps.getProperty('url_maj')

    def set_url_maj(self, value):
        self.jiProps._updateProperty('url_maj', value)

    url_maj = property(get_url_maj, set_url_maj)

    def getAllActiver(self):
        return {"fichiers"      : self.get_activer_fichiers(),
                "externes"      : self.get_activer_externes(),
                "glossaire"     : self.get_activer_glossaire(),
                "webconference" : self.get_activer_webconference(),
                "sonorisation"  : self.get_activer_sonorisation(),
                "wims"          : self.get_activer_wims(),
                "cataloguebu"   : self.get_activer_cataloguebu(),
                "maj"           : self.get_activer_maj(),
               }

configfichierset = FormFieldsets(IJalonConfigFichiersControlPanel)
configfichierset.id = 'configfichier'
configfichierset.label = _(u"Fichiers")

configsonorisationset = FormFieldsets(IJalonConfigSonorisationControlPanel)
configsonorisationset.id = 'configsonorisation'
configsonorisationset.label = _(u"Présentation sonorisée & Webconférence")

configgwimsset = FormFieldsets(IJalonConfigWimsControlPanel)
configgwimsset.id = 'configwims'
configgwimsset.label = _(u"Exercices WIMS")

configexternesset = FormFieldsets(IJalonConfigExterneControlPanel)
configexternesset.id = 'configexternes'
configexternesset.label = _(u"Ressources externes & Catalogue BU")

configglossaireset = FormFieldsets(IJalonConfigGlossaireControlPanel)
configglossaireset.id = 'configglossaire'
configglossaireset.label = _(u"Termes de glossaire")

#configwebconferenceset = FormFieldsets(IJalonConfigWebconferenceControlPanel)
#configwebconferenceset.id = 'configwebconference'
#configwebconferenceset.label = _(u"Webconférence")

configmajset = FormFieldsets(IJalonConfigMAJControlPanel)
configmajset.id = 'configmaj'
configmajset.label = _(u"Mise à jour")


class JalonConfigControlPanel(ControlPanelForm):

    label = _("Jalon Content Config")
    description = _("""Configuration des contenus de Jalon""")
    form_name = _("Jalon Content Config")
    form_fields = FormFieldsets(configfichierset, configsonorisationset, configgwimsset, configexternesset, configglossaireset, configmajset)
