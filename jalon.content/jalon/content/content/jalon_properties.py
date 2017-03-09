# -*- coding: utf-8 -*-
""" Jalon Properties. """

from zope.interface import implements

from OFS.SimpleItem import SimpleItem
from persistent.dict import PersistentDict
from Products.CMFCore.utils import getToolByName

from twython import Twython, TwythonError

from ..browser.interfaces import IJalonProperties
from jalon.content import contentMessageFactory as _
from jalon.content.content import jalon_utils

from DateTime import DateTime

import json
import copy

# Messages de debug :
from logging import getLogger
LOG = getLogger('[JalonProperties]')


class JalonProperties(SimpleItem):

    """ Jalon Properties Class. """

    implements(IJalonProperties)
    #categories de cours
    _categories = {}

    #gestion podcasts
    _activerPodcasts = False
    _uploadPodcasts = ""
    _dnsPodcasts = ""
    _dicoUsersPodcast = {}
    _dicoLibCatITunesU = {"102":    "Art & Architecture",
                          "102100": "Architecture",
                          "102102": "Art History",
                          "102109": "Culinary Arts",
                          "102103": "Dance",
                          "102105": "Design",
                          "102111": "Fashion",
                          "102104": "Film",
                          "102106": "Interior Design",
                          "102112": "Media Arts",
                          "102107": "Music",
                          "102113": "Photography",
                          "102108": "Theater",
                          "102110": "Visual Art",
                          "100":    "Business",
                          "100100": "Economics",
                          "100107": "Entrepreneurship",
                          "100101": "Finance",
                          "100102": "Hospitality",
                          "100103": "Management",
                          "100104": "Marketing",
                          "100105": "Personal Finance",
                          "100106": "Real Estate",
                          "113":    "Communications & Media",
                          "113101": "Broadcasting",
                          "113102": "Digital Media",
                          "113103": "Journalism",
                          "113104": "Photojournalism",
                          "113105": "Print",
                          "113106": "Speech",
                          "113107": "Writing",
                          "101":    "Engineering",
                          "101100": "Chemical & Petroleum Engineering",
                          "101101": "Civil Engineering",
                          "101102": "Computer Science",
                          "101103": "Electrical Engineering",
                          "101104": "Environmental Engineering",
                          "101105": "Mechanical Engineering",
                          "103":    "Health & Medicine",
                          "103100": "Anatomy & Physiology",
                          "103101": "Behavioral Science",
                          "103102": "Dentistry",
                          "103103": "Diet & Nutrition",
                          "103104": "Emergency Medicine",
                          "103105": "Genetics",
                          "103106": "Gerontology",
                          "103112": "Global Health",
                          "103107": "Health & Exercise Science",
                          "103108": "Immunology",
                          "103109": "Neuroscience",
                          "103114": "Nursing",
                          "103110": "Pharmacology & Toxicology",
                          "103111": "Psychiatry",
                          "103113": "Radiology",
                          "104":    "History",
                          "104104": "African History",
                          "104100": "Ancient History",
                          "104105": "Asia-Pacific History",
                          "104106": "European History",
                          "104101": "Medieval History",
                          "104107": "Middle Eastern History",
                          "104102": "Military History",
                          "104103": "Modern History",
                          "104108": "North American History",
                          "104109": "South American History",
                          "106":    "Language",
                          "106100": "African Languages",
                          "106101": "Ancient Languages",
                          "106114": "Arabic",
                          "106113": "Chinese",
                          "106104": "English",
                          "106106": "French",
                          "106107": "German",
                          "106115": "Hebrew",
                          "106116": "Hindi",
                          "106117": "Indigenous Languages",
                          "106108": "Italian",
                          "106118": "Japanese",
                          "106119": "Korean",
                          "106109": "Linguistics",
                          "106120": "Other Languages",
                          "106121": "Portuguese",
                          "106122": "Russian",
                          "106111": "Spanish",
                          "106112": "Speech Pathology",
                          "116":    "Law & Politics",
                          "116100": "Foreign Policy & International Relations",
                          "116101": "Law",
                          "116102": "Local Governments",
                          "116103": "National Governments",
                          "116104": "Political Science",
                          "116105": "Public Administration",
                          "116106": "World Affairs",
                          "107":    "Literature",
                          "107100": "Anthologies",
                          "107101": "Biography",
                          "107102": "Classics",
                          "107106": "Comparative Literature",
                          "107104": "Fiction",
                          "107103": "Literary Criticism",
                          "107105": "Poetry",
                          "108":    "Mathematics",
                          "108100": "Advanced Mathematics",
                          "108101": "Algebra",
                          "108102": "Arithmetic",
                          "108103": "Calculus",
                          "108104": "Geometry",
                          "108105": "Statistics",
                          "114":    "Philosophy",
                          "114100": "Aesthetics",
                          "114101": "Epistemology",
                          "114102": "Ethics",
                          "114105": "Logic",
                          "114103": "Metaphysics",
                          "114106": "Philosophy of Language",
                          "114107": "Philosophy of Religion",
                          "114104": "Political Philosophy",
                          "110":    "Psychology & Social Science",
                          "110107": "Anthropology",
                          "110106": "Archaeology",
                          "110103": "Psychology",
                          "110104": "Social Welfare",
                          "110105": "Sociology",
                          "115":    "Religion & Spirituality",
                          "115100": "Buddhism",
                          "115101": "Christianity",
                          "115102": "Comparative Religion",
                          "115103": "Hinduism",
                          "115104": "Islam",
                          "115105": "Judaism",
                          "115106": "Other Religions",
                          "115107": "Spirituality",
                          "109":    "Science",
                          "109100": "Agriculture",
                          "109101": "Astronomy",
                          "109102": "Atmosphere",
                          "109103": "Biology",
                          "109104": "Chemistry",
                          "109105": "Ecology",
                          "109109": "Environment",
                          "109106": "Geography",
                          "109107": "Geology",
                          "109108": "Physics",
                          "111":    "Society",
                          "111107": "African Studies",
                          "111108": "American Studies",
                          "111101": "Asia Pacific Studies",
                          "111109": "Cross-cultural Studies",
                          "111102": "European Studies",
                          "111110": "Immigration & Emigration",
                          "111103": "Indigenous Studies",
                          "111104": "Latin & Caribbean Studies",
                          "111105": "Middle Eastern Studies",
                          "111111": "Race & Ethnicity Studies",
                          "111112": "Sexuality Studies",
                          "111106": "Women's Studies",
                          "112":    "Teaching & Learning",
                          "112100": "Curriculum & Teaching",
                          "112101": "Educational Leadership",
                          "112106": "Educational Technology",
                          "112102": "Family & Childcare",
                          "112107": "Information/Library Science",
                          "112103": "Learning Resources",
                          "112104": "Psychology & Research",
                          "112105": "Special Education"}
    _catITunesU = {"102":  ["102100", "102102", "102109", "102103", "102105", "102111", "102104", "102106", "102112", "102107", "102113", "102108", "102110"],
                   "100": ["100100", "100107", "101101", "100102", "100103", "100104", "100105", "100106"],
                   "113": ["113101", "113102", "113103", "113104", "113105", "113106", "113107"],
                   "101": ["101100", "101101", "101102", "101103", "101104", "101105"],
                   "103": ["103100", "103101", "103102", "103103", "103104", "103105", "103106", "103112", "103107", "103108", "103109", "103114", "103110", "103111", "103113"],
                   "104": ["104104", "104100", "104105", "104106", "104101", "104107", "104102", "104103", "104108", "104109"],
                   "106": ["106100", "106101", "106114", "106113", "106104", "106106", "106107", "106115", "106116", "106117", "106108", "106118", "106119", "106109", "106120", "106121", "106122", "106111", "106112"],
                   "116": ["116100", "116101", "116102", "116103", "116104", "116105", "116106"],
                   "107": ["107100", "107101", "107102", "107106", "107104", "107103", "107105"],
                   "108": ["108100", "108101", "108102", "108103", "108104", "108105"],
                   "114": ["114100", "114101", "114102", "114105", "114103", "114106", "114107", "114104"],
                   "110": ["110107", "110106", "110103", "110104", "110105"],
                   "115": ["115100", "115101", "115102", "115103", "115104", "115105", "115106", "115107"],
                   "109": ["109100", "109101", "109102", "109103", "109104", "109105", "109109", "109106", "109107", "109108"],
                   "111": ["111107", "111108", "111101", "111109", "111102", "111110", "111103", "111104", "111105", "111111", "111112", "111106"],
                   "112": ["112100", "112101", "112106", "112102", "112107", "112103", "112104", "112105"]}
    _ordreCatiTunesU = ["102", "100", "113", "101", "103", "104", "106", "116", "107", "108", "114", "110", "115", "109", "111", "112"]

    # Gestion de la connexion
    _activer_cas = 0
    _serviceUrl = ""
    _casServerUrlPrefix = ""
    _activer_creationcompte = 0

    # Gestion du bloc informations
    _activer_etablissement = 1
    _etablissement = "Université Nice Sophia antipolis (UNS)"
    _lien_etablissement = "http://unice.fr"
    _activer_lien_sesame = 1
    _lien_sesame = "http://ent.unice.fr"
    _activer_lien_contact = 1
    _lien_contact = "http://unice.fr/contact-info"
    _activer_lien_mention = 1
    _lien_mention = "http://unice.fr/mentions-legales"
    _activer_lien_credit = 1
    _lien_credit = "http://unice.fr/mentions-legales"

    # Gestion du bloc "Didacticiels"
    _activer_aide = 1
    _lien_aide = "http://jalon.unice.fr/public/xau995"
    _activer_aide_plan = 1
    _lien_aide_plan = '<div class="flex-video"><iframe src="//www.youtube.com/embed/Z10V-BMXuec?list=PLV8G_tL0jD2LmZ79s0D-4EkeCVgQTvWfo" frameborder="0" allowfullscreen></iframe></div>\n<p>Cette vidéo disparaîtra automatiquement quand vous aurez ajouté des éléments à votre cours.</p>'
    _activer_guide_anti_spam = "1"
    _message_guide_anti_spam = """<h3>Pour être sûr(e) de recevoir les courriels de vos enseignants</h3>
<p>Si vous avez fait le choix de rediriger votre courriel @etu.unice.fr vers une autre adresse, vous devez effectuer les réglages permettant d'autoriser le serveur jalon.unice.fr et l'expéditeur noreply@jalon.unice.fr à vous envoyer des courriels et à ne pas les considérer comme du spam.</p>
<dl>
    <dt>Google Mail :</dt>
    <dd>ajoutez noreply@jalon.unice.fr dans vos contacts gmail afin que les messages de cet expéditeur ne soient plus considérés comme du spam.</dd>
    <dt>Hotmail :</dt>
    <dd>rendez-vous dans la rubrique filtre et ajoutez @jalon.unice.fr dans la liste des serveurs expéditeurs autorisés.</dd>
    <dt>Autres :</dt>
    <dd>consultez l'aide de votre webmail à la rubrique spam…</dd>
</dl>"""

    # Gestion du bloc "Message"
    _activer_message_general = 0
    _message_general = ""
    _activer_bie = 0
    _bie_message = ""
    _activer_message_enseignant = 0
    _message_enseignant = ""

    # Gestion du bloc "Courriels"
    _activer_erreur = 0
    _activer_email_erreur = 0
    _adresse_email_erreur = ""
    _activer_liste_diffusion = 0
    _type_diffusion = "etape,ue,uel,groupe"
    _format_diffusion = ""

    # Gestion des bulles de "Mon Espace"
    _activer_fichiers = 1
    _activer_presentations_sonorisees = 0
    _activer_exercices_wims = 0
    _activer_liens = 1
    _activer_liens_catalogue_bu = 0
    _activer_tags_catalogue_bu = 0
    _activer_lille1pod = 0
    _activer_termes_glossaire = 1
    _activer_webconferences = 0
    _activer_lien_intracursus = 0
    _lien_intracursus = "http://intracursus.unice.fr"
    _activer_lien_assistance = 1
    _lien_assitance = "https://sourcesup.renater.fr/forum/forum.php?thread_id=3460&forum_id=2232&group_id=832"
    _activer_video = 0
    _url_video = ""
    _activer_vod = 0

    # Gestion du bloc "Réaseaux sociaux"
    _COMPTE_TWITTER = ""
    _APP_KEY = ""
    _APP_SECRET = ""
    _OAUTH_TOKEN = ""
    _OAUTH_TOKEN_SECRET = ""

    # Gestion de la récupération des données utilisateurs
    _activer_ldap = 0
    _base_ldap = ""
    _schema_ldap = ""
    _fiche_ldap = ""
    _activer_trombinoscope = 0
    _activer_stockage_photo = 0
    _lien_trombinoscope = "http://tice-trombino.unice.fr"

    # Gestion statistique Google Analytics
    _activer_ga = 0
    _ga_id_account = ""
    _ga_id_domain = ""
    _ga_cryptage = ""

    # Gestion de la partie de maintenance
    _annoncer_maintenance = ""
    _activer_maintenance = ""
    _date_debut_maintenance = ""
    _date_fin_maintenance = ""
    _annoncer_vider_cache = ""
    _url_news_maintenance = ""

    def __init__(self, *args, **kwargs):
        super(JalonProperties, self).__init__(*args, **kwargs)
        self._categories = {1: {"title": _(u"Mes formations"), "users": ['all']},
                            2: {"title": _(u"Inscription par mot de passe"), "users": ['all']}}

    #-------------#
    # utilitaires #
    #-------------#
    def getJalonProperty(self, key):
        return getattr(self, "_%s" % key)

    def test(self, condition, valeurVrai, valeurFaux):
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

    def getShortText(self, text, limit=75):
        return jalon_utils.getShortText(text, limit)

    def getJalonPhoto(self, user_id):
        if self._activer_stockage_photo:
            portal = self.portal_url.getPortalObject()
            return "%s/etudiants/%s" % (portal.absolute_url(), user_id)
        else:
            return "%s/%s.jpg" % (self._lien_trombinoscope, user_id)

    def getTopBarMenuLeft(self, user_role):
        # LOG.info("----- getTopBar -----")
        menu_left = []
        is_personnel = user_role in ["Personnel", "Secretaire", "Manager"]

        sub_menu_mes_cours = []
        sub_menu_mes_cours_class = ""
        if user_role in ["Etudiant", "EtudiantJalon"]:
            jalon_categories = dict(self.getCategorie())
            liste_id_categorie = jalon_categories.keys()
            liste_id_categorie.sort()

            for id_categorie in liste_id_categorie:
                sub_menu_mes_cours.append({"id":      "cat%s" % id_categorie,
                                           "icon":    "fa fa-book",
                                           "title":   jalon_categories[id_categorie]['title'],
                                           "link":    "mes_cours?categorie=%s" % id_categorie})
            if sub_menu_mes_cours:
                sub_menu_mes_cours_class = "has-dropdown not-click"

        menu_left.append({"id":       "mes-cours",
                          "class":    sub_menu_mes_cours_class,
                          "icon":     "fa fa-university",
                          "title":    _(u"Mes cours"),
                          "link":     "mes_cours",
                          "sub_menu": sub_menu_mes_cours})

        menu_my_space = None
        if is_personnel:
            menu_my_space = {"id":        "mes_ressources",
                             "class":     "has-dropdown not-click",
                             "icon":      "fa fa-folder-open",
                             "title":     _(u"Mes ressources"),
                             "link":      "mes_ressources",
                             "sub_menu":  []}

            for sub_menu in self.getGridMonEspaceNew():
                if sub_menu["activated"]:
                    menu_my_space["sub_menu"].append(sub_menu)
            menu_left.append(menu_my_space)

            menu_left.append({"id":       "mes_etudiants",
                              "class":    "",
                              "icon":     "fa fa-users",
                              "title":    _(u"Mes étudiants"),
                              "link":     "mes_etudiants",
                              "sub_menu": []})

            menu_left.append({"id":       "tools",
                              "class":    "",
                              "icon":     "fa fa-wrench",
                              "title":    _(u"Outils"),
                              "link":     "tools_page",
                              "sub_menu": []})

        if user_role == "Manager":
            menu_left.append({"id":       "gestion_pedagogique",
                              "class":    "has-dropdown not-click",
                              "icon":    "fa fa-database",
                              "title":    _(u"Gestion pédagogique"),
                              "link":     "portal_jalon_bdd/@@jalon-bdd",
                              "sub_menu": [{"id":    "gestion_bdd",
                                            "icon":  "fa fa-list",
                                            "title": _(u"Offre de formations"),
                                            "link":  "portal_jalon_bdd/@@jalon-bdd?gestion=gestion_bdd"},
                                           {"id":    "gestion_utilisateurs",
                                            "icon":  "fa fa-users",
                                            "title": _(u"Utilsateurs"),
                                            "link":  "portal_jalon_bdd/@@jalon-bdd?gestion=gestion_utilisateurs"},
                                           {"id":    "gestion_connexion_bdd",
                                            "icon": "fa fa-key",
                                            "title": _(u"Propriétés"),
                                            "link":  "portal_jalon_bdd/@@jalon-bdd?gestion=gestion_connexion_bdd"}]})

            menu_left.append({"id":       "configuration",
                              "class":    "has-dropdown not-click",
                              "icon":     "fa fa-cogs",
                              "title":    _(u"Configuration"),
                              "link":     "portal_jalon_properties/@@jalon_properties",
                              "sub_menu": [{"id":    "gestion_connexion",
                                            "icon":  "fa fa-key",
                                            "title": _(u"Connexion à Jalon"),
                                            "link":  "portal_jalon_properties/gestion_connexion"},
                                           {"id":    "gestion_mes_ressources",
                                            "icon":  "fa fa-folder-open",
                                            "title": _(u"Gestion \"Mes ressources\""),
                                            "link":  "portal_jalon_properties/gestion_mes_ressources"},
                                           {"id":    "gestion_mes_cours",
                                            "icon":  "fa fa-university",
                                            "title": _(u"Gestion des cours"),
                                            "link":  "portal_jalon_properties/gestion_mes_cours"},
                                           {"id":    "gestion_infos",
                                            "icon":  "fa fa-external-link-square",
                                            "title": _(u"Liens d'informations"),
                                            "link":  "portal_jalon_properties/gestion_infos"},
                                           {"id":    "gestion_didacticiels",
                                            "icon":  "fa fa-life-ring",
                                            "title": _(u"Didacticiels"),
                                            "link":  "portal_jalon_properties/gestion_didacticiels"},
                                           {"id":    "gestion_messages",
                                            "icon":  "fa fa-bullhorn",
                                            "title": _(u"Diffusion de messages"),
                                            "link":  "portal_jalon_properties/gestion_messages"},
                                           {"id":    "gestion_email",
                                            "icon":  "fa fa-envelope-o",
                                            "title": _(u"Courriels"),
                                            "link":  "portal_jalon_properties/gestion_email"},
                                           {"id":     "gestion_donnees_utilisateurs",
                                            "icon":  "fa fa-users",
                                            "title": _(u"Données utilisateurs"),
                                            "link":  "portal_jalon_properties/gestion_donnees_utilisateurs"},
                                           {"id":     "gestion_ga",
                                            "icon":  "fa fa-line-chart",
                                            "title": _(u"Google Analytics"),
                                            "link":  "portal_jalon_properties/gestion_ga"},
                                           {"id":     "gestion_maintenance",
                                            "icon": "fa fa-umbrella",
                                            "title": _(u"Maintenance"),
                                            "link":  "portal_jalon_properties/gestion_maintenance"}]})

        if user_role == "Secretaire":
            menu_left.append({"id":       "gestion_pedagogique",
                              "class":    "",
                              "icon":     "fa fa-database",
                              "title":    _(u"Gestion pédagogique"),
                              "link":     "/portal_jalon_bdd/gestion_utilisateurs",
                              "sub_menu": []})

        return menu_left

    def getMonEspace(self):
        # LOG.info("----- getMonEspace -----")
        return {"site":        self.aq_parent.Title(),
                "grid":        self.getGridMonEspaceNew(),
                "maintenance": self.getPropertiesMaintenance(),
                "vidercache":  self.getJalonProperty("annoncer_vider_cache"),
                "messages":    self.getPropertiesMessages()}

    def generatePageMonEspace(self, request):
        # LOG.info("----- generatePageMonEspace -----")
        macro_mes_ressources_grid_generate = ["<metal:macro define-macro=\"mes_ressources_grid\">"]
        macro_mes_ressources_grid_generate.append(self.restrictedTraverse("portal_jalon_properties/macro_mes_ressources_grid_base")())
        macro_mes_ressources_grid_generate.append("</metal:macro>")
        self.restrictedTraverse("mes_ressources/macro_mes_ressources_grid").pt_edit("\n".join(macro_mes_ressources_grid_generate), "text/html", "utf-8")

        top_bar_base = self.restrictedTraverse("portal_jalon_properties/top_bar_base").PrincipiaSearchSource()

        request.set("left_menu", self.getTopBarMenuLeft('Manager'))
        top_bar_menu_left_base = self.restrictedTraverse("portal_jalon_properties/top_bar_menu_left_base")(REQUEST=request)
        top_bar_manager = top_bar_base.replace("*****left_menu*****", top_bar_menu_left_base)
        self.restrictedTraverse("top_bar/top_bar_manager").pt_edit(top_bar_manager, "text/html", "utf-8")

        request.set("left_menu", self.getTopBarMenuLeft('Personnel'))
        top_bar_menu_left_base = self.restrictedTraverse("portal_jalon_properties/top_bar_menu_left_base")(REQUEST=request)
        top_bar_personnel = top_bar_base.replace("*****left_menu*****", top_bar_menu_left_base)
        self.restrictedTraverse("top_bar/top_bar_personnel").pt_edit(top_bar_personnel, "text/html", "utf-8")

        request.set("left_menu", self.getTopBarMenuLeft('Secretaire'))
        top_bar_menu_left_base = self.restrictedTraverse("portal_jalon_properties/top_bar_menu_left_base")(REQUEST=request)
        top_bar_secretaire = top_bar_base.replace("*****left_menu*****", top_bar_menu_left_base)
        self.restrictedTraverse("top_bar/top_bar_secretaire").pt_edit(top_bar_secretaire, "text/html", "utf-8")

        request.set("left_menu", self.getTopBarMenuLeft('Etudiant'))
        top_bar_menu_left_base = self.restrictedTraverse("portal_jalon_properties/top_bar_menu_left_base")(REQUEST=request)
        top_bar_etudiant = top_bar_base.replace("*****left_menu*****", top_bar_menu_left_base)
        self.restrictedTraverse("top_bar/top_bar_etudiant").pt_edit(top_bar_etudiant, "text/html", "utf-8")
        self.restrictedTraverse("top_bar/top_bar_etudiantjalon").pt_edit(top_bar_etudiant, "text/html", "utf-8")

    #------------------------#
    # Fonctions de connexion #
    #------------------------#
    def getPropertiesConnexion(self, key=None):
        if key:
            return getattr(self, "_%s" % key)
        else:
            return {"activer_cas":            self._activer_cas,
                    "serviceUrl":             self._serviceUrl,
                    "casServerUrlPrefix":     self._casServerUrlPrefix,
                    "activer_creationcompte": self._activer_creationcompte}

    def setPropertiesConnexion(self, form):
        for key in form.keys():
            val = form[key]
            if key == "activer_cas":
                val = int(val)
            if key == "activer_creationcompte":
                val = int(val)
            setattr(self, "_%s" % key, val)

    #--------------------------------#
    # Fonctions du bloc Informations #
    #--------------------------------#
    def getPropertiesInfos(self, key=None):
        if key:
            return getattr(self, "_%s" % key)
        else:
            return {"activer_etablissement":   self._activer_etablissement,
                    "etablissement":           self._etablissement,
                    "lien_etablissement":      self._lien_etablissement,
                    "activer_lien_sesame":     self._activer_lien_sesame,
                    "lien_sesame":             self._lien_sesame,
                    "activer_lien_contact":    self._activer_lien_contact,
                    "lien_contact":            self._lien_contact,
                    "activer_lien_mention":    self._activer_lien_mention,
                    "lien_mention":            self._lien_mention,
                    "activer_lien_credit":     self._activer_lien_credit,
                    "lien_credit":             self._lien_credit, }

    def setPropertiesInfos(self, form):
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "_%s" % key, val)

    def getLienContact(self):
        """ Fournit un lien pour contacter l'administrateur du site."""
        portal = self.portal_url.getPortalObject()
        portal_title = portal.Title()
        if self._activer_lien_contact:
            lien_contact = self._lien_contact
        else:
            if self._activer_email_erreur:
                lien_contact = "mailto:%s" % self._adresse_email_erreur
            else:
                lien_contact = "mailto:%s" % portal.getProperty("email_from_address")
        return {"portal_title": portal_title,
                "contact_link":  lien_contact}

    #--------------------------------#
    # Fonctions du bloc Didacticiels #
    #--------------------------------#
    def getPropertiesDidacticiels(self, key=None):
        if key:
            return getattr(self, "_%s" % key)
        else:
            return {"activer_aide":            self._activer_aide,
                    "lien_aide":               self._lien_aide,
                    "activer_aide_plan":       self._activer_aide_plan,
                    "lien_aide_plan":          self._lien_aide_plan,
                    "activer_guide_anti_spam": self._activer_guide_anti_spam,
                    "message_guide_anti_spam": self._message_guide_anti_spam}

    def setPropertiesDidacticiels(self, form):
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "_%s" % key, val)

    #--------------------------------------------#
    # Fonctions du bloc de diffusion de messages #
    #--------------------------------------------#
    def getPropertiesMessages(self, key=None):
        if key:
            return getattr(self, "_%s" % key)
        else:
            return {"is_message_general": self._activer_message_general,
                    "message_general":    self._message_general,
                    "is_message_student": self._activer_bie,
                    "message_student":    self._bie_message,
                    "is_message_teacher": self._activer_message_enseignant,
                    "message_teacher":    self._message_enseignant}

    def setPropertiesMessages(self, form, request):
        # LOG.info("----- setPropertiesMessages -----")
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "_%s" % key, val)
        self.generateMessages(request)

    def generateMessages(self, request):
        # LOG.info("----- generateMessages -----")
        messages_properties = self.getPropertiesMessages()
        for key in messages_properties:
            request.set(key, messages_properties[key])

        #properties_messages = self.getPropertiesMaintenance()
        #for key in properties_messages:
        #    request.set(key, properties_messages[key])

        request.set("site", self.aq_parent.Title())
        request.set("maintenance", self.getPropertiesMaintenance())
        messages_template = ["<metal:macro define-macro=\"messages_folder_macro\">"]
        messages_template.append(self.restrictedTraverse("messages_folder/macro_messages_base")(REQUEST=request))
        messages_template.append("</metal:macro>metal:macro>")
        self.restrictedTraverse("messages_folder/Manager").pt_edit("\n".join(messages_template), "text/html", "utf-8")

        request.set("is_message_student", False)
        messages_template = ["<metal:macro define-macro=\"messages_folder_macro\">"]
        messages_template.append(self.restrictedTraverse("messages_folder/macro_messages_base")(REQUEST=request))
        messages_template.append("</metal:macro>metal:macro>")
        self.restrictedTraverse("messages_folder/Personnel").pt_edit("\n".join(messages_template), "text/html", "utf-8")

        request.set("is_message_teacher", False)
        request.set("is_message_student", messages_properties["is_message_student"])
        messages_template = ["<metal:macro define-macro=\"messages_folder_macro\">"]
        messages_template.append(self.restrictedTraverse("messages_folder/macro_messages_base")(REQUEST=request))
        messages_template.append("</metal:macro>metal:macro>")
        self.restrictedTraverse("messages_folder/Etudiant").pt_edit("\n".join(messages_template), "text/html", "utf-8")

    #-----------------------------#
    # Fonctions du bloc Courriels #
    #-----------------------------#
    def getPropertiesCourriels(self):
        return {"activer_erreur":          self._activer_erreur,
                "activer_email_erreur":    self._activer_email_erreur,
                "adresse_email_erreur":    self._adresse_email_erreur,
                "activer_liste_diffusion": self._activer_liste_diffusion,
                "type_diffusion":          self._type_diffusion,
                "format_diffusion":        self._format_diffusion}

    def setPropertiesCourriels(self, form):
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "_%s" % key, val)

    def isMailhost(self):
        mailhost = getToolByName(self, 'MailHost')
        if getattr(mailhost, 'smtp_host', ''):
            return True
        else:
            return False

    #-------------------------#
    # Fonctions de Mon Espace #
    #-------------------------#
    def getPropertiesMonEspace(self, key=None):
        if key:
            return getattr(self, "_%s" % key)
        else:
            return {"activer_fichiers":                  self._activer_fichiers,
                    "activer_presentations_sonorisees":  self._activer_presentations_sonorisees,
                    "activer_exercices_wims":            self._activer_exercices_wims,
                    "activer_liens":                     self._activer_liens,
                    "activer_liens_catalogue_bu":        self._activer_liens_catalogue_bu,
                    "activer_tags_catalogue_bu":         self._activer_tags_catalogue_bu,
                    "activer_lille1pod":                 self._activer_lille1pod,
                    "activer_termes_glossaire":          self._activer_termes_glossaire,
                    "activer_webconferences":            self._activer_webconferences,
                    "activer_lien_intracursus":          self._activer_lien_intracursus,
                    "lien_intracursus":                  self._lien_intracursus,
                    "activer_lien_assistance":           self._activer_lien_assistance,
                    "lien_assitance":                    self._lien_assitance,
                    "activer_video":                     self._activer_video,
                    "url_video":                         self._url_video,
                    "activer_vod":                       self._activer_vod}

    def getGridMonEspace(self, key=None):
        return [{"espace":      "fichiers",
                 "titre":       "Fichiers",
                 "activer":     self._activer_fichiers,
                 "repertoire":  "Fichiers",
                 "icone":       "fa fa-files-o"},
                {"espace":      "connect",
                 "titre":       "Présentations sonorisées",
                 "activer":     self._activer_presentations_sonorisees,
                 "repertoire":  "Sonorisation",
                 "icone":       "fa fa-microphone"},
                {"espace":      "wims",
                 "titre":       "Exercices Wims",
                 "activer":     self._activer_exercices_wims,
                 "repertoire":  "Wims",
                 "icone":       "fa fa-random"},
                {"espace":      "liens",
                 "titre":       "Ressources externes",
                 "activer":     self._activer_liens,
                 "repertoire":  "Externes",
                 "icone":       "fa fa-external-link"},
                {"espace":      "glossaire",
                 "titre":       "Termes de glossaire",
                 "activer":     self._activer_termes_glossaire,
                 "repertoire":  "Glossaire",
                 "icone":       "fa fa-font"},
                {"espace":      "connect",
                 "titre":       "Webconférences",
                 "activer":     self._activer_webconferences,
                 "repertoire":  "Webconference",
                 "icone":       "fa fa-headphones"},
                {"espace":      "video",
                 "titre":       "Vidéos",
                 "activer":     self._activer_lille1pod,
                 "repertoire":  "Video",
                 "icone":       "fa fa-youtube-play"},
                {"espace":      "vod",
                 "titre":       "VOD",
                 "activer":     self._activer_vod,
                 "repertoire":  "VOD",
                 "icone":       "fa fa-video-camera"}]

    def getGridMonEspaceNew(self, key=None):
        return [{"css":       "fichiers",
                 "title":     "Fichiers",
                 "activated": self._activer_fichiers,
                 "link":      "mes_ressources/mes_fichiers",
                 "icon":      "fa fa-files-o"},
                {"css":       "connect",
                 "title":     "Présentations sonorisées",
                 "activated": self._activer_presentations_sonorisees,
                 "link":      "mes_ressources/mes_presentations_sonorisees",
                 "icon":      "fa fa-microphone"},
                {"css":       "wims",
                 "title":     "Exercices Wims",
                 "activated": self._activer_exercices_wims,
                 "link":      "mes_ressources/mes_exercices_wims",
                 "icon":      "fa fa-random"},
                {"css":       "liens",
                 "title":     "Ressources externes",
                 "activated": self._activer_liens,
                 "link":      "mes_ressources/mes_ressources_externes",
                 "icon":      "fa fa-external-link"},
                {"css":       "glossaire",
                 "title":     "Termes de glossaire",
                 "activated": self._activer_termes_glossaire,
                 "link":      "mes_ressources/mes_termes_glossaire",
                 "icon":      "fa fa-font"},
                {"css":       "connect",
                 "title":     "Webconférences",
                 "activated": self._activer_webconferences,
                 "link":      "mes_ressources/mes_webconferences",
                 "icon":      "fa fa-headphones"},
                {"css":       "video",
                 "title":     "Vidéos",
                 "activated": self._activer_lille1pod,
                 "link":      "mes_ressources/mes_videos_pod",
                 "icon":      "fa fa-youtube-play"},
                {"css":       "vod",
                 "title":     "VOD",
                 "activated": self._activer_vod,
                 "link":      "mes_ressources/mes_vods",
                 "icon":      "fa fa-video-camera"}]

    def setPropertiesMonEspace(self, form, request):
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "_%s" % key, val)
        self.generatePageMonEspace(request)

    def isAdobeConnect(self):
        portal = self.portal_url.getPortalObject()
        connect = getattr(portal, "portal_connect", None)
        if connect:
            url_connexion = connect.getConnectProperty("url_connexion")
            if not url_connexion or url_connexion == "http://domainname.com/api/xml":
                return {"module":  False,
                        "message": "Le module Adobe Connect de Jalon n'est pas configuré"}
            else:
                return {"module":  True,
                        "message": "Test"}
        else:
            return {"module":  False,
                    "message": "Vous n'avez pas de module Adobe Connect installé dans Jalon"}

    def getPropertiesAdobeConnect(self):
        portal = self.portal_url.getPortalObject()
        connect = getattr(portal, "portal_connect", None)
        if connect:
            return {"url_connexion" : connect.getConnectProperty("url_connexion"),
                    "login"         : connect.getConnectProperty("login"),
                    "password"      : connect.getConnectProperty("password"),
                    "version"       : connect.getConnectProperty("version"),
                    "num_serveur"   : connect.getConnectProperty("num_serveur"),
                    "etablissement" : connect.getConnectProperty("etablissement"),
                    "dossiers"      : connect.getConnectProperty("dossiers"), }
        else:
            return None

    def setPropertiesAdobeConnect(self, form):
        portal = self.portal_url.getPortalObject()
        connect = getattr(portal, "portal_connect", None)
        connect.setProperties(form)

    def isWims(self):
        portal = self.portal_url.getPortalObject()
        wims = getattr(portal, "portal_wims", None)
        if wims:
            url_connexion = wims.getWimsProperty("url_connexion")
            if not url_connexion or url_connexion == "http://domainname.com/wims/wims.cgi":
                return {"module"  : False,
                        "message" : "Le module Wims de Jalon n'est pas configuré"}
            else:
                return {"module"  : True,
                        "message" : "Test"}
        else:
            return {"module"  : False,
                    "message" : "Vous n'avez pas de module Wims installé dans Jalon"}

    def getPropertiesWims(self):
        portal = self.portal_url.getPortalObject()
        wims = getattr(portal, "portal_wims", None)
        if wims:
            return {"url_connexion"       : wims.getWimsProperty("url_connexion"),
                    "login"               : wims.getWimsProperty("login"),
                    "password"            : wims.getWimsProperty("password"),
                    "classe_locale"       : wims.getWimsProperty("classe_locale"),
                    "nom_institution"     : wims.getWimsProperty("nom_institution"),
                    "donnees_classe"      : wims.getWimsProperty("donnees_classe"),
                    "donnees_superviseur" : wims.getWimsProperty("donnees_superviseur"),
                    "donnees_exercice"    : wims.getWimsProperty("donnees_exercice"), }
        else:
            return None

    def setPropertiesWims(self, form):
        portal = self.portal_url.getPortalObject()
        wims = getattr(portal, "portal_wims", None)
        wims.setProperties(form)

    def isPrimo(self):
        portal = self.portal_url.getPortalObject()
        primo = getattr(portal, "portal_primo", None)
        if primo:
            url_connexion = primo.getPrimoProperty("url_connexion")
            if not url_connexion or url_connexion == "http://domainname.com/PrimoWebServices/xservice/":
                return {"module"  : False,
                        "message" : "Le module ExLibris Primo de Jalon n'est pas configuré"}
            else:
                return {"module"  : True,
                        "message" : "Test"}
        else:
            return {"module"  : False,
                    "message" : "Vous n'avez pas de module ExLibris Primo installé dans Jalon"}

    def getPropertiesPrimo(self):
        portal = self.portal_url.getPortalObject()
        primo = getattr(portal, "portal_primo", None)
        if primo:
            return {"url_connexion"   : primo.getPrimoProperty("url_connexion"),
                    "url_catalogue"   : primo.getPrimoProperty("url_catalogue"),
                    "url_acquisition" : primo.getPrimoProperty("url_acquisition"), }
        else:
            return None

    def setPropertiesPrimo(self, form):
        portal = self.portal_url.getPortalObject()
        primo = getattr(portal, "portal_primo", None)
        primo.setProperties(form)

    #-------------------#
    # Fonctions Twitter #
    #-------------------#
    def getPropertiesTwitter(self, key=None):
        if key:
            return getattr(self, "_%s" % key)
        else:
            return {"COMPTE_TWITTER":     self._COMPTE_TWITTER,
                    "APP_KEY":            self._APP_KEY,
                    "APP_SECRET":         self._APP_SECRET,
                    "OAUTH_TOKEN":        self._OAUTH_TOKEN,
                    "OAUTH_TOKEN_SECRET": self._OAUTH_TOKEN_SECRET}

    def setPropertiesTwitter(self, form):
        for key in form.keys():
            setattr(self, "_%s" % key, form[key])

    def connexionTwitter(self):
        return Twython(self._APP_KEY, self._APP_SECRET, self._OAUTH_TOKEN, self._OAUTH_TOKEN_SECRET)

    def getTwitterCours(self, hashtag):
        twitter = self.connexionTwitter()
        try:
            tweets = twitter.search(q='from:%s+%s' % (self._COMPTE_TWITTER, hashtag), count=50)
            liste = []
            for tweet in tweets['statuses']:
                #print 'Tweet from @%s Date: %s' % (tweet['user']['screen_name'].encode('utf-8'), tweet['created_at'])
                #print tweet['text'].encode('utf-8')
                liste.append({"date": DateTime(tweet['created_at'], datefmt='international').strftime("%d/%m/%Y %H:%M"),
                              "texte": tweet['text']})
            return liste
        except TwythonError as e:
            print e

    #----------------------------------------------------#
    # Fonctions de récupération des données utilisateurs #
    #----------------------------------------------------#
    def getPropertiesDonneesUtilisateurs(self, key=None):
        if key:
            return getattr(self, "_%s" % key)
        else:
            return {"activer_ldap":           self._activer_ldap,
                    "base_ldap":              self._base_ldap,
                    "schema_ldap":            self._schema_ldap,
                    "fiche_ldap":             self._fiche_ldap,
                    "activer_trombinoscope":  self._activer_trombinoscope,
                    "activer_stockage_photo": self._activer_stockage_photo,
                    "lien_trombinoscope":     self._lien_trombinoscope}

    def setPropertiesDonneesUtilisateurs(self, form):
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_"):
                val = int(val)
            setattr(self, "_%s" % key, val)

    def isLDAP(self):
        return jalon_utils.isLDAP()

    def rechercherUtilisateur(self, username, typeUser, match=False, attribut="displayName"):
        """recherche un Utilisateur."""
        if self.isLDAP():
            if self._schema_ldap == "supann":
                ldap = "ldap-plugin"
                if typeUser == "Etudiant":
                    ldap = "ldap-plugin-etu"
                return self.rechercherUserLDAPSupann(username, attribut, ldap, match)
            if self._schema_ldap == "eduPerson":
                return self.rechercherUserLDAPEduPerson(username, attribut, "ldap-plugin", match)
        else:
            portal_jalon_bdd = getToolByName(self, "portal_jalon_bdd")
            return portal_jalon_bdd.rechercherUtilisateursByName(username, typeUser)

    def rechercherUserLDAPSupann(self, username, attribut, ldap="ldap-plugin", match=False):
        retour = []
        acl_users = getattr(getattr(getattr(self, "acl_users"), ldap), "acl_users")
        for user in acl_users.findUser(search_param=attribut, search_term=username, exact_match=match):
            if "supannAliasLogin" in user:
                email = user["supannAliasLogin"]
                if "mail" in user:
                    email = user["mail"].decode("iso-8859-1")
                retour.append({"id":    user["supannAliasLogin"],
                               "name":  user["displayName"].decode("iso-8859-1"),
                               "email": email})
        return json.dumps(retour)

    def rechercherUserLDAPEduPerson(self, username, attribut, ldap="ldap-plugin", match=False):
        retour = []
        eduPersonAffiliation = ["employee", "faculty"]
        if ldap == "ldap-plugin-etu":
            eduPersonAffiliation = ["student"]
        acl_users = getattr(getattr(getattr(self, "acl_users"), ldap), "acl_users")
        for user in acl_users.findUser(search_param=attribut, search_term=username, exact_match=match):
            if "login" in user and user["eduPersonAffiliation"] in eduPersonAffiliation:
                email = user["login"]
                if "mail" in user:
                    email = user["mail"].decode("iso-8859-1")
                retour.append({"id":    user["login"],
                               "name":  user["displayName"].decode("iso-8859-1"),
                               "email": email})
        return json.dumps(retour)

    #-------------------------------#
    # Fonctions de Google Analytics #
    #-------------------------------#
    def getPropertiesGA(self, key=None):
        if key:
            return getattr(self, "_%s" % key)
        else:
            return {"activer_ga":    self._activer_ga,
                    "ga_id_account": self._ga_id_account,
                    "ga_id_domain":  self._ga_id_domain,
                    "ga_cryptage":   self._ga_cryptage}

    def setPropertiesGA(self, form):
        for key in form.keys():
            val = form[key]
            if key == "activer_ga":
                val = int(val)
            setattr(self, "_%s" % key, val)

    #--------------------------#
    # Fonctions de Maintenance #
    #--------------------------#
    def getPropertiesMaintenance(self):
        date_debut_maintenance = self._date_debut_maintenance
        if not date_debut_maintenance:
            date_debut_maintenance = DateTime()
        date_fin_maintenance = self._date_fin_maintenance
        if not date_fin_maintenance:
            date_fin_maintenance = DateTime()
        return {"annoncer_maintenance":       self._annoncer_maintenance,
                "activer_maintenance":        self._activer_maintenance,
                "date_debut_maintenance":     date_debut_maintenance,
                "date_debut_maintenance_aff": jalon_utils.getLocaleDate(date_debut_maintenance, '%d %B %Y - %Hh%M'),
                "date_fin_maintenance":       date_fin_maintenance,
                "date_fin_maintenance_aff":   jalon_utils.getLocaleDate(date_fin_maintenance, '%d %B %Y - %Hh%M'),
                "annoncer_vider_cache":       self._annoncer_vider_cache,
                "url_news_maintenance":       self._url_news_maintenance}

    def setPropertiesMaintenance(self, form, request):
        # LOG.info("----- setPropertiesMaintenance -----")
        for key in form.keys():
            val = form[key]
            if key.startswith("activer_") or key.startswith("annoncer_"):
                val = int(val)
            if key.startswith("date_"):
                val = DateTime(val)
            setattr(self, "_%s" % key, val)
        self.generatePageMonEspace(request)
        self.generateMessages(request)

    #------------------------#
    # Fonction Elasticsearch #
    #------------------------#
    def getPropertiesElasticsearch(self):
        portal = self.portal_url.getPortalObject()
        portal_elasticsearch = getattr(portal, "portal_jalon_elasticsearch", None)
        return portal_elasticsearch.getPropertiesElasticsearch()

    def setPropertiesElasticsearch(self, propertiesElasticsearch):
        portal = self.portal_url.getPortalObject()
        portal_elasticsearch = getattr(portal, "portal_jalon_elasticsearch", None)
        portal_elasticsearch.setPropertiesElasticsearch(propertiesElasticsearch)

    def searchElasticsearch(self, type_search=None, term_search=None, page=1):
        portal = self.portal_url.getPortalObject()
        portal_elasticsearch = getattr(portal, "portal_jalon_elasticsearch", None)
        return portal_elasticsearch.searchElasticsearch(type_search, term_search, page)

    def isElasticsearch(self):
        portal = self.portal_url.getPortalObject()
        portal_jalon_elasticsearch = getattr(portal, "portal_jalon_elasticsearch", None)
        if portal_jalon_elasticsearch:
            elasticsearch_properties = portal_jalon_elasticsearch.getPropertiesElasticsearch()
            if not elasticsearch_properties["url_connexion"] or elasticsearch_properties["url_connexion"] == "http://domainname.com/":
                return {"module":  False,
                        "message": "Le module Elasticsearch de Jalon n'est pas configuré"}
            else:
                return {"module":  True,
                        "message": "Test"}
        else:
            return {"module":  False,
                    "message": "Vous n'avez pas de module Elasticsearch installé dans Jalon"}

    #----------------#
    # Fonction Wowza #
    #----------------#
    def isVOD(self):
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        if portal_jalon_wowza:
            wowza_properties = portal_jalon_wowza.getWowzaProperties()
            if not wowza_properties["wowza_server"] or wowza_properties["wowza_server"] == "http://domainname.com":
                return {"module":  False,
                        "message": "Le module Wowza de Jalon n'est pas configuré"}
            else:
                return {"module":  True,
                        "message": "Test"}
        else:
            return {"module":  False,
                    "message": "Vous n'avez pas de module Wowza installé dans Jalon"}

    def getWowzaProperties(self):
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        return portal_jalon_wowza.getWowzaProperties()

    def setWowzaProperties(self, wowzaProperties):
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        portal_jalon_wowza.setWowzaProperties(wowzaProperties)

    def searchExtraits(self, page, term_search):
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        return portal_jalon_wowza.searchExtraits(page, term_search)

    def getExpirationDate(self, pod):
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        return portal_jalon_wowza.getStreamingAvailable(pod)

    def modifyStreaming(self, params):
        # LOG.info("----- modifyStreaming -----")
        # LOG.info(params)
        portal = self.portal_url.getPortalObject()
        portal_jalon_wowza = getattr(portal, "portal_jalon_wowza", None)
        if "datetime-expiration_date" in params:
            portal_jalon_wowza.modifyStreaming(params["pod"], params["datetime-expiration_date"])
        else:
            portal_jalon_wowza.modifyStreaming(params["pod"])

    # -----------------------#
    # Gestion des catégories #
    #------------------------#
    def getCategorie(self, key=None):
        if key:
            return self._categories.get(int(key), None)
        return dict(self._categories)

    def getClefCategories(self):
        clefs = self._categories.keys()[:]
        clefs.sort(lambda x, y: cmp(int(x), int(y)))
        return clefs

    def setCategories(self, categories):
        if type(self._categories).__name__ != "PersistentMapping":
            self._categories = PersistentDict(categories)
        else:
            self._categories = categories

    def getUsersCategorie(self, clef):
        categorie = self.getCategorie(int(clef))
        if categorie["users"] == ["all"]:
            return ["all"]
        return self.getInfosUsers(categorie["users"])

    def setUsersCategorie(self, form):
        categories = copy.deepcopy(self.getCategorie())
        if "all" in form:
            categories[int(form["clef"])]["users"] = ["all"]
        else:
            users = []
            if "users-actu" in form:
                users = form["users-actu"]
            if "username" in form:
                usernames = form["username"].split(",")
                if usernames != ['']:
                    for username in usernames:
                        if not username in users:
                            users.append(username)
            categories[int(form["clef"])]["users"] = users
        self.setCategories(categories)

    def getInfosUsers(self, users):
        infosUsers = []
        for user in users:
            result = self.rechercherUtilisateur(user, "Personnel", match=True, attribut="supannAliasLogin")
            infosUsers.append(json.loads(result)[0])
        infosUsers.sort(lambda x, y: cmp(x["name"], y["name"]))
        return infosUsers

    def creerCategorie(self, title):
        clefs = copy.deepcopy(self.getClefCategories())
        clef = int(clefs[-1]) + 1
        categories = self.getCategorie()
        categories[clef] = {"title": title, "users": []}
        self.setCategories(categories)

    def renommerCategorie(self, clef, title):
        categories = copy.deepcopy(self.getCategorie())
        categories[int(clef)]["title"] = title
        self.setCategories(categories)

    #--------------------#
    # Gestion du Podcast #
    #--------------------#
    def getVariablesPodcast(self):
        return {"activerPodcasts": self._activerPodcasts,
                "uploadPodcasts":  self._uploadPodcasts,
                "dnsPodcasts":     self._dnsPodcasts}

    def setVariablesPodcast(self, podcasts):
        if "activerPodcasts" in podcasts:
            self._activerPodcasts = podcasts["activerPodcasts"]
        self._uploadPodcasts = podcasts["uploadPodcasts"]
        self._dnsPodcasts = podcasts["dnsPodcasts"]

    def getUsersPodcast(self, tiny=None):
        if tiny:
            return self._dicoUsersPodcast.keys()
        listeUsers = []
        for user in self._dicoUsersPodcast.keys():
            listeUsers.append({"id": user,
                               "fullname": jalon_utils.getIndividu(user, "dict")["fullname"]})
        listeUsers.sort(lambda x, y: cmp(x["fullname"], y["fullname"]))
        return listeUsers

    def setDicoUsersPodcast(self, dicoUsersPodcast):
        if type(self._dicoUsersPodcast).__name__ != "PersistentMapping":
            self._dicoUsersPodcast = PersistentDict(dicoUsersPodcast)
        else:
            self._dicoUsersPodcast = dicoUsersPodcast

    def setUsersPodcast(self, form):
        dicoUsersPodcast = self._dicoUsersPodcast
        if "username" in form:
            usernames = form["username"].split(",")
            if usernames != ['']:
                for username in usernames:
                    if not username in dicoUsersPodcast.keys():
                        dicoUsersPodcast[username] = {}
                self.setDicoUsersPodcast(dicoUsersPodcast)

    def setUsersiTunesU(self, auteurCours):
        dicoUsersPodcast = self._dicoUsersPodcast
        if not auteurCours in dicoUsersPodcast:
            dicoUsersPodcast[auteurCours] = []
            self.setDicoUsersPodcast(dicoUsersPodcast)

    def setCoursUser(self, auteurCours, idCours):
        dicoUsersPodcast = self._dicoUsersPodcast
        listeCours = dicoUsersPodcast[auteurCours]
        if not idCours in listeCours:
            listeCours.append(idCours)
            dicoUsersPodcast[auteurCours] = listeCours
            self.setDicoUsersPodcast(dicoUsersPodcast)

    def getCoursUser(self, user):
        retour = []
        portal = self.aq_parent
        listeCours = self._dicoUsersPodcast[user]
        dicoLibCatITunesU = self._dicoLibCatITunesU
        repCours = getattr(getattr(portal, "cours"), user)
        for idCours in listeCours:
            cours = getattr(repCours, idCours, None)
            if cours:
                catiTunesU = cours.getCatiTunesU()
                if catiTunesU:
                    catPrinCours = dicoLibCatITunesU[catiTunesU[:3]]
                    catSecCours = dicoLibCatITunesU[catiTunesU]
                else:
                    catPrinCours = "Erreur : catégorie à redéfinir"
                    catSecCours = ""
                retour.append({"idCours":      idCours,
                               "titreCours":   cours.Title(),
                               "etatCours":    cours.isDiffuseriTunesU(),
                               "catPrinCours": catPrinCours,
                               "catSecCours":  catSecCours,
                               "urlCours":     cours.absolute_url()})

        retour.sort(lambda x, y: cmp(x["titreCours"], y["titreCours"]))
        return retour

    def getAffCatiTunesUCours(self, idCatiTunesU):
        dicoLibCatITunesU = self._dicoLibCatITunesU
        catPrinCours = dicoLibCatITunesU[idCatiTunesU[:3]]
        catSecCours = dicoLibCatITunesU[idCatiTunesU]
        return "%s / %s" % (catPrinCours, catSecCours)

    def validerCoursiTunesU(self, idCours, auteurCours):
        portal = self.aq_parent
        repCours = getattr(getattr(portal, "cours"), auteurCours)
        cours = getattr(repCours, idCours, None)
        if idCours:
            cours.setProperties({"diffusioniTunesU": True})
            cours.setProperties({"DateDerniereModif": DateTime()})
            infosMembre = jalon_utils.getIndividu(auteurCours, "dict")
            jalon_utils.envoyerMail({"a":       infosMembre["email"],
                                     "objet":   "Validation de votre demande iTunesU",
                                     "message": "Bonjour\n\nLe cours \"%s\" pour lequel vous avez demandé une publication sur iTunesU a été validé dans la catégorie : \"%s\".\n\nCordialement,\nL'équipe %s" % (cours.Title(), cours.getAffCatiTunesUCours(), portal.Title()), })

    def rejeterCoursiTunesU(self, idCours, auteurCours):
        portal = self.aq_parent
        repCours = getattr(getattr(portal, "cours"), auteurCours)
        cours = getattr(repCours, idCours, None)
        if idCours:
            infosMembre = jalon_utils.getIndividu(auteurCours, "dict")
            jalon_utils.envoyerMail({"a":        infosMembre["email"],
                                     "objet":    "Rejet de votre demande iTunesU",
                                     "message": "Bonjour\n\nLe cours \"%s\" pour lequel vous avez demandé une publication sur iTunesU dans la catégorie : \"%s\" a été rejeté.\n\nNous vous remercions de votre compréhension,\n\nCordialement,\nL'équipe %s" % (cours.Title(), cours.getAffCatiTunesUCours(), portal.Title()), })
            cours.setProperties({"DiffusioniTunesU": False})
            cours.setProperties({"CatiTunesU": ""})
            cours.setProperties({"DateDerniereModif": DateTime()})
            dicoUsersPodcast = self._dicoUsersPodcast
            listeCours = dicoUsersPodcast[auteurCours]
            listeCours.remove(idCours)
            dicoUsersPodcast[auteurCours] = listeCours
            self.setDicoUsersPodcast(dicoUsersPodcast)

    def getCatITunesU(self):
        return self._catITunesU

    def getPropertiesCatiTunesU(self):
        return {"dicoLibCatITunesU" : self._dicoLibCatITunesU,
                "catITunesU"        : self._catITunesU,
                "ordreCatiTunesU"   : self._ordreCatiTunesU}

    def getListeCatITunesU(self):
        listeCatITunesU = self._catITunesU.keys()
        listeCatITunesU.sort()
        return listeCatITunesU

    #-------------------------------#
    # Fonction Communication NodeJS #
    #-------------------------------#
    def getPropertiesCommunication(self):
        portal = self.portal_url.getPortalObject()
        portal_jalon_communication = getattr(portal, "portal_jalon_communication", None)
        return portal_jalon_communication.getPropertiesCommunication()

    def setPropertiesCommunication(self, propertiesCommunication):
        portal = self.portal_url.getPortalObject()
        portal_jalon_communication = getattr(portal, "portal_jalon_communication", None)
        portal_jalon_communication.setPropertiesCommunication(propertiesCommunication)

    #----------------------#
    # Fonction Breadcrumbs #
    #----------------------#
    def getBreadcrumbs(self, page="Basic"):
        return self.__getattribute__("getBreadcrumbs%s" % page)()

    def getBreadcrumbsBasic(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()}]

    def getBreadcrumbsConnexion(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()},
                {"title": _(u"Connexion à Jalon"),
                 "icon":  "fa fa-key",
                 "link":  "%s/portal_jalon_properties/gestion_connexion" % self.absolute_url()}]

    def getBreadcrumbsMonEspace(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()},
                {"title": _(u"Gestion \"Mes ressources\""),
                 "icon":  "fa fa-folder-open",
                 "link":  "%s/portal_jalon_properties/gestion_mes_ressources" % self.absolute_url()}]

    def getBreadcrumbsMesCours(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()},
                {"title": _(u"Gestion des Cours"),
                 "icon":  "fa fa-university",
                 "link":  "%s/portal_jalon_properties/gestion_mes_cours" % self.absolute_url()}]

    def getBreadcrumbsInformations(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()},
                {"title": _(u"Gestion des liens d'informations"),
                 "icon":  "fa fa-external-link-square",
                 "link":  "%s/portal_jalon_properties/gestion_infos" % self.absolute_url()}]

    def getBreadcrumbsDidacticiels(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()},
                {"title": _(u"Gestion des didacticiels"),
                 "icon":  "fa fa-life-ring",
                 "link":  "%s/portal_jalon_properties/gestion_didacticiels" % self.absolute_url()}]

    def getBreadcrumbsMessages(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()},
                {"title": _(u"Gestion de la diffusion de messages"),
                 "icon":  "fa fa-bullhorn",
                 "link":  "%s/portal_jalon_properties/gestion_messages" % self.absolute_url()}]

    def getBreadcrumbsEmail(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()},
                {"title": _(u"Gestion des paramètres de courriels"),
                 "icon":  "fa fa-envelope-o",
                 "link":  "%s/portal_jalon_properties/gestion_email" % self.absolute_url()}]

    def getBreadcrumbsUsers(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()},
                {"title": _(u"Gestion des données utilisateurs"),
                 "icon":  "fa fa-users",
                 "link":  "%s/portal_jalon_properties/gestion_donnees_utilisateurs" % self.absolute_url()}]

    def getBreadcrumbsGA(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()},
                {"title": _(u"Gestion de Google Analytics"),
                 "icon":  "fa fa-line-chart",
                 "link":  "%s/portal_jalon_properties/gestion_ga" % self.absolute_url()}]

    def getBreadcrumbsMaintenance(self):
        return [{"title": _(u"Configuration de Jalon"),
                 "icon":  "fa fa-cogs",
                 "link":  "%s/portal_jalon_properties/@@jalon_properties" % self.absolute_url()},
                {"title": _(u"Gestion des paramètres de maintenance"),
                 "icon":  "fa fa-umbrella",
                 "link":  "%s/portal_jalon_properties/gestion_maintenance" % self.absolute_url()}]
