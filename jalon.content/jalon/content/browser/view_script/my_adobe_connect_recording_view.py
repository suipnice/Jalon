# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter

from urlparse import urlparse

from my_space_view import MySpaceView
from jalon.content import contentMessageFactory as _

import random
import string

from logging import getLogger
LOG = getLogger('[MyAdobeConnectRecordingView]')


class MyAdobeConnectRecordingView(MySpaceView):
    """ Class View du fichier my_adobe_connect_recording_view.pt
    """

    def __init__(self, context, request):
        # LOG.info("----- Init -----")
        MySpaceView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.folder_dict = {"mes_presentations_sonorisees": "Sonorisation",
                            "mes_webconferences":           "Webconference"}

    def getBreadcrumbs(self):
        return [{"title": _(u"Mes ressources"),
                 "icon":  "fa fa-folder-open",
                 "link":  self.context.aq_parent.absolute_url()},
                {"title": _(u"Mes présentations sonorisées"),
                 "icon":  "fa fa-microphone",
                 "link":  self.context.absolute_url()}]

    def getMyAdobeConnectRecordingView(self, user):
        # LOG.info("----- getMyAdobeConnectRecordingView -----")
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        portal_connect = portal.portal_connect

        user_id = user.getId()
        context_id = self.context.getId()
        folder_id = self.folder_dict[context_id]
        folder = getattr(getattr(portal.Members, user_id), folder_id)
        # LOG.info(folder)
        adobe_connect_session = self.getSessionConnect(user, folder, portal_connect)
        adobe_connect_reunion = self.getAdobeConnectReunion(user, folder, portal_connect)

        item_adder_p = adobe_connect_reunion["adobe_connect_reunion_link"]
        item_adder_name = "Se connecter à votre salle virtuelle"
        if context_id == "mes_presentations_sonorisees":
            item_adder_p = False
            item_adder_name = "Créer une présentation sonorisée"

        item_adder = {"item_adder_link": "%s?session=%s" % (adobe_connect_reunion["adobe_connect_reunion_link"], adobe_connect_session),
                      "item_adder_name": item_adder_name,
                      "item_adder_p":    item_adder_p}

        selected_tags_list = folder.getSelectedTags().split(",")

        tags = self.getTags(folder, selected_tags_list)
        tags_dict = tags["tags_dict"]
        tags_list = tags["tags_list"]

        my_adobe_connect_recording_list = self.getMyAdobeConnectRecordingList(folder, adobe_connect_reunion["adobe_connect_reunion_id"], selected_tags_list, portal_connect)

        one_and_selected_tag = self.getOneAndSelectedTag(my_adobe_connect_recording_list, selected_tags_list, tags_dict)

        no_items_strong = "Il n'y a aucune webconférence dans votre espace."
        no_items_button = "Pour en ajouter, connectez vous à votre salle virtuelle en cliquant sur la barre ci-dessus."
        if one_and_selected_tag["is_no_items"] and context_id == "mes_presentations_sonorisees":
            no_items_strong = "Il n'y a aucune présentation sonorisée dans votre espace."
            no_items_button = "Pour en ajouter, cliquez sur la barre « Créer une présentation sonorisée » ci-dessus."

        nb_display_items = len(my_adobe_connect_recording_list)
        nb_items = len(folder.objectIds())

        return {"adobe_connect_session": adobe_connect_session,
                "adobe_connect_reunion": adobe_connect_reunion,
                "item_adder":            item_adder,
                "tags_list":             tags_list,
                "is_no_items":           one_and_selected_tag["is_no_items"],
                "no_items_strong":       no_items_strong,
                "no_items_button":       no_items_button,
                "is_one_tag":            one_and_selected_tag["is_one_tag"],
                "one_tag":               one_and_selected_tag["one_tag"],
                "is_selected_tags":      one_and_selected_tag["is_selected_tags"],
                "my_items_list":         my_adobe_connect_recording_list,
                "nb_display_items":      nb_display_items,
                "nb_items":              nb_items,
                "folder_path":           "/".join(folder.getPhysicalPath()),
                "folder_link":           folder.absolute_url()}

    def getSessionConnect(self, user, folder, portal_connect):
        # LOG.info("----- getSessionConnect -----")
        user_id = user.getId()
        user_connect_password = folder.getComplement()
        # LOG.info(user_connect_password)
        portal_connect.connexion()
        if not user_connect_password:
            # LOG.info("***** not user_connect_password")
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
            # LOG.info("***** user_connect_password ok")
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
        # LOG.info("----- getAdobeConnectReunion -----")
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

    def getMyAdobeConnectRecordingList(self, folder, adobe_connect_reunion_id, selected_tags_list, portal_connect):
        # LOG.info("----- getMyAdobeConnectRecordingList -----")
        if (not selected_tags_list) or selected_tags_list == ["last"]:
            reindex = False
            jalon_recording_list = folder.objectIds()
            adobe_connect_recording_list = portal_connect.rechercherEnregistrements({'id': adobe_connect_reunion_id})
            for recording in adobe_connect_recording_list:
                if not recording["id"] in jalon_recording_list:
                    recording_id = folder.invokeFactory(type_name='JalonConnect', id=recording["id"])
                    recording_object = getattr(folder, recording_id)
                    recording_object.setProperties({"Title":     recording["title"],
                                                    "DateAjout": str(recording["created"]),
                                                    "DateUS":    recording["dateUS"],
                                                    "Duree":     recording["duration"],
                                                    "UrlEnr":    recording["url"]})
                    recording_object.reindexObject()
                    reindex = True
            if reindex:
                folder.reindexObject()

        content_filter = {"portal_type": ["JalonConnect"]}
        return self.getItemsList(folder, selected_tags_list, content_filter)

    def isSameServer(self, url1, url2):
        u"""Renvoit TRUE si le serveur de l'url "url1" est identique à celui de l'URL "url2"."""
        server1 = urlparse(url1)
        server2 = urlparse(url2)
        return server1.netloc == server2.netloc
