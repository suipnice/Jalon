# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter

import urllib

from logging import getLogger
LOG = getLogger('[MesFichiersView]')


class MesFichiersView(BrowserView):
    """ Class View du fichier mes_fichiers_view.pt
    """

    def __init__(self, context, request):
        #LOG.info("----- Init -----")
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def isAnonymous(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.anonymous()

    def getMyFilesView(self, user):
        LOG.info("----- getMyFilesView -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        folder = getattr(portal.Members, user.getId()).Fichiers
        selected_tags_list = folder.getSelectedTags().split(",")

        tags = self.getTags(folder, selected_tags_list)
        tags_dict = tags["tags_dict"]
        tags_list = tags["tags_list"]

        my_files_list = self.getMyFilesList(folder, selected_tags_list)

        is_no_files = False
        if not my_files_list:
            if "last" in selected_tags_list:
                selected_tags_list.remove("last")
            is_no_files = True if len(selected_tags_list) == 0 else False

        one_tag = ""
        is_one_tag = False
        try:
            selected_tags_list.remove("")
        except:
            pass
        if len(selected_tags_list) == 1:
            is_one_tag = True
            one_tag = {"tag_id": urllib.quote(selected_tags_list[-1]),
                       "tag_title": tags_dict[selected_tags_list[-1]]}

        # is_no_files = is_no_tag and not:my_files_list
        nb_display_files = len(my_files_list)
        nb_files = len(folder.objectIds())

        return {"tags_list":        tags_list,
                "is_no_files":      is_no_files,
                "is_one_tag":       is_one_tag,
                "one_tag":          one_tag,
                "my_files_list":    my_files_list,
                "nb_display_files": nb_display_files,
                "nb_files":         nb_files,
                "folder_path":      "/".join(folder.getPhysicalPath())}

    def getTags(self, folder, selected_tags_list):
        tags_dict = {"last": "Les 20 derniers"}
        tags_list = []
        tags = list(folder.Subject())
        tags.sort()
        for tag in tags:
            tags_dict[tag] = tag
            tags_list.append({"tag_id":    urllib.quote(tag),
                              "tag_title": tag,
                              "tag_css":   "filter-button selected" if tag in selected_tags_list else "filter-button unselected"})

        tags_list.insert(0, {"tag_id":    "last",
                             "tag_title": "Les 20 derniers",
                             "tag_css":   "filter-button fixed_filter selected" if "last" in selected_tags_list else "filter-button fixed_filter unselected"})
        return {"tags_dict": tags_dict,
                "tags_list": tags_list}

    # def getContents(self, subject, typeR, authMember, repertoire, categorie=None):
    def getMyFilesList(self, folder, selected_tags_list):
        dico = {"portal_type": ["File", "Image", "Document"]}

        if selected_tags_list and selected_tags_list != ["last"]:
            last = False
            subjects = []
            if "last" in selected_tags_list:
                selected_tags_list.remove("last")
                last = True
            for tag in selected_tags_list:
                subjects.append(urllib.quote(tag))
            if len(subjects) > 1:
                dico['Subject'] = {'query': subjects, 'operator': 'and'}
            else:
                dico['Subject'] = subjects[0]
            if last:
                dico["sort_on"] = "modified"
                dico["sort_order"] = "descending"
                return folder.getFolderContents(contentFilter=dico, batch=True, b_size=20)
            else:
                return folder.getFolderContents(contentFilter=dico)
        elif selected_tags_list == ["last"]:
            dico["sort_on"] = "modified"
            dico["sort_order"] = "descending"
            return folder.getFolderContents(contentFilter=dico, batch=True, b_size=20)
        else:
            dico["sort_on"] = "modified"
            dico["sort_order"] = "descending"
            return folder.getFolderContents(contentFilter=dico)
