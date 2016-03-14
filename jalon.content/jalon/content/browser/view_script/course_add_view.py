# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from my_space_view import MySpaceView

from logging import getLogger
LOG = getLogger('[CourseAddView]')


class CourseAddView(MySpaceView):
    """ Class View du fichier course_add_view.pt
    """

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
                        "glossaire":    {"course_add_js": "setTagFilter(True)"},
                        "biblio":       {"course_add_js": "setTagFilter(True)"}}

    def __init__(self, context, request):
        #LOG.info("----- Init -----")
        MySpaceView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.anonymous()

    def getCourseAddView(self, user, course_path):
        #LOG.info("----- getCourseAddView -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        course_add_dict = self._course_add_dict[self.context.getId()]

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
        course_object = getattr(getattr(portal.cours, course_path_list[0]), course_path_list[1])

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
                "course_map":           course_object.getPlanPlat(),
                "is_display_hide":      course_add_dict["is_display_hide"],
                "folder_id":            course_add_dict["folder_id"],
                "course_link":          course_object.absolute_url(),
                "course_add_js":        course_add_dict["course_add_js"]}

    def getCourseMapForm(self, course_path):
        #LOG.info("----- getCourseMapForm -----")
        return self.context.restrictedTraverse("cours/%s/course_map_form" % course_path)()
