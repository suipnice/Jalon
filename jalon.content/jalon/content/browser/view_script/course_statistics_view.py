# -*- coding: utf-8 -*-

from Products.Five import BrowserView

from jalon.content.content import jalon_utils
from jalon.content import contentMessageFactory as _

from DateTime import DateTime

from logging import getLogger
LOG = getLogger('[CourseStatisticsView]')
"""
# Log examples :
# LOG.info('info message')
"""


class CourseStatisticsView(BrowserView):

    def __init__(self, context, request):
        # LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def getBreadcrumbs(self):
        portal = self.context.portal_url.getPortalObject()
        return [{"title": _(u"Mes cours"),
                 "icon":  "fa fa-university",
                 "link":  "%s/mes_cours" % portal.absolute_url()},
                {"title": self.context.Title(),
                 "icon":  "fa fa-book",
                 "link":  self.context.absolute_url()},
                {"title": "Statistiques",
                 "icon":  "fa fa-bar-chart",
                 "link":  "%s/course_statistics_view" % self.context.absolute_url()}]

    def getRequest(self):
        return self.request

    def getPageView(self, user, mode_etudiant):
        # LOG.info("----- getPageView -----")
        is_personnel = self.context.isPersonnel(user, mode_etudiant)
        mode_etudiant = "false" if (not mode_etudiant) and is_personnel else mode_etudiant

        my_view = {"is_personnel":  is_personnel,
                   "mode_etudiant": mode_etudiant}

        onglet = self.request.get("onglet", "1")
        onglets = []
        cours_url = self.context.absolute_url()
        onglets.append({"href":      "%s/course_statistics_view?onglet=1" % cours_url,
                        "css_class": " selected" if onglet == "1" else "",
                        "icon":      "fa-info",
                        "text":      "Généralités"})
        onglets.append({"href":      "%s/course_statistics_view?onglet=2" % cours_url,
                        "css_class": " selected" if onglet == "2" else "",
                        "icon":      "fa-bar-chart",
                        "text":      "Fréquentation"})
        onglets.append({"href":      "%s/course_statistics_view?onglet=3" % cours_url,
                        "css_class": " selected" if onglet == "3" else "",
                        "icon":      "fa-files-o",
                        "text":      "Supports pédagogiques"})
        onglets.append({"href":      "%s/course_statistics_view?onglet=4" % cours_url,
                        "css_class": " selected" if onglet == "4" else "",
                        "icon":      "fa-random",
                        "text":      "Activités"})

        my_view["onglets"] = onglets
        my_view["onglet_view"] = self.getOngletView(onglet, is_personnel)

        if onglet == "1":
            my_view["course_actions"] = my_view["onglet_view"]["course_actions"]
        return my_view

    def getOngletView(self, onglet, is_personnel):
        # LOG.info("----- getOngletView -----")
        if onglet == "1":
            return self.getIndicateursGeneralitesView(is_personnel)
        if onglet == "2":
            return self.getIndicateursFrequentationView()
        if onglet == "3":
            return self.getIndicateursRessourcesView()
        if onglet == "4":
            return self.getIndicateursActivitiesView()

    def getElementsCoursByType(self):
        # LOG.info("----- getElementsCoursByType -----")
        element_by_type_dict = {"Titre":          {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "TexteLibre":     {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "Fichiers":       {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "Webconference":  {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "Externes":       {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "Video":          {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "VOD":            {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "Presentations":  {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "BoiteDepot":     {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "AutoEvaluation": {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "Examen":         {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "SalleVirtuelle": {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "Forum":          {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "Forums":         {"elements_count": len(self.context.forum.objectIds()), "elements_list": [], "elements_dict": {}},
                                "TermeGlossaire": {"elements_count": 0, "elements_list": [], "elements_dict": {}},
                                "Bibliographie":  {"elements_count": len(self.context.getBibliographie()), "elements_list": [], "elements_dict": {}}}
        element_cours_dict = self.context.getCourseItemProperties()
        for element_id in element_cours_dict.keys():
            type_element = element_cours_dict[element_id]["typeElement"]
            if type_element in ["File", "Image", "Page"]:
                type_element = "Fichiers"
            if type_element in ["Lien web", "Lecteur exportable", "Ressource bibliographique", "Catalogue BU", "Video", "VOD"]:
                type_element = "Externes"
            if type_element in ["Presentations sonorisees", "Sonorisation"]:
                type_element = "Presentations"
            element_by_type_dict[type_element]["elements_count"] += 1
            element_by_type_dict[type_element]["elements_list"].append(element_id)
            element_by_type_dict[type_element]["elements_dict"][element_id] = element_cours_dict[element_id]["titreElement"]
        return element_by_type_dict

    def getIndicateursGeneralitesView(self, is_personnel):
        # LOG.info("----- getIndicateursGeneralitesView -----")
        course_training_offer_list = self.context.getCourseTrainingOffer()
        course_training_offer_students = 0
        for course_training_offer in course_training_offer_list:
            course_training_offer_students = course_training_offer_students + int(course_training_offer["nb_etu"])
        course_training_offer = len(course_training_offer_list)

        course_actions = [{"course_actions_id":           "course_to",
                           "course_actions_icon":         "fa fa-university fa-fw",
                           "course_actions_text":         "Offre(s) de formation",
                           "course_actions_list":         [],
                           "course_actions_registration": "%s (%s étu.)" % (course_training_offer, course_training_offer_students),
                           "is_course_password":          False}]
        course_actions.append({"course_actions_id":           "course_nr",
                               "course_actions_icon":         "fa fa-users fa-fw",
                               "course_actions_text":         "Inscription(s) nominative(s)",
                               "course_actions_list":         [],
                               "course_actions_registration": len(self.context.getGroupe()),
                               "is_course_password":          False})
        course_actions.append({"course_actions_id":           "course_er",
                               "course_actions_icon":         "fa fa-envelope-o fa-fw",
                               "course_actions_text":         "Invitation(s) par courriel",
                               "course_actions_list":         [],
                               "course_actions_registration": len(self.context.getInvitations()),
                               "is_course_password":          False})
        course_actions.append({"course_actions_id":           "course_pr",
                               "course_actions_icon":         "fa fa-key fa-fw",
                               "course_actions_text":         "Accès par mot de passe",
                               "course_actions_list":         [],
                               "course_actions_registration": len(self.context.getInscriptionsLibres()),
                               "is_course_password":          self.context.getLibre() and is_personnel,
                               "course_password":             self.context.getLienMooc()})
        course_actions.append({"course_actions_id":           "course_cr",
                               "course_actions_icon":         "fa fa-users fa-fw",
                               "course_actions_text":         "Lecteur(s) enseignant(s)",
                               "course_actions_list":         [],
                               "course_actions_registration": len(self.context.getCoLecteurs()),
                               "is_course_password":          False})

        nb_element_by_type = {"Titre":          0,
                              "TexteLibre":     0,
                              "Fichiers":       0,
                              "Webconference":  0,
                              "Externes":       0,
                              "Video":          0,
                              "VOD":            0,
                              "Presentations":  0,
                              "BoiteDepot":     0,
                              "AutoEvaluation": 0,
                              "Examen":         0,
                              "SalleVirtuelle": 0,
                              "Forum":          0,
                              "Forums":         len(self.context.forum.objectIds()),
                              "TermeGlossaire": 0,
                              "Bibliographie":  len(self.context.getBibliographie())}
        element_cours = self.context.getCourseItemProperties()
        course_map = self.context.getCourseMapList()
        for element_id in course_map:
            element = element_cours[element_id]
            type_element = element["typeElement"]
            if type_element in ["File", "Image", "Page"]:
                type_element = "Fichiers"
            if type_element in ["Lien web", "Lecteur exportable", "Ressource bibliographique", "Catalogue BU", "Video", "VOD"]:
                type_element = "Externes"
            if type_element in ["Presentations sonorisees", "Sonorisation"]:
                type_element = "Presentations"
            nb_element_by_type[type_element] += 1
        return {"macro":               "indicateurs_generalite",
                "created":             jalon_utils.getLocaleDate(self.context.created(), "%d/%m/%Y &agrave; %H:%M"),
                "modified":            jalon_utils.getLocaleDate(self.context.modified(), "%d/%m/%Y &agrave; %H:%M"),
                "nb_element_by_type":  nb_element_by_type,
                "course_actions":      course_actions}

    def getIndicateursFrequentationView(self):
        # LOG.info("----- getIndicateursFrequentationView -----")
        graph = ""
        requete = self.context.getConsultationByCoursByUniversityYearByDate(None, False, False).all()
        # LOG.info(requete)
        if requete:
            requete_dict = {}
            for ligne in requete:
                try:
                    requete_dict[ligne[0]].append({"consultations": ligne[1], "public": ligne[2]})
                except:
                    requete_dict[ligne[0]] = [{"consultations": ligne[1], "public": ligne[2]}]
            try:
                requete_dict[ligne[0]].sort(lambda x, y: cmp(x["public"], y["public"]))
            except:
                pass
            graph = self.context.genererGraphIndicateurs(requete_dict)

        frequentation_graph = ""
        requete2 = self.context.getConsultationByCoursByUniversityYearByDate(None, True, "Etudiant").all()
        # LOG.info(requete2)
        if requete2:
            requete_dict = dict(requete2)
            frequentation_graph = self.context.genererFrequentationGraph(requete_dict)
            # LOG.info(frequentation_graph)

        return {"macro":               "indicateurs_frequentation",
                "year":                "%s/%s" % (DateTime().year() - 1, DateTime().year()),
                "graph":               graph,
                "frequentation_graph": frequentation_graph}

    def getIndicateursRessourcesView(self):
        # LOG.info("----- getIndicateursRessourcesView -----")
        box = self.request.get("box", "1")
        box_dict = {"1": "Fichiers",
                    "2": "Presentations sonorisees",
                    "3": "Externes",
                    "4": "Webconference",
                    "5": "Video",
                    "6": "VOD"}
        cours_url = self.context.absolute_url()
        box_list = [{"css_class": "button radius%s" % (" selected" if box == "1" else " off"),
                     "link_url":  "%s/course_statistics_view?onglet=3&box=1" % cours_url,
                     "icon":      "fa-files-o",
                     "link_text": "Fichiers"},
                    {"css_class": "button radius%s" % (" selected" if box == "2" else " off"),
                     "link_url":  "%s/course_statistics_view?onglet=3&box=2" % cours_url,
                     "icon":      "fa-microphone",
                     "link_text": "Présentations sonorisées"},
                    {"css_class": "button radius%s" % (" selected" if box == "3" else " off"),
                     "link_url":  "%s/course_statistics_view?onglet=3&box=3" % cours_url,
                     "icon":      "fa-external-link",
                     "link_text": "Ressources externes"},
                    {"css_class": "button radius%s" % (" selected" if box == "4" else " off"),
                     "link_url":  "%s/course_statistics_view?onglet=3&box=4" % cours_url,
                     "icon":      "fa-headphones",
                     "link_text": "Webconférences"},
                    {"css_class": "button radius%s" % (" selected" if box == "5" else " off"),
                     "link_url":  "%s/course_statistics_view?onglet=3&box=5" % cours_url,
                     "icon":      "fa-youtube-play",
                     "link_text": "Vidéos"},
                    {"css_class": "button radius%s" % (" selected" if box == "6" else " off"),
                     "link_url":  "%s/course_statistics_view?onglet=3&box=6" % cours_url,
                     "icon":      "fa-video-camera",
                     "link_text": "VOD"}]
        element_id = self.request.get("element_id", None)
        thead_th_list = [{"data-sort": "nb_cons_month_before",
                          "th_title":  "les consultations du mois précédent",
                          "th_text":   "Mois précédent"},
                         {"data-sort": "nb_cons_month",
                          "th_title":  "les consultations du mois courant",
                          "th_text":   "Mois courant"},
                         {"data-sort": "nb_cons_year",
                          "th_title":  "les consultations sur l'année en cours",
                          "th_text":   "Année en cours"}]
        if not element_id:
            thead_th_list.insert(0, {"data-sort": "title",
                                     "th_title":  "le titre du fichier",
                                     "th_text":   "Titre"})
            elements_consultation = []
            elements_cours = self.getElementsCoursByType()
            if box_dict[box] in elements_cours:
                elements_consultation = self.context.getConsultationElementsByCours(elements_cours[box_dict[box]]["elements_list"], elements_cours[box_dict[box]]["elements_dict"])
                # LOG.info(len(elements_consultation))
                # LOG.info(elements_consultation)
            indicateurs_ressources_view = {"macro":                 "indicateurs_ressources",
                                           "box_list":              box_list,
                                           "second_macro":          "display_all_ressources",
                                           "thead_th_list":         thead_th_list,
                                           "elements_consultation": elements_consultation,
                                           "box_url":               "%s/course_statistics_view?onglet=3&box=%s" % (self.context.absolute_url(), box)}
        else:
            thead_th_list.insert(0, {"data-sort": "public",
                                     "th_title":  "le type de public",
                                     "th_text":   "Public"})
            graph = ""
            requete = self.context.getConsultationByElementByCoursByUniversityYearForGraph(element_id).all()
            # LOG.info(requete)
            if requete:
                requete_dict = {}
                for ligne in requete:
                    try:
                        requete_dict[ligne[0]].append({"consultations": ligne[1], "public": ligne[2]})
                    except:
                        requete_dict[ligne[0]] = [{"consultations": ligne[1], "public": ligne[2]}]
                try:
                    requete_dict[ligne[0]].sort(lambda x, y: cmp(x["public"], y["public"]))
                except:
                    pass
                graph = self.context.genererGraphIndicateurs(requete_dict)
            indicateurs_ressources_view = {"macro":                 "indicateurs_ressources",
                                           "element_title":         self.context.getCourseItemProperties(element_id)["titreElement"],
                                           "box_list":              box_list,
                                           "second_macro":          "display_ressource",
                                           "thead_th_list":         thead_th_list,
                                           "elements_consultation": self.context.getConsultationByElementByCours(element_id),
                                           "graph":                 graph,
                                           "box_url":               "%s/course_statistics_view?onglet=3&box=%s" % (self.context.absolute_url(), box)}
        return indicateurs_ressources_view

    def getIndicateursActivitiesView(self):
        """Fournit les indicateurs des Activites."""
        # LOG.info("----- getIndicateursActivitiesView -----")
        box = self.request.get("box", "1")
        box_dict = {"1": "BoiteDepot",
                    "2": "AutoEvaluation",
                    "3": "Examen",
                    "4": "SalleVirtuelle"}
        cours_url = self.context.absolute_url()
        box_list = [{"css_class": "button radius%s" % (" selected" if box == "1" else " off"),
                     "link_url":  "%s/course_statistics_view?onglet=4&box=1" % cours_url,
                     "icon":      "fa-inbox",
                     "link_text": "Boite de dépôts"},
                    {"css_class": "button radius%s" % (" selected" if box == "2" else " off"),
                     "link_url":  "%s/course_statistics_view?onglet=4&box=2" % cours_url,
                     "icon":      "fa-gamepad",
                     "link_text": "Auto-évaluation WIMS"},
                    {"css_class": "button radius%s" % (" selected" if box == "3" else " off"),
                     "link_url":  "%s/course_statistics_view?onglet=4&box=3" % cours_url,
                     "icon":      "fa-graduation-cap",
                     "link_text": "Examen WIMS"},
                    {"css_class": "button radius%s" % (" selected" if box == "4" else " off"),
                     "link_url":  "%s/course_statistics_view?onglet=4&box=4" % cours_url,
                     "icon":      "fa-globe",
                     "link_text": "Salle virtuelle"}]
        element_id = self.request.get("element_id", None)
        thead_th_list = [{"data-sort": "nb_cons_month_before",
                          "th_title":  "les consultations du mois précédent",
                          "th_text":   "Mois précédent"},
                         {"data-sort": "nb_cons_month",
                          "th_title":  "les consultations du mois courant",
                          "th_text":   "Mois courant"},
                         {"data-sort": "nb_cons_year",
                          "th_title":  "les consultations sur l'année en cours",
                          "th_text":   "Année en cours"}]
        if not element_id:
            thead_th_list.insert(0, {"data-sort": "title",
                                     "th_title":  "le titre du fichier",
                                     "th_text":   "Titre"})
            elements_consultation = []
            elements_cours = self.getElementsCoursByType()
            if box_dict[box] in elements_cours:
                elements_consultation = self.context.getConsultationElementsByCours(elements_cours[box_dict[box]]["elements_list"], elements_cours[box_dict[box]]["elements_dict"])
            indicateurs_activites_view = {"macro":                 "indicateurs_ressources",
                                          "box_list":              box_list,
                                          "second_macro":          "display_all_ressources",
                                          "thead_th_list":         thead_th_list,
                                          "elements_consultation": elements_consultation,
                                          "box_url":               "%s/course_statistics_view?onglet=4&box=%s" % (self.context.absolute_url(), box)}
        else:
            thead_th_list.insert(0, {"data-sort": "public",
                                     "th_title":  "le type de public",
                                     "th_text":   "Public"})
            graph = ""
            requete = self.context.getConsultationByElementByCoursByUniversityYearForGraph(element_id).all()
            # LOG.info(requete)
            if requete:
                requete_dict = {}
                for ligne in requete:
                    try:
                        requete_dict[ligne[0]].append({"consultations": ligne[1], "public": ligne[2]})
                    except:
                        requete_dict[ligne[0]] = [{"consultations": ligne[1], "public": ligne[2]}]
                try:
                    requete_dict[ligne[0]].sort(lambda x, y: cmp(x["public"], y["public"]))
                except:
                    pass
                graph = self.context.genererGraphIndicateurs(requete_dict)
            indicateurs_activites_view = {"macro":                "indicateurs_activites",
                                          "element_title":         self.context.getCourseItemProperties(element_id)["titreElement"],
                                          "box_list":              box_list,
                                          "second_macro":          "display_ressource",
                                          "thead_th_list":         thead_th_list,
                                          "elements_consultation": self.context.getConsultationByElementByCours(element_id),
                                          "graph":                 graph,
                                          "box_url":               "%s/course_statistics_view?onglet=4&box=%s" % (self.context.absolute_url(), box)}
        return indicateurs_activites_view
