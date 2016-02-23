# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from my_space_view import MySpaceView

from jalon.content import contentMessageFactory as _

import random
import string
import urllib

from logging import getLogger
LOG = getLogger('[MyFilesView]')


class MyAdobeConnectRecordingView(MySpaceView):
    """ Class View du fichier mes_fichiers_view.pt
    """

    def __init__(self, context, request):
        #LOG.info("----- Init -----")
        MySpaceView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.folder_dict = {"mes_presentations_sonorisees": "Sonorisation",
                            "mes_webconferences":           "Webconference"}

    def getBreadcrumbs(self):
        return [{"title": _(u"Mon espace"),
                 "icon":  "fa fa-home",
                 "link":  self.context.aq_parent.absolute_url()},
                {"title": _(u"Présentations sonorisées"),
                 "icon":  "fa fa-microphone",
                 "link":  self.context.absolute_url()}]

    def getMyAdobeConnectRecordingView(self, user):
        LOG.info("----- getMyAdobeConnectRecordingView -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        portal_connect = portal.portal_connect

        user_id = user.getId()
        folder_id = self.folder_dict[self.context.getId()]
        folder = getattr(getattr(portal.Members, user_id), folder_id)
        adobe_connect_session = self.getSessionConnect(user, folder, portal_connect)
        adobe_connect_reunion = self.getAdobeConnectReunion(user, folder, portal_connect)

        item_adder = {"item_adder_link": "",
                      "item_adder_name": "",
                      "item_adder_p":    ""}

        return {"adobe_connect_session": adobe_connect_session,
                "adobe_connect_reunion": adobe_connect_reunion,
                "item_adder":            item_adder}

    def getSessionConnect(self, user, folder, portal_connect):
        LOG.info("----- getSessionConnect -----")
        user_id = user.getId()
        user_connect_password = folder.getComplement()
        portal_connect.connexion()
        if not user_connect_password:
            LOG.info("***** not user_connect_password")
            self.addAdobeConnectPassword(folder.aq_parent)
            user_email = user.getProperty("email")
            user_fullname = user.getProperty("fullname")
            if not user_fullname:
                user_fullname = user.getProperty("displayName", user_id)
            if not user_email:
                user_email = user.getProperty("mail", "Aucun")
            portal_connect.creerUser({"userid":   user_id,
                                      "password": user_connect_password,
                                      "fullname": user_fullname,
                                      "email":    user_email})
        else:
            LOG.info("***** user_connect_password ok")
            portal_connect.majPasswordUser({"userid":   user_id,
                                            "password": user_connect_password})
        return portal_connect.genererSessionUser({"userid":   user_id,
                                                  "password": user_connect_password})

    def addAdobeConnectPassword(self, folder_parent):
        user_connect_password = ''.join(
            [random.choice(string.ascii_letters + string.digits) for i in range(8)])
        for folder_key in self.folder_dict:
            getattr(folder_parent, self.folder_dict[folder_key]).setComplement(user_connect_password)

    def getAdobeConnectReunion(self, user, folder, portal_connect):
        LOG.info("----- getAdobeConnectReunion -----")
        user_id = user.getId()
        user_connect_password = folder.getComplement()

        adobe_connect_folders = portal_connect.getConnectProperty("dossiers")
        if adobe_connect_folders:
            adobe_connect_model = ""
            for adobe_connect_folder in adobe_connect_folders.split("\n"):
                if folder.getId() in adobe_connect_folder:
                    adobe_connect_model = adobe_connect_folder.split(":")[-1]
                    break
            if adobe_connect_model == "":
                return []
            else:
                adobe_connect_model = adobe_connect_model.replace("\r", "")
        else:
            return {"adobe_connect_reunion_id":   None,
                    "adobe_connect_reunion_link": None}

        adobe_connect_reunions = portal_connect.rechercherReunions({"login": user_id, "modele": adobe_connect_model})
        if not adobe_connect_reunions:
            if user_connect_password:
                user_fullname = user.getProperty("fullname")
                if not user_fullname:
                    user_fullname = user.getProperty("displayName", user_id)
                adobe_connect_reunion = portal_connect.creerReunion({"userid": user_id,
                                                                     "password": user_connect_password,
                                                                     "fullname": user_fullname,
                                                                     "modele": adobe_connect_model,
                                                                     "repertoire": folder.getId()})
            else:
                adobe_connect_reunion = {"adobe_connect_reunion_id":   None,
                                         "adobe_connect_reunion_link": None}
        else:
            adobe_connect_reunion = adobe_connect_reunions[0]

        return {"adobe_connect_reunion_id":   adobe_connect_reunion["id"],
                "adobe_connect_reunion_link": adobe_connect_reunion["url"]}
