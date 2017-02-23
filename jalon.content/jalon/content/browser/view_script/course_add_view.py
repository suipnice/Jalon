# -*- coding: utf-8 -*-
"""Vue du template "jalon/theme/browser/view_template/jalon_course/course_add_view.pt"."""
from zope.component import getMultiAdapter
from my_space_view import MySpaceView

from logging import getLogger
LOG = getLogger('[CourseAddView]')


class CourseAddView(MySpaceView):
    """Class View du fichier course_add_view.pt."""

    _course_add_dict = {"mes_fichiers":                 {"folder_id":            "Fichiers",
                                                         "macro_file":           "add_course_files_macro",
                                                         "portal_type":          ["File", "Image", "Document"],
                                                         "course_add_list_icon": "fa fa-files-o",
                                                         "is_display_hide":      True,
                                                         "course_add_js":        "setAttachmentCreator()"},
                        "mes_presentations_sonorisees": {"folder_id":            "Sonorisation",
                                                         "macro_file":           "add_course_adobe_connect_recording_macro",
                                                         "portal_type":          ["JalonConnect"],
                                                         "course_add_list_icon": "fa fa-microphone",
                                                         "is_display_hide":      True,
                                                         "course_add_js":        "setAttachmentCreator()"},
                        "mes_ressources_externes":      {"folder_id":            "Externes",
                                                         "macro_file":           "add_course_external_resources_macro",
                                                         "portal_type":          ["JalonRessourceExterne"],
                                                         "course_add_list_icon": "fa fa-external-link",
                                                         "is_display_hide":      True,
                                                         "course_add_js":        "setAttachmentCreator()"},
                        "mes_termes_glossaire":         {"folder_id":            "Glossaire",
                                                         "macro_file":           "add_course_glossary_term_macro",
                                                         "portal_type":          ["JalonTermeGlossaire"],
                                                         "course_add_list_icon": "fa fa-font",
                                                         "is_display_hide":      False,
                                                         "course_add_js":        "setTagFilter(true)"},
                        "mes_webconferences":           {"folder_id":            "Webconference",
                                                         "macro_file":           "add_course_adobe_connect_recording_macro",
                                                         "portal_type":          ["JalonConnect"],
                                                         "course_add_list_icon": "fa fa-headphones",
                                                         "is_display_hide":      True,
                                                         "course_add_js":        "setAttachmentCreator()"},
                        "mes_videos_pod":               {"folder_id":            "Video",
                                                         "macro_file":           "add_course_pod_videos_macro",
                                                         "portal_type":          ["JalonRessourceExterne"],
                                                         "course_add_list_icon": "fa fa-youtube-play",
                                                         "is_display_hide":      True,
                                                         "course_add_js":        "setAttachmentCreator()"},
                        "mes_exercices_wims":           {"folder_id":            "Wims",
                                                         "macro_file":           "add_wims_activity_exercice_macro",
                                                         "portal_type":          ["JalonExerciceWims"],
                                                         "course_add_list_icon": "fa fa-random",
                                                         "is_display_hide":      False,
                                                         "course_add_js":        "setTagFilter(true)"},
                        "course_bibliography":          {"folder_id":            "Externes",
                                                         "macro_file":           "add_course_bibliography_macro",
                                                         "portal_type":          ["JalonRessourceExterne"],
                                                         "course_add_list_icon": "fa fa-external-link",
                                                         "is_display_hide":      False,
                                                         "course_add_js":        "setTagFilter(true)"}}

    def __init__(self, context, request):
        """initialise CourseAddView."""
        # LOG.info("----- Init -----")
        MySpaceView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        """check if connected user is Anonymous."""
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getCourseAddView(self, user, course_path):
        """Fournit les infos d'ajout d'un element dans le cours."""
        LOG.info("----- getCourseAddView -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        course_add_dict = self._course_add_dict[self.context.getId()]
        LOG.info(self.context.getId())

        folder = getattr(getattr(portal.Members, user.getId()), course_add_dict["folder_id"])
        selected_tags_list = folder.getSelectedTags().split(",")

        tags = self.getTags(folder, selected_tags_list)
        tags_dict = tags["tags_dict"]
        tags_list = tags["tags_list"]

        course_add_list = self.getItemsList(folder, selected_tags_list, {"portal_type": course_add_dict["portal_type"]})

        one_and_selected_tag = self.getOneAndSelectedTag(course_add_list, selected_tags_list, tags_dict)

        nb_display_items = len(course_add_list)
        nb_items = len(folder.objectIds())

        course_path_list = course_path.split("/")
        # LOG.info("***** course_path : %s" % course_path)
        course_object = getattr(getattr(portal.cours, course_path_list[0]), course_path_list[1])

        is_course = True
        course_map_form = ""
        wims_exercice_model_list = ""
        # Cours- = id à partir de 09/2012 ; Cours. = id avant 09/2012
        if course_path_list[-1].startswith("Cours-") or course_path_list[-1].startswith("Cours."):
            if self.context.getId() == "mes_termes_glossaire":
                is_course = False
                course_map = course_object.getGlossaire()
            elif self.context.getId() == "course_bibliography":
                is_course = False
                course_map = course_object.getBibliographie()
            else:
                course_map = course_object.getCourseMapList()
                course_map_form = self.getCourseMapForm(course_path)
            course_add_js = course_add_dict["course_add_js"]
        else:
            is_course = False
            course_object = getattr(course_object, course_path_list[-1])
            if course_add_dict["folder_id"] == "Wims":
                course_map = course_object.getListeExercices()
                wims_exercice_model_list = folder.getModelesWims()
            else:
                course_map = course_object.getDocumentsList()
            course_add_js = "setTagFilter(true)"

        return {"tags_list":            tags_list,
                "is_no_items":          one_and_selected_tag["is_no_items"],
                "is_one_tag":           one_and_selected_tag["is_one_tag"],
                "one_tag":              one_and_selected_tag["one_tag"],
                "is_selected_tags":     one_and_selected_tag["is_selected_tags"],
                "macro_file":           course_add_dict["macro_file"],
                "course_add_list_icon": course_add_dict["course_add_list_icon"],
                "nb_display_items":     nb_display_items,
                "nb_items":             nb_items,
                "course_add_list":      course_add_list,
                "is_course":            is_course,
                "course_map":           course_map,
                "course_map_form":      course_map_form,
                "is_display_hide":      course_add_dict["is_display_hide"],
                "folder_id":            course_add_dict["folder_id"],
                "folder_link":          "%s/mes_ressources/%s" % (portal.absolute_url(), self.context.getId()),
                "course_link":          course_object.absolute_url(),
                "course_add_js":        course_add_js,
                "wims_exercice_model_list": wims_exercice_model_list}

    def getCourseMapForm(self, course_path):
        """redirige vers course_map_form."""
        # LOG.info("----- getCourseMapForm -----")
        return self.context.restrictedTraverse("cours/%s/course_map_form" % course_path)()
