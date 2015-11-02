# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter

from plone.app.discussion.browser.comments import CommentsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


from jalon.content.content import jalon_utils

import ldap


class MyComments(CommentsViewlet):
    index = ViewPageTemplateFile('../templates/comments.pt')

    def __init__(self, *args, **kwargs):
        super(MyComments, self).__init__(*args, **kwargs)

    def get_commenter_portrait(self, username=None):
        return jalon_utils.getPhotoTrombi(username)

    def getInfosAuteur(self, dico, username):
        if not username in dico:
            portal_state = getMultiAdapter((self.context, self.request),
                                           name=u'plone_portal_state')
            portal = portal_state.portal()

            ldapplugin = getattr(getattr(portal.acl_users, "ldap-plugin-etu"), "acl_users")
            user = ldapplugin._binduid
            password = ldapplugin._bindpwd
            infosServer = ldapplugin.getServers()

            try:
                server = "%s://%s:%s" % (infosServer[0]["protocol"], infosServer[0]["host"], infosServer[0]["port"])
                ldapserver = ldap.initialize(server)
                ldapserver.simple_bind_s(user, password)
            except:
                server = "%s://%s:%s" % (infosServer[1]["protocol"], infosServer[1]["host"], infosServer[1]["port"])
                ldapserver = ldap.initialize(server)
                ldapserver.simple_bind_s(user, password)

            ldapfilter = "(&(cptcree=1)(%s=%s))" % (ldapplugin._login_attr, username)
            result = ldapserver.search_s(ldapplugin.users_base, ldap.SCOPE_SUBTREE, ldapfilter, None)
            dico[username] = {"cn": username, "src": "defaultUser.gif"}
            if result:
                dico[username] = {"cn": result[0][1].get("cn", [username])[0].capitalize(), "src": "../photo?login=%s" % result[0][1].get("supannEtuId", [username])[0]}
                ldapserver.unbind_s()
            else:
                ldapplugin = getattr(getattr(portal.acl_users, "ldap-plugin"), "acl_users")
                ldapfilter = "(&(%s=%s))" % (ldapplugin._login_attr, username)
                result = ldapserver.search_s(ldapplugin.users_base, ldap.SCOPE_SUBTREE, ldapfilter, None)
                if result:
                    dico[username]["cn"] = result[0][1].get("cn", [username])[0].capitalize()

                ldapserver.unbind_s()
        return dico
