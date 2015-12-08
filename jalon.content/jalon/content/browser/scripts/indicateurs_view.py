# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
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
                        "icon":      "fa-sitemap",
                        "text":      "Ressources"})
        onglets.append({"href":      "%s/cours_indicateurs_view?onglet=3" % self.context.absolute_url(),
                        "css_class": " selected" if onglet == "3" else "",
                        "icon":      "fa-random",
                        "text":      "Activités"})

        return {"onglets": onglets}

    def test(self):
        if "i" in self.request:
            LOG.info(self.request["i"])

    def __call__(self):
        LOG.info("----- Call -----")
        # à faire tester pour redirection si utilisateur n'a pas le droit d'afficher la page.
        return self.template()
