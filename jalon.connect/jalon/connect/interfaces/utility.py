# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema

from jalon.connect import contentMessageFactory as _


class IConnectLayout(Interface):
    """This interface defines the layout properties."""

    url_connexion = schema.TextLine(title=_(u"Url de la librairie xml-rpc sur serveur Adobe Connect"),
                                    description=_(u"exemple : http://domainname.com/api/xml"),
                                    required=True)
    login = schema.TextLine(title=_(u"Nom d'utilisateur du compte administrateur du serveur Adobe Connect"),
                            description=_(u"exemple : admin"),
                            required=True)
    password = schema.Password(title=_(u"Mot de passe du compte administrateur Adobe Connect"),
                               description=_(u"exemple : admin"),
                               required=True)
    version = schema.TextLine(title=_(u"Version d'Adobe Connect"),
                              description=_(u"exemple : 8"),
                              required=True)
    etablissement = schema.TextLine(title=_(u"Etablissement des utilisateurs Adobe Connect"),
                                    description=_(u"exemple : UNS"),
                                    required=True)
    num_serveur = schema.TextLine(title=_(u"Numéro du serveur"),
                                  description=_(u"A ne changer que si vous connectez un nouveau serveur connect vierge de tout utilisateur."),
                                  required=True)


class IConnectModele(Interface):
    """This interface defines the layout properties."""
    dossiers = schema.Text(title=_(u"title_dossiers", default=u"Indiquer l'id d'un dossier et le modèle de réunion qui lui sera associé. (le 'sco-id' d'une reunion Adobe Connect)"),
                           description=_(u"description_dossiers", default=u"Exemple : Webconference:123456"),
                           required=False)


class IConnect(
    IConnectLayout,
    IConnectModele,
    ):
    """This interface defines the Utility."""

    def getContentType(self, object=None, fieldname=None):
        """Get the content type of the field."""

    def getConfiguration(self, context=None, field=None, request=None):
        """Get the configuration based on the control panel settings and the field settings.
        request can be provide for translation purpose."""
