# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from jalon.content.content import jalon_utils

from logging import getLogger
LOG = getLogger('[IndicateursView]')
"""
# Log examples :
LOG.info('info message')
"""


class IndicateursView(BrowserView):
    template = ViewPageTemplateFile("../templates/cours_indicateurs_view.pt")

    def __init__(self, context, request):
        LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def getRequest(self):
        return self.request

    def getPageView(self):
        LOG.info("----- getPageView -----")
        onglet = self.request.get("onglet", "1")
        onglets = []
        onglets.append({"href":      "%s/cours_indicateurs_view?onglet=1" % self.context.absolute_url(),
                        "css_class": " selected" if onglet == "1" else "",
                        "icon":      "fa-info",
                        "text":      "Généralités"})
        onglets.append({"href":      "%s/cours_indicateurs_view?onglet=2" % self.context.absolute_url(),
                        "css_class": " selected" if onglet == "2" else "",
                        "icon":      "fa-files-o",
                        "text":      "Supports pédagogiques"})
        onglets.append({"href":      "%s/cours_indicateurs_view?onglet=3" % self.context.absolute_url(),
                        "css_class": " selected" if onglet == "3" else "",
                        "icon":      "fa-random",
                        "text":      "Activités"})

        return {"onglets": onglets, "onglet_view": self.getOngletView(onglet)}

    def getOngletView(self, onglet):
        LOG.info("----- getOngletView -----")
        if onglet == "1":
            return self.getIndicateursGeneralitesView()
        if onglet == "2":
            return self.getIndicateursRessourcesView()
        if onglet == "3":
            return self.getIndicateursActitivesView()

    def getIndicateursGeneralitesView(self):
        LOG.info("----- getIndicateursGeneralitesView -----")
        nb_element_by_type = {"Titre":          0,
                              "TexteLibre":     0,
                              "Fichiers":       0,
                              "Webconferences": 0,
                              "Externes":       0,
                              "Presentations":  0,
                              "BoiteDepot":     0,
                              "AutoEvaluation": 0,
                              "Examen":         0,
                              "SalleVirtuelle": 0,
                              "Forums":         len(self.context.forum.objectIds()),
                              "Glossaire":      len(self.context.getGlossaire()),
                              "Bibliographie":  len(self.context.getBibliographie())}
        element_cours = self.context.getElementCours().values()
        for element in element_cours:
            type_element = element["typeElement"]
            if type_element in ["File", "Image", "Page"]:
                type_element = "Fichiers"
            if type_element in ["Lien web", "Lecteur exportable", "Ressource bibliographique", "Catalogue BU"]:
                type_element = "Externes"
            if type_element == "Presentations sonorisees":
                type_element = "Presentations"
            nb_element_by_type[type_element] += 1

        requete = self.context.getConsultationByCoursByYearByPublic().all()
        if requete:
            graph = self.context.genererGraphIndicateurs(dict(requete))

        return {"macro":              "indicateurs_generalite",
                "created":            jalon_utils.getLocaleDate(self.context.created(), "%d/%m/%Y à %H:%M"),
                "modified":           jalon_utils.getLocaleDate(self.context.modified(), "%d/%m/%Y à %H:%M"),
                "nb_element_by_type": nb_element_by_type,
                "cours_consultation": self.context.getConsultation(),
                "graph":              graph}

    def getIndicateursRessourcesView(self):
        LOG.info("----- getIndicateursRessourcesView -----")
        return {"macro": "indicateurs_ressources"}

    def getIndicateursActitivesView(self):
        LOG.info("----- getIndicateursActitivesView -----")
        return {"macro": "indicateurs_activites"}

    def __call__(self):
        LOG.info("----- Call -----")
        # à faire tester pour redirection si utilisateur n'a pas le droit d'afficher la page.
        return self.template()
