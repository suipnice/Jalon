# -*- coding: utf-8 -*-
import logging

from zope.component import getMultiAdapter

from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

_marker = []
logger = logging.getLogger(__name__)

class JalonSection(GlobalSectionsViewlet):
    index = ViewPageTemplateFile('../viewlets/sections.pt')

    def __init__(self, *args, **kwargs):
        super(JalonSection, self).__init__(*args, **kwargs)

    def isAnonyme(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        if portal_state.anonymous():
            return True
        return False

    def getMenu(self, member_id, is_personnel, is_manager, lang):
        #logger.debug("getMenu")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return {"left_menu" : self.getLeftMenu(member_id, is_personnel, is_manager, portal_state),
                "right_menu": self.getRightMenu(portal_state, member_id, lang)}

    def getLeftMenu(self, member_id, is_personnel, is_manager, portal_state=None):
        if not portal_state:
            portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')

        portal_url = portal_state.portal_url()
        jalon_properties = getToolByName(self, "portal_jalon_properties")
        jalon_categories = dict(jalon_properties.getCategorie())
        liste_id_categorie = jalon_categories.keys()
        liste_id_categorie.sort()

        class_cours = ""
        sub_menu_mes_cours = []
        if not is_personnel:
            for id_categorie in liste_id_categorie:
                sub_menu_mes_cours.append({"id"   : "cat%s" % id_categorie,
                                           "icone": "fa fa-book",
                                           "title": jalon_categories[id_categorie]['title'],
                                           "href" : "%s/cours/%s?categorie=%s" % (portal_url, member_id, id_categorie)
                                          })
            if sub_menu_mes_cours:
                class_cours = "has-dropdown not-click"

        return [{"id"      : "mon_espace",
                 "class"   : "has-dropdown not-click",
                 "icone"   : "fa fa-home",
                 "title"   : _(u"Mon espace"),
                 "href"    : portal_url,
                 "sub_menu": [{"id"   : "fichiers",
                               "icone": "fa fa-files-o",
                               "title": _(u"Fichiers"),
                               "href" : "%s/Members/%s/Fichiers" % (portal_url, member_id)},
                              {"id"   : "sonorisation",
                               "icone": "fa fa-microphone",
                               "title": _(u"Présentations sonorisées"),
                               "href" : "%s/Members/%s/Sonorisation" % (portal_url, member_id)},
                              {"id"   : "wims",
                               "icone": "fa fa-random",
                               "title": _(u"Exercices Wims"),
                               "href" : "%s/Members/%s/Wims" % (portal_url, member_id)},
                              {"id"   : "liens",
                               "icone": "fa fa-external-link",
                               "title": _(u"Ressources externes"),
                               "href" : "%s/Members/%s/Externes" % (portal_url, member_id)},
                              {"id"   : "glossaire",
                               "icone": "fa fa-font",
                               "title": _(u"Termes de glossaire"),
                               "href" : "%s/Members/%s/Glossaire" % (portal_url, member_id)},
                              {"id"   : "connect",
                               "icone": "fa fa-headphones",
                               "title": _(u"Webconférences"),
                               "href" : "%s/Members/%s/Webconference" % (portal_url, member_id)}
                             ],
                 "is_visible": is_personnel or is_manager},
                {"id"      : "mes-cours",
                 "class"   : class_cours,
                 "icone"   : "fa fa-university",
                 "title"   :  _(u"Mes cours"),
                 "href"    :   "%s/cours/%s" % (portal_url, member_id),
                 "sub_menu": sub_menu_mes_cours,
                 "is_visible": True},
                {"id"      : "mes_etudiants",
                 "class"   : "",
                 "icone"   : "fa fa-users",
                 "title"   : _(u"Mes étudiants"),
                 "href"    : "%s/etudiants" % portal_url,
                 "sub_menu": [],
                 "is_visible": is_personnel or is_manager},
                {"id"      : "configuration",
                 "class"   : "has-dropdown not-click",
                 "icone"   : "fa fa-cogs",
                 "title"   : _(u"Configuration"),
                 "href"    : "%s/portal_jalon_properties/@@jalon-configuration" % portal_url,
                 "sub_menu": [{"id"   : "gestion_connexion",
                               "icone": "fa fa-key",
                               "title": _(u"Connexion à Jalon"),
                               "href" : "%s/portal_jalon_properties/gestion_connexion" % portal_url},
                              {"id"   : "gestion_mon_espace",
                               "icone": "fa fa-home",
                               "title": _(u"Gestion \"Mon Espace\""),
                               "href" : "%s/portal_jalon_properties/gestion_mon_espace" % portal_url},
                              {"id"   : "gestion_mes_cours",
                               "icone": "fa fa-university",
                               "title": _(u"Gestion des cours"),
                               "href" : "%s/portal_jalon_properties/gestion_mes_cours" % portal_url},
                              {"id"   : "gestion_infos",
                               "icone": "fa fa-external-link-square",
                               "title": _(u"Liens d'informations"),
                               "href" : "%s/portal_jalon_properties/gestion_infos" % portal_url},
                              {"id"   : "gestion_didacticiels",
                               "icone": "fa fa-life-ring",
                               "title": _(u"Didacticiels"),
                               "href" : "%s/portal_jalon_properties/gestion_didacticiels" % portal_url},
                              {"id"   : "gestion_messages",
                               "icone": "fa fa-newspaper-o",
                               "title": _(u"Diffusion de messages"),
                               "href" : "%s/portal_jalon_properties/gestion_messages" % portal_url},
                              {"id"   : "gestion_email",
                               "icone": "fa fa-envelope-o",
                               "title": _(u"Courriels"),
                               "href" : "%s/portal_jalon_properties/gestion_email" % portal_url},
                              {"id"   : "gestion_donnees_utilisateurs",
                               "icone": "fa fa-users",
                               "title": _(u"Données utilisateurs"),
                               "href" : "%s/portal_jalon_properties/gestion_donnees_utilisateurs" % portal_url},
                              {"id"   : "gestion_ga",
                               "icone": "fa fa-line-chart",
                               "title": _(u"Google Analytics"),
                               "href" : "%s/portal_jalon_properties/gestion_ga" % portal_url},
                              {"id"   : "gestion_maintenance",
                               "icone": "fa fa-fire-extinguisher",
                               "title": _(u"Maintenance"),
                               "href" : "%s/portal_jalon_properties/gestion_maintenance" % portal_url}
                             ],
                 "is_visible": is_manager},
               ]

    def getRightMenu(self, portal_state=None, member_id=None, lang="fr"):
        #"%s/@@personal-information" % portal_state.portal_url()
        if not portal_state:
            portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        """
        {"id"      : "profil",
                 "class"   : "",
                 "icone"   : "fa fa-cog fa-fw",
                 "title"   : _(u"Mon profil"),
                 "href"    : jalon_utils.getFicheAnnuaire({"id" : member_id}),
                 "sub_menu": []},
                {"id"      : "language",
                 "class"   : "has-dropdown not-click",
                 "icone"   : "fa fa-flag fa-fw",
                 "title"   : _(u"Langues"),
                 "href"    : "",
                 "sub_menu": [{"id"   : "en",
                               "class": 'active' if lang == 'en' else '',
                               "title": _(u"English"),
                               "href" : "%s?set_language=en" % self.context.absolute_url()},
                              {"id"   : "fr",
                               "class": 'active' if lang == 'fr' else '',
                               "title": _(u"Français"),
                               "href" : "%s?set_language=fr" % self.context.absolute_url()},
                              {"id"   : "it",
                               "class": 'active' if lang == 'it' else '',
                               "title": _(u"Italiano"),
                               "href" : "%s?set_language=it" % self.context.absolute_url()}]
                },
        """
        return [{"id"      : "deconnexion",
                 "class"   : "",
                 "icone"   : "fa fa-sign-out fa-fw",
                 "title"   : _(u"Deconnexion"),
                 "href"    : "%s/logout" % portal_state.portal_url(),
                 "sub_menu": []}
               ]

    def getSite(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return {"name": portal_state.portal_title(),
                "url":  portal_state.portal_url()}
