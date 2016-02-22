# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from my_space_view import MySpaceView

from jalon.content import contentMessageFactory as _

import urllib

from logging import getLogger
LOG = getLogger('[MyFilesView]')


class MyFilesView(MySpaceView):
    """ Class View du fichier mes_fichiers_view.pt
    """

    def __init__(self, context, request):
        #LOG.info("----- Init -----")
        MySpaceView.__init__(self, context, request)
        self.context = context
        self.request = request

    def getBreadcrumbs(self):
        return [{"title": _(u"Mon espace"),
                 "icon":  "fa fa-home",
                 "link":  self.context.aq_parent.absolute_url()},
                {"title": _(u"Fichiers"),
                 "icon":  "fa fa-files-o",
                 "link":  self.context.absolute_url()}]

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

        is_selected_tags = "remove_tags_objects" if selected_tags_list != ["last"] and len(selected_tags_list) >= 1 else "isnt_selected_tags"
        LOG.info(selected_tags_list)
        LOG.info(is_selected_tags)

        nb_display_files = len(my_files_list)
        nb_files = len(folder.objectIds())

        return {"tags_list":        tags_list,
                "is_no_files":      is_no_files,
                "is_one_tag":       is_one_tag,
                "one_tag":          one_tag,
                "is_selected_tags": is_selected_tags,
                "my_files_list":    my_files_list,
                "nb_display_files": nb_display_files,
                "nb_files":         nb_files,
                "folder_path":      "/".join(folder.getPhysicalPath())}

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
