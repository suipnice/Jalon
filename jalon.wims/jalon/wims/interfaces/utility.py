# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema

from jalon.wims import contentMessageFactory as _


class IWimsLayout(Interface):
    """This interface defines the layout properties."""

    url_connexion = schema.TextLine(
        title=_(u"Url du fichier wims.cgi sur le serveur Wims."),
        description=_(u"exemple : http://domainname.com/wims/wims.cgi"),
        required=True)

    login = schema.TextLine(
        title=_(u"Identifiant de Jalon sur le serveur Wims."),
        description=_(u"exemple : adminJalon"),
        required=True)

    password = schema.Password(
        title=_(u"Mot de passe de Jalon sur le serveur Wims."),
        description=_(u"exemple : "),
        required=True)

    classe_locale = schema.TextLine(
        title=_(u"Identifiant local des classes."),
        description=_(u"exemple : ClassePlone"),
        required=True)

    nom_institution = schema.TextLine(
        title=_(u"Nom de l'institution."),
        description=_(u"exemple : Université de Nice Sophia Antipolis"),
        required=True)


class IWimsClasse(Interface):
    """This interface defines the classe properties."""

    donnees_classe = schema.Text(
        title=_(u"title_classe", default=u"Indiquer le schéma de la classe, plus d'informations dans le répertoire doc de jalon.wims"),
        description=_(u"description_classe", default=u"Exemple : "),
        required=False)
    donnees_superviseur = schema.Text(
        title=_(u"title_superviseur", default=u"Indiquer le schéma de la classe, plus d'informations dans le répertoire doc de jalon.wims"),
        description=_(u"description_superviseur", default=u"Exemple : "),
        required=False)
    donnees_exercice = schema.Text(
        title=_(u"title_exercice", default=u"Indiquer le schéma utilisé pour ajouter un exercice à une feuille ou un examen dans wims, plus d'informations dans le répertoire doc de jalon.wims"),
        description=_(u"description_exercice", default=u"Exemple : "),
        required=False)


class IWimsModele(Interface):
    """This interface defines the modele properties."""

    qcmsimple = schema.Text(title=_(u"title_qcmsimple", default=u"Schéma du modèle 'Question Simple' de createxo, id du modèle : qcmsimple"),
                    description=_(u"description_qcmsimple",
                                  default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                    required=False)

    equation = schema.Text(title=_(u"title_equation", default=u"Schéma du modèle 'Équation' de createxo, id du modèle : equation"),
                    description=_(u"description_equation",
                                  default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                    required=False)
    texteatrous = schema.Text(title=_(u"title_texteatrous", default=u"Schéma du modèle 'Texte à trous' de createxo, id du modèle : texteatrous"),
                    description=_(u"description_texteatrous",
                                  default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                    required=False)
    marqueruntexte = schema.Text(title=_(u"title_marqueruntexte", default=u"Schéma du modèle 'Marquer un texte' de createxo, id du modèle : marqueruntexte"),
                    description=_(u"description_marqueruntexte",
                                  default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                    required=False)
    marquerparpropriete = schema.Text(title=_(u"title_marquerparpropriete", default=u"Schéma du modèle 'Marquer par propriété' de createxo, id du modèle : marquerparpropriete"),
                    description=_(u"description_marquerparpropriete",
                                  default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                    required=False)
    questiontextuelletolerante = schema.Text(title=_(u"title_questiontextuelletolerante", default=u"Schéma du modèle 'Question textuelle tolérante' de createxo, id du modèle : questiontextuelletolerante"),
                    description=_(u"description_questiontextuelletolerante",
                                  default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                    required=False)
    taperlemotassocie = schema.Text(title=_(u"title_taperlemotassocie", default=u"Schéma du modèle 'Taper le mot associé' de createxo, id du modèle : taperlemotassocie"),
                    description=_(u"description_taperlemotassocie",
                                  default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                    required=False)
    reordonner = schema.Text(title=_(u"title_reordonner", default=u"Schéma du modèle 'Réordonner' de createxo, id du modèle : reordonner"),
                    description=_(u"description_reordonner",
                                  default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                    required=False)
    correspondance = schema.Text(title=_(u"title_correspondance", default=u"Schéma du modèle 'Correspondance' de createxo, id du modèle : correspondance"),
                     description=_(u"description_correspondance",
                                   default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                     required=False)
    classerparpropriete = schema.Text(title=_(u"title_classerparpropriete", default=u"Schéma du modèle 'Classer par propriété' de createxo, id du modèle : classerparpropriete"),
                          description=_(u"description_classerparpropriete",
                                        default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                          required=False)
    vraifauxmultiples = schema.Text(title=_(u"title_vraifauxmultiples", default=u"Schéma du modèle 'Vrai / Faux multiples' de createxo, id du modèle : vraifauxmultiples"),
                          description=_(u"description_vraifauxmultiples",
                                        default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                          required=False)
    texteatrousmultiples = schema.Text(title=_(u"title_texteatrousmultiples", default=u"Schéma du modèle 'Textes à trous multiples' de createxo, id du modèle : texteatrousmultiples"),
                           description=_(u"description_texteatrousmultiples",
                                         default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                           required=False)
    qcmsuite = schema.Text(title=_(u"title_qcmsuite", default=u"Schéma du modèle 'QCM Suite' de createxo, id du modèle : qcmsuite"),
                           description=_(u"description_qcmsuite",
                                         default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                           required=False)
    exercicelibre = schema.Text(title=_(u"title_exercicelibre", default=u"Schéma du modèle 'Exercice libre (mode brut)' de createxo, id du modèle : exercicelibre"),
                    description=_(u"description_exercicelibre",
                                  default=u"Les variables sont indiquées entre double $, exemple : $$variable$$"),
                    required=False)


class IWims(
    IWimsLayout,
    IWimsClasse,
    IWimsModele,
    ):
    """This interface defines the Utility."""

    def getContentType(self, object=None, fieldname=None):
        """Get the content type of the field."""

    def getConfiguration(self, context=None, field=None, request=None):
        """Get the configuration based on the control panel settings and the field settings.
        request can be provide for translation purpose."""
