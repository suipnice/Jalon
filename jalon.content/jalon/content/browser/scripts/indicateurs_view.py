# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from jalon.content.content import jalon_utils

from logging import getLogger
LOG = getLogger('[IndicateursView]')
"""
# Log examples :
# LOG.info('info message')
"""


class IndicateursView(BrowserView):
    template = ViewPageTemplateFile("../templates/cours_indicateurs_view.pt")

    def __init__(self, context, request):
        # LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def getRequest(self):
        return self.request

    def getPageView(self):
        # LOG.info("----- getPageView -----")
        onglet = self.request.get("onglet", "1")
        onglets = []
        cours_url = self.context.absolute_url()
        onglets.append({"href":      "%s/cours_indicateurs_view?onglet=1" % cours_url,
                        "css_class": " selected" if onglet == "1" else "",
                        "icon":      "fa-info",
                        "text":      "Généralités"})
        onglets.append({"href":      "%s/cours_indicateurs_view?onglet=2" % cours_url,
                        "css_class": " selected" if onglet == "2" else "",
                        "icon":      "fa-files-o",
                        "text":      "Supports pédagogiques"})
        onglets.append({"href":      "%s/cours_indicateurs_view?onglet=3" % cours_url,
                        "css_class": " selected" if onglet == "3" else "",
                        "icon":      "fa-random",
                        "text":      "Activités"})

        return {"onglets": onglets, "onglet_view": self.getOngletView(onglet)}

    def getOngletView(self, onglet):
        # LOG.info("----- getOngletView -----")
        if onglet == "1":
            return self.getIndicateursGeneralitesView()
        if onglet == "2":
            return self.getIndicateursRessourcesView()
        if onglet == "3":
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
        element_cours_dict = self.context.getElementCours()
        for element_id in element_cours_dict.keys():
            type_element = element_cours_dict[element_id]["typeElement"]
            if type_element in ["File", "Image", "Page"]:
                type_element = "Fichiers"
            if type_element in ["Lien web", "Lecteur exportable", "Ressource bibliographique", "Catalogue BU", "Video", "VOD"]:
                type_element = "Externes"
            if type_element == "Presentations sonorisees":
                type_element = "Presentations"
            element_by_type_dict[type_element]["elements_count"] += 1
            element_by_type_dict[type_element]["elements_list"].append(element_id)
            element_by_type_dict[type_element]["elements_dict"][element_id] = element_cours_dict[element_id]["titreElement"]
        return element_by_type_dict

    def getIndicateursGeneralitesView(self):
        # LOG.info("----- getIndicateursGeneralitesView -----")
        thead_th_list = [{"data-sort": "public",
                          "th_title":  "les consultations par public",
                          "th_text":   "Public"},
                         {"data-sort": "nb_cons_month_before",
                          "th_title":  "les consultations du mois précédent",
                          "th_text":   "Mois précédent"},
                         {"data-sort": "nb_cons_month",
                          "th_title":  "les consultations du mois courant",
                          "th_text":   "Mois courant"},
                         {"data-sort": "nb_cons_year",
                          "th_title":  "les consultations sur l'année en cours",
                          "th_text":   "Année en cours"}]

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
        element_cours = self.context.getElementCours().values()
        for element in element_cours:
            type_element = element["typeElement"]
            if type_element in ["File", "Image", "Page"]:
                type_element = "Fichiers"
            if type_element in ["Lien web", "Lecteur exportable", "Ressource bibliographique", "Catalogue BU", "Video", "VOD"]:
                type_element = "Externes"
            if type_element == "Presentations sonorisees":
                type_element = "Presentations"
            nb_element_by_type[type_element] += 1

        graph = ""
        requete = self.context.getConsultationByCoursByUniversityYearByDate(None, False, False).all()
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
        #requete2 = self.context.getFrequentationByCoursByUniversityYearByDate("Etudiant").all()
        # LOG.info(requete2)
        if requete2:
            requete_dict = dict(requete2)
            frequentation_graph = self.context.genererFrequentationGraph(requete_dict)
            # LOG.info(frequentation_graph)

        return {"macro":               "indicateurs_generalite",
                "created":             jalon_utils.getLocaleDate(self.context.created(), "%d/%m/%Y à %H:%M"),
                "modified":            jalon_utils.getLocaleDate(self.context.modified(), "%d/%m/%Y à %H:%M"),
                "thead_th_list":       thead_th_list,
                "nb_element_by_type":  nb_element_by_type,
                "graph":               graph,
                "frequentation_graph": frequentation_graph}

        """
        return {"macro":               "indicateurs_generalite",
                "created":             jalon_utils.getLocaleDate(self.context.created(), "%d/%m/%Y à %H:%M"),
                "modified":            jalon_utils.getLocaleDate(self.context.modified(), "%d/%m/%Y à %H:%M"),
                "thead_th_list":       thead_th_list,
                "nb_element_by_type":  nb_element_by_type,
                "cours_consultation":  self.context.getConsultation(),
                "graph":               graph,
                "frequentation_graph": frequentation_graph}
        """

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
                     "link_url":  "%s/cours_indicateurs_view?onglet=2&box=1" % cours_url,
                     "icon":      "fa-files-o",
                     "link_text": "Fichiers"},
                    {"css_class": "button radius%s" % (" selected" if box == "2" else " off"),
                     "link_url":  "%s/cours_indicateurs_view?onglet=2&box=2" % cours_url,
                     "icon":      "fa-microphone",
                     "link_text": "Présentations sonorisées"},
                    {"css_class": "button radius%s" % (" selected" if box == "3" else " off"),
                     "link_url":  "%s/cours_indicateurs_view?onglet=2&box=3" % cours_url,
                     "icon":      "fa-external-link",
                     "link_text": "Ressources externes"},
                    {"css_class": "button radius%s" % (" selected" if box == "4" else " off"),
                     "link_url":  "%s/cours_indicateurs_view?onglet=2&box=4" % cours_url,
                     "icon":      "fa-headphones",
                     "link_text": "Webconférences"},
                    {"css_class": "button radius%s" % (" selected" if box == "5" else " off"),
                     "link_url":  "%s/cours_indicateurs_view?onglet=2&box=5" % cours_url,
                     "icon":      "fa-youtube-play",
                     "link_text": "Vidéos"},
                    {"css_class": "button radius%s" % (" selected" if box == "6" else " off"),
                     "link_url":  "%s/cours_indicateurs_view?onglet=2&box=6" % cours_url,
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
            indicateurs_ressources_view = {"macro":                 "indicateurs_ressources",
                                           "box_list":              box_list,
                                           "second_macro":          "display_all_ressources",
                                           "thead_th_list":         thead_th_list,
                                           "elements_consultation": elements_consultation,
                                           "box_url":               "%s/cours_indicateurs_view?onglet=2&box=%s" % (self.context.absolute_url(), box)}
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
                                           "element_title":         self.context.getElementCours(element_id)["titreElement"],
                                           "box_list":              box_list,
                                           "second_macro":          "display_ressource",
                                           "thead_th_list":         thead_th_list,
                                           "elements_consultation": self.context.getConsultationByElementByCours(element_id),
                                           "graph":                 graph,
                                           "box_url":               "%s/cours_indicateurs_view?onglet=2&box=%s" % (self.context.absolute_url(), box)}
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
                     "link_url":  "%s/cours_indicateurs_view?onglet=3&box=1" % cours_url,
                     "icon":      "fa-inbox",
                     "link_text": "Boite de dépôts"},
                    {"css_class": "button radius%s" % (" selected" if box == "2" else " off"),
                     "link_url":  "%s/cours_indicateurs_view?onglet=3&box=2" % cours_url,
                     "icon":      "fa-gamepad",
                     "link_text": "Entrainement WIMS"},
                    {"css_class": "button radius%s" % (" selected" if box == "3" else " off"),
                     "link_url":  "%s/cours_indicateurs_view?onglet=3&box=3" % cours_url,
                     "icon":      "fa-graduation-cap",
                     "link_text": "Examen WIMS"},
                    {"css_class": "button radius%s" % (" selected" if box == "4" else " off"),
                     "link_url":  "%s/cours_indicateurs_view?onglet=3&box=4" % cours_url,
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
                                     "th_title":  "le titre du fichiers",
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
                                          "box_url":               "%s/cours_indicateurs_view?onglet=3&box=%s" % (self.context.absolute_url(), box)}
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
                                          "element_title":         self.context.getElementCours(element_id)["titreElement"],
                                          "box_list":              box_list,
                                          "second_macro":          "display_ressource",
                                          "thead_th_list":         thead_th_list,
                                          "elements_consultation": self.context.getConsultationByElementByCours(element_id),
                                          "graph":                 graph,
                                          "box_url":               "%s/cours_indicateurs_view?onglet=3&box=%s" % (self.context.absolute_url(), box)}
        return indicateurs_activites_view

    def __call__(self):
        # LOG.info("----- Call -----")
        # à faire tester pour redirection si utilisateur n'a pas le droit d'afficher la page.
        return self.template()
