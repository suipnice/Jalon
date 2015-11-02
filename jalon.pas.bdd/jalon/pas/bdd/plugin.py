"""Class: BddHelper
"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements

# Pluggable Auth Service
from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin, IRolesPlugin, IUserEnumerationPlugin
from Products.PlonePAS.sheet import MutablePropertySheet

from OFS.Cache import Cacheable


class BddHelper(BasePlugin, Cacheable):

    meta_type = 'bdd Helper'
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    #
    # IPropertiesPlugin implementation
    #
    security.declarePrivate('enumerateUsers')
    def enumerateUsers(self, id=None, login=None, exact_match=False,
                       sort_by=None, max_results=None, **kw):
        """See IUserEnumerationPlugin."""

        portal = self.portal_url.getPortalObject()
        portal_jalon_bdd = portal.portal_jalon_bdd
        individu = portal_jalon_bdd.getIndividuLITE(id)

        if individu is not None:
            return ({'login': id, 'pluginid': self.getId(), 'id': id},)
        return None

    #
    # IPropertiesPlugin implementation
    #
    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """Get property values for a user or group.
        Returns a dictionary of values or a PropertySheet.
        """

        #print "--- getPropertiesForUser ---"
        try:
            username = user.getUserName()
        except:
            username = user
        #print "username : %s" % username
        if request and request.SESSION.get("sheetJalon%s" % username):
            #print "session"
            return request.SESSION.get("sheetJalon%s" % username)
        #print "pas de session"

        data = {}

        portal = self.portal_url.getPortalObject()
        portal_jalon_bdd = portal.portal_jalon_bdd
        individu = portal_jalon_bdd.getIndividuLITE(username)
        #print "APPEL BDD"

        if individu is not None:
            #print "creation session"
            data["fullname"] = "%s %s" % (individu["LIB_PR1_IND"], individu["LIB_NOM_PAT_IND"])
            data["email"] = individu["EMAIL_ETU"]
            data["role"] = individu["TYPE_IND"]

            sheet = MutablePropertySheet(username, **data)
            if request:
                request.SESSION.set("sheetJalon%s" % username, sheet)
            return sheet
        return None

    #
    # IRolesPlugin implementation
    #
    def getRolesForPrincipal(self, principal, request=None):
        #print "--- getRolesForPrincipal ---"
        #print "principal : %s" % principal
        #print request
        roles = ("Anonymous")
        if request and request.SESSION.get("sheetJalon%s" % principal):
            #print "session"
            role = request.SESSION.get("sheetJalon%s" % principal).getProperty("role")
            #print "ROLE : %s" % str(role)
            return ("Authenticated", "Member", str(role))
        """
        else:
            portal = self.portal_url.getPortalObject()
            portal_jalon_bdd = portal.portal_jalon_bdd
            individu = portal_jalon_bdd.getIndividuLITE(principal.getId())
            #print "APPEL BDD"
            if individu:
                return ("Authenticated", "Member", individu["TYPE_IND"])
        """
        return roles

classImplements(BddHelper,
                IRolesPlugin,
                IPropertiesPlugin,
                IUserEnumerationPlugin)

InitializeClass(BddHelper)
