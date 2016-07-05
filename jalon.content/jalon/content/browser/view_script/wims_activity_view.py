# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from course_view import CourseView
from jalon.content import contentMessageFactory as _

from logging import getLogger
LOG = getLogger('[WimsActivityView]')


class WimsActivityView(CourseView):
    """Class pour le first_page
    """

    def __init__(self, context, request):
        #LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getBreadcrumbs(self):
        portal = self.context.portal_url.getPortalObject()
        parent = self.context.aq_parent
        return [{"title": _(u"Mes cours"),
                 "icon":  "fa fa-university",
                 "link":  "%s/mes_cours" % portal.absolute_url()},
                {"title": parent.Title(),
                 "icon":  "fa fa-book",
                 "link":  parent.absolute_url()},
                {"title": self.context.Title(),
                 "icon":  "fa fa-gamepad" if self.context.getId().startswith("AutoEvaluation-") else "fa fa-graduation-cap",
                 "link":  self.context.absolute_url()}]

    def getWimsActivityView(self, user, mode_etudiant, tab, is_ajax):
        LOG.info("----- getWimsActivityView (Start) -----")
        user_id = user.getId()
        my_view = {"is_anonymous": self.isAnonymous()}

        my_wims_activity = self.context
        instruction_text = my_wims_activity.Description()
        if instruction_text:
            my_view["instruction_class"] = "panel callout radius"
            my_view["instruction_text"] = instruction_text
        else:
            my_view["instruction_class"] = "panel radius"
            my_view["instruction_text"] = "Consigne non renseignée"

        my_view["wims_activity_id"] = my_wims_activity.getId()
        my_view["wims_activity_link"] = my_wims_activity.absolute_url()
        my_view["is_personnel"] = my_wims_activity.isPersonnel(user, mode_etudiant)
        my_view["mode_etudiant"] = "false" if (not mode_etudiant) and my_view["is_personnel"] else mode_etudiant

        if is_ajax or my_view["is_anonymous"]:
            my_view["came_from"] = "%s/login_form?came_from=%s" % (my_view["wims_activity_link"], my_wims_activity.jalon_quote(my_view["wims_activity_link"])),
            return my_view

        #my_view["wims_activity_instruction"] = {"href":  "%s/edit_wims_activity_instruction_form?tab=%s" % (my_view["wims_activity_link"], tab),
        #                                        "icon":  "fa-pencil",
        #                                        "text":  "Modifier"}

        my_view["wims_activity_visibility"] = my_wims_activity.isAfficherElement(my_wims_activity.getDateAff(), my_wims_activity.getDateMasq())

        my_view["wims_activity_edit"] = []
        if my_view["wims_activity_visibility"]["val"]:
            my_view["wims_activity_edit"].append({"href": "%s/edit_course_item_visibility_form?item_id=%s&amp;tab=%s" % (my_view["wims_activity_link"], my_view["wims_activity_id"], tab),
                                                  "icon": "fa-eye-slash",
                                                  "text": "Masquer"})
        else:
            my_view["wims_activity_edit"].append({"href": "%s/edit_course_item_visibility_form?item_id=%s&amp;tab=%s" % (my_view["wims_activity_link"], my_view["wims_activity_id"], tab),
                                                  "icon": "fa-eye",
                                                  "text": "Afficher"})
        my_view["wims_activity_edit"].append({"href": "%s/edit_wims_activity_form?tab=%s" % (my_view["wims_activity_link"], tab),
                                              "icon": "fa-pencil",
                                              "text": "Titre"})

        my_view["is_personnel_or_wims_activity_visible"] = True if my_view["is_personnel"] or my_view["wims_activity_visibility"]['val'] != 0 else False
        my_view["is_student_and_wims_activity_hidden"] = True if (not my_view["is_personnel"]) and my_view["wims_activity_visibility"]['val'] == 0 else False
        my_view["is_display_mod"] = my_wims_activity.isAuteurs(user.getId())

        my_view["wims_activity_tabs"] = []

        my_view["is_exercices_tab"] = True if tab == "exercices" else False
        my_view["wims_activity_tabs"].append({"href":      "%s?tab=exercices&amp;mode_etudiant=%s" % (my_view["wims_activity_link"], mode_etudiant),
                                              "css_class": " selected" if my_view["is_exercices_tab"] else "",
                                              "icon":      "fa-random",
                                              "text":      "Exercices",
                                              "nb":        my_wims_activity.getNbExercices()})

        my_view["is_documents_tab"] = True if tab == "documents" else False
        my_view["wims_activity_tabs"].append({"href":      "%s?tab=documents&amp;mode_etudiant=%s" % (my_view["wims_activity_link"], mode_etudiant),
                                              "css_class": " selected" if my_view["is_documents_tab"] else "",
                                              "icon":      "fa-upload",
                                              "text":      "Documents enseignants",
                                              "nb":        my_wims_activity.getNbSujets()})
        if my_view["is_documents_tab"]:
            portal = my_wims_activity.portal_url.getPortalObject()
            wims_activity_path = my_wims_activity.getPhysicalPath()
            my_view["documents_add"] = self.getCourseItemAdderMenuList(my_view["wims_activity_link"], "/".join([wims_activity_path[-3], wims_activity_path[-2], wims_activity_path[-1]]), portal)["my_space"]
            my_view["documents_list"] = my_wims_activity.displayDocumentsList(my_view["is_personnel"], portal)

        my_view["is_resultats_tab"] = True if tab == "resultats" else False
        my_view["wims_activity_tabs"].append({"href":      "%s?tab=resultats&amp;mode_etudiant=%s" % (my_view["wims_activity_link"], mode_etudiant),
                                              "css_class": " selected" if my_view["is_resultats_tab"] else "",
                                              "icon":      "fa-trophy",
                                              "text":      "Résultats"})

        LOG.info("----- getWimsActivityView (End) -----")
        return my_view
