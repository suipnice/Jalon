# -*- coding: utf-8 -*-


from zope.schema import TextLine, Bool, Text
#from zope.schema import Dict, Choice
from zope.component import adapts
from zope.interface import Interface, implements

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets

from jalon.content import contentMessageFactory as _


class IJalonConfigAnalyticsControlPanel(Interface):
    """
    fields for Config Analytics control panel
    """
    id_account = TextLine(title=_(u"Identifiant Google Analytics."),
                          description=_(u"Exemple : UA-12345678-1"),
                          default=u"UA-12345678-1", required=True)
    id_domain = TextLine(title=_(u"Domaine du site."),
                         description=_(u"Exemple : unice.fr"),
                         default=u"unice.fr", required=True)
    chemin_encodage = TextLine(title=_(u"Clé de cryptage"),
                               description=_(u"Une clé de cryptage des identifants sera créée. Pensez à sauvegarder le fichier. Exemple : /var/secret"),
                               default=u"", required=True)


class IJalonConfigLDAPControlPanel(Interface):
    """
    fields for Config LDAP control panel
    TODO : Placer ici les configs génériques pour la connexion LDAP
    """
    activer_ldap = Bool(title=_(u"Exemple de champ générique"),
                        description=_(u"Cocher pour activer ce champ générique"),
                        default=False,
                        required=False)
    fiche_ldap = TextLine(title=_(u"Chemin vers une fiche de votre annuaire"),
                          description=_(u"exemple : http://universite.fr/page?variable=valeur&Nom=*-*nom*-* ou uid=*-*id*-*"),
                          required=False)
    schema_ldap = TextLine(title=_(u"Schema de l'annuaire LDAP"),
                           description=_(u"exemple : supann ou eduPerson"),
                           default=_(u"supann"),
                           required=True)


class IJalonConfigDidacticielControlPanel(Interface):
    """
    fields for jalon Didacticiels control panel
    """

    didacticiel_plan_vide = Text(title=_(u"Didacticiel du plan interactif"),
                                 description=_(u"Didacticiel à afficher automatiquement lorsque le plan de cours est vide"),
                                 default=u'La vidéo ci-dessous vous expliquera comment construire votre premier plan :\n <iframe style="max-width:853px;height:480px;width:100%" src="http://www.youtube.com/embed/Z10V-BMXuec?rel=0" frameborder="0" allowfullscreen="allowfullscreen"></iframe>',
                                 required=False)


class IJalonConfigMailErreurControlPanel(Interface):
    """
    fields for jalon mail_erreur control panel
    """

    mail_erreur = TextLine(title=_(u"Adresse de réception des erreurs"),
                           description=_(u"Adresse mail de réception des error_log"),
                           required=True)
    activer_listeDiffusion = Bool(title=_(u"Activer les listes de diffusions"),
                                  description=_(u"Activer les listes de diffusions"),
                                  default=False,
                                  required=False)
    cible_listeDiffusion = Text(title=_(u"Éléments utilisant une liste de diffusions"),
                                description=_(u"valeur possible : etape, ue, uel, groupe"),
                                default=u"Liste des éléments utilisant les listes de diffusions, une valeur par ligne",
                                required=False)
    mail_listeDiffusion = TextLine(title=_(u"Adresse des listes de diffusion"),
                                   description=_(u"Adresse des listes de diffusion"),
                                   default=_(u"@etablissement.com"),
                                   required=False)


class IJalonConfigLienControlPanel(Interface):
    """
    fields for jalon Lien control panel
    """

    lien_sesame = TextLine(title=_(u"Absence de sésame"),
                           description=_(u"lien vers la page « Vous n'avez pas de sésame ? »"),
                           default=_(u"http://serveur.univ.fr/sesame"),
                           required=True)
    lien_contact = TextLine(title=_(u"Contact du service en charge"),
                            description=_(u"lien vers la page « Contacts »"),
                            default=_(u"http://serveur.univ.fr/contacts"),
                            required=True)
    lien_mention = TextLine(title=_(u"Mentions légales"),
                            description=_(u"lien vers la page « Mentions légales »"),
                            default=_(u"http://serveur.univ.fr/mentions"),
                            required=True)
    lien_credit = TextLine(title=_(u"Crédits"),
                           description=_(u"lien vers la page « Crédits »"),
                           default=_(u"https://sourcesup.renater.fr/projects/jalonos/"),
                           required=True)
    lien_bug = TextLine(title=_(u"Assistance / Helpdesk"),
                        description=_(u"lien vers la page « Signaler un bug »"),
                        default=_(u"https://sourcesup.renater.fr/forum/forum.php?forum_id=2232"),
                        required=True)
    lien_trombi = TextLine(title=_(u"Trombinoscope"),
                           description=_(u"lien vers le trombinoscope"),
                           default=_(u"http://trombi.univ.fr"),
                           required=True)
    categories_itunesu = Text(title=_(u"Catégories iTunesU"),
                              description=_(u"Listes des identifiants des cours et de leur catégorie iTunesU correspondante"),
                              default=u'id1|categorie123\nid2|categorie456',
                              required=False)


class IJalonConfigUnivControlPanel(Interface):
    """
    fields for jalon Université control panel
    """

    etablissement = TextLine(title=_(u"Établissement de la plateforme"),
                             default=_(u"Université de…"),
                             required=False)


class IJalonConfigurationControlPanel(IJalonConfigAnalyticsControlPanel,
                                      IJalonConfigLDAPControlPanel,
                                      IJalonConfigDidacticielControlPanel,
                                      IJalonConfigMailErreurControlPanel,
                                      IJalonConfigLienControlPanel,
                                      IJalonConfigUnivControlPanel,):
    """Combined schemas for the adapter lookup.
    """


class JalonConfigurationControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IJalonConfigurationControlPanel)

    def __init__(self, context):
        super(JalonConfigurationControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.jiProps = pprop.jalonconfiguration_properties

    # Analytics :
    def get_id_account(self):
        return self.jiProps.getProperty('id_account')

    def set_id_account(self, value):
        self.jiProps._updateProperty('id_account', value)

    id_account = property(get_id_account, set_id_account)

    def get_id_domain(self):
        return self.jiProps.getProperty('id_domain')

    def set_id_domain(self, value):
        self.jiProps._updateProperty('id_domain', value)

    id_domain = property(get_id_domain, set_id_domain)

    def get_chemin_encodage(self):
        return self.jiProps.getProperty('chemin_encodage')

    def set_chemin_encodage(self, value):
        self.jiProps._updateProperty('chemin_encodage', value)

    chemin_encodage = property(get_chemin_encodage, set_chemin_encodage)

    # LDAP :
    def get_activer_ldap(self):
        return self.jiProps.getProperty('activer_ldap')

    def set_activer_ldap(self, value):
        self.jiProps._updateProperty('activer_ldap', value)

    activer_ldap = property(get_activer_ldap, set_activer_ldap)

    def get_fiche_ldap(self):
        return self.jiProps.getProperty('fiche_ldap')

    def set_fiche_ldap(self, value):
        print value
        self.jiProps._updateProperty('fiche_ldap', value)

    fiche_ldap = property(get_fiche_ldap, set_fiche_ldap)

    def get_schema_ldap(self):
        return self.jiProps.getProperty('schema_ldap')

    def set_schema_ldap(self, value):
        print value
        self.jiProps._updateProperty('schema_ldap', value)

    schema_ldap = property(get_schema_ldap, set_schema_ldap)

    def getLoginLDAP(self):
        if self.get_schema_ldap() == "supann":
            return "supannAliasLogin"
        if self.get_schema_ldap() == "eduPerson":
            return "login"

    # Didacticiels :
    def get_didacticiel_plan_vide(self):
        valeur = self.jiProps.getProperty('didacticiel_plan_vide', None)
        return valeur

    def set_didacticiel_plan_vide(self, value):
        self.jiProps._updateProperty('didacticiel_plan_vide', value)

    didacticiel_plan_vide = property(get_didacticiel_plan_vide, set_didacticiel_plan_vide)

    #Gestion emails :
    def get_mail_erreur(self):
        valeur = self.jiProps.getProperty('mail_erreur', None)
        return valeur

    def set_mail_erreur(self, value):
        self.jiProps._updateProperty('mail_erreur', value)

    mail_erreur = property(get_mail_erreur, set_mail_erreur)

    def get_activer_listeDiffusion(self):
        valeur = self.jiProps.getProperty('activer_listeDiffusion', None)
        return valeur

    def set_activer_listeDiffusion(self, value):
        self.jiProps._updateProperty('activer_listeDiffusion', value)

    activer_listeDiffusion = property(get_activer_listeDiffusion, set_activer_listeDiffusion)

    def get_cible_listeDiffusion(self):
        valeur = self.jiProps.getProperty('cible_listeDiffusion', [])
        return valeur

    def set_cible_listeDiffusion(self, value):
        self.jiProps._updateProperty('cible_listeDiffusion', value)

    cible_listeDiffusion = property(get_cible_listeDiffusion, set_cible_listeDiffusion)

    def get_mail_listeDiffusion(self):
        valeur = self.jiProps.getProperty('mail_listeDiffusion', None)
        return valeur

    def set_mail_listeDiffusion(self, value):
        self.jiProps._updateProperty('mail_listeDiffusion', value)

    mail_listeDiffusion = property(get_mail_listeDiffusion, set_mail_listeDiffusion)

    def getListeDiffusion(self):
        return {"activerListeDiffusion": self.jiProps.getProperty('activer_listeDiffusion', None),
                "cibleListeDiffusion": self.jiProps.getProperty('cible_listeDiffusion', []),
                "mailListeDiffusion": self.jiProps.getProperty('mail_listeDiffusion', None)}

    # Liens :
    def get_lien_sesame(self):
        valeur = self.jiProps.getProperty('lien_sesame', None)
        return valeur

    def set_lien_sesame(self, value):
        self.jiProps._updateProperty('lien_sesame', value)

    lien_sesame = property(get_lien_sesame, set_lien_sesame)

    def get_lien_contact(self):
        valeur = self.jiProps.getProperty('lien_contact', None)
        return valeur

    def set_lien_contact(self, value):
        self.jiProps._updateProperty('lien_contact', value)

    lien_contact = property(get_lien_contact, set_lien_contact)

    def get_lien_mention(self):
        valeur = self.jiProps.getProperty('lien_mention', None)
        return valeur

    def set_lien_mention(self, value):
        self.jiProps._updateProperty('lien_mention', value)

    lien_mention = property(get_lien_mention, set_lien_mention)

    def get_lien_credit(self):
        valeur = self.jiProps.getProperty('lien_mention', None)
        return valeur

    def set_lien_credit(self, value):
        self.jiProps._updateProperty('lien_credit', value)

    lien_credit = property(get_lien_credit, set_lien_credit)

    def get_lien_bug(self):
        valeur = self.jiProps.getProperty('lien_bug', None)
        return valeur

    def set_lien_bug(self, value):
        self.jiProps._updateProperty('lien_bug', value)

    lien_bug = property(get_lien_bug, set_lien_bug)

    def get_lien_trombi(self):
        valeur = self.jiProps.getProperty('lien_trombi', None)
        return valeur

    def set_lien_trombi(self, value):
        self.jiProps._updateProperty('lien_trombi', value)

    lien_trombi = property(get_lien_trombi, set_lien_trombi)

    def get_categories_itunesu(self):
        valeur = self.jiProps.getProperty('categories_itunesu', None)
        return valeur

    def set_categories_itunesu(self, value):
        self.jiProps._updateProperty('categories_itunesu', value)

    categories_itunesu = property(get_categories_itunesu, set_categories_itunesu)

    #Établissement
    def get_etablissement(self):
        valeur = self.jiProps.getProperty('etablissement')
        return valeur

    def set_etablissement(self, value):
        self.jiProps._updateProperty('etablissement', value)

    etablissement = property(get_etablissement, set_etablissement)

    #accès à une valeur de la coonfiguration
    def getInfosConfiguration(self, info):
        dico = {"bug": self.jiProps.getProperty('lien_bug', None),
                "trombi": self.jiProps.getProperty('lien_trombi', None),
                "plan_vide": self.jiProps.getProperty('didacticiel_plan_vide', None),
                "etablissement": self.jiProps.getProperty('etablissement', None),
                "categories_itunesu": self.jiProps.getProperty('categories_itunesu', None)}
        if not info in dico:
            return ""
        return dico[info]

configAnalyticsset = FormFieldsets(IJalonConfigAnalyticsControlPanel)
configAnalyticsset.id = 'configAnalytics'
configAnalyticsset.label = _(u"Analytics")

configLDAPset = FormFieldsets(IJalonConfigLDAPControlPanel)
configLDAPset.id = 'configLDAP'
configLDAPset.label = _(u"LDAP")

configDidacticielset = FormFieldsets(IJalonConfigDidacticielControlPanel)
configDidacticielset.id = 'configDidacticiel'
configDidacticielset.label = _(u"Didacticiels")

configMailErreurset = FormFieldsets(IJalonConfigMailErreurControlPanel)
configMailErreurset.id = 'configMailErreur'
configMailErreurset.label = _(u"Gestion des emails")

configLienset = FormFieldsets(IJalonConfigLienControlPanel)
configLienset.id = 'configLien'
configLienset.label = _(u"Liens")

configUnivset = FormFieldsets(IJalonConfigUnivControlPanel)
configUnivset.id = 'configUniv'
configUnivset.label = _(u"Établissement")


class JalonConfigurationControlPanel(ControlPanelForm):

    label = _("Jalon Configuration")
    description = _("""Configuration de Jalon""")
    form_name = _("Jalon Configuration")
    form_fields = FormFieldsets(configAnalyticsset, configLDAPset, configDidacticielset, configMailErreurset, configLienset, configUnivset)
