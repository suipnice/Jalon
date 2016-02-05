# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.common import ViewletBase

from jalon.content.content import jalon_encode


class JalonAnalytics(ViewletBase):
    """Class pour le first_page"""

    codeDeb = ["<script type='text/javascript'>"]
    codeDeb.append("var _gaq = _gaq || [];")
    codeDeb.append("_gaq.push(['_setAccount', '*id_account*']);")
    codeDeb.append("_gaq.push(['_setDomainName', '*id_domain*']);")
    codeDeb.append("_gaq.push(['_trackPageview']);")

    codeFin = [""]
    codeFin.append("(function() {")
    codeFin.append("  var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;")
    codeFin.append("  ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';")
    codeFin.append("  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);")
    codeFin.append("})();")
    codeFin.append("")
    codeFin.append("</script>")

    def __init__(self, *args, **kwargs):
        super(JalonAnalytics, self).__init__(*args, **kwargs)

    def isAnonyme(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.anonymous()

    def googleAnalytics(self):
        portal_jalon_properties = getToolByName(self, "portal_jalon_properties")
        ga_properties = portal_jalon_properties.getPropertiesGA()
        if not ga_properties["activer_ga"]:
            return ""
        code = self.codeDeb[:]
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        authMember = portal.portal_membership.getAuthenticatedMember()

        code[2] = code[2].replace("*id_account*", ga_properties["ga_id_account"])
        code[3] = code[3].replace("*id_domain*", ga_properties["ga_id_domain"])

        variable = []
        if not (authMember.has_role("Anonymous") or authMember.has_role("Manager")):
            roles = authMember.getRoles()
            try:
                roles.remove("Member")
            except:
                pass
            try:
                roles.remove("Authenticated")
            except:
                pass
            variable.append("_gaq.push(['_setCustomVar',")
            variable.append("           1,")
            variable.append("           'User Type',")
            #Si roles[0] ne fonctionne pas, c'est certainement que le ldap n'est pas bien configuré dans acl_users
            variable.append("           '%s'," % roles[0])
            variable.append("           1")
            variable.append("           ]);")
            variable.append("_gaq.push(['_setCustomVar',")
            variable.append("           2,")
            variable.append("           'User Id',")
            variable.append("           '%s'," % jalon_encode.encodeTexte(ga_properties["ga_cryptage"], authMember.getId()))
            variable.append("           1")
            variable.append("           ]);")
        if self.context.Type() == "Jalon Cours":
            variable.append("_gaq.push(['_setCustomVar',")
            variable.append("           3,")
            variable.append("           'Id Cours',")
            variable.append("           '%s'," % self.context.getId())
            variable.append("           3")
            variable.append("           ]);")
        if variable:
            code.extend(variable)

        code.extend(self.codeFin)
        return "\n".join(code)
