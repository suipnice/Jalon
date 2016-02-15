# -*- coding: utf-8 -*-
"""Interface for WIMS plugin properties."""
from zope.interface import Interface
from zope import schema

from jalon.wims import contentMessageFactory as _


class IWimsLayout(Interface):

    """This interface defines the WIMS layout properties."""

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


class IWims(IWimsLayout,
            IWimsClasse,
            ):

    """This interface defines the Utility."""

    def getContentType(self, object=None, fieldname=None):
        """Get the content type of the field."""

    def getConfiguration(self, context=None, field=None, request=None):
        """Get the configuration based on the control panel settings and the field settings.

        request can be provided for translation purpose.

        """
