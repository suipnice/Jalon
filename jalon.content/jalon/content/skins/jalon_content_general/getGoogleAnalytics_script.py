## Controller Python Script "getGoogleAnalytics_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=authMember
##title=getGoogleAnalytics_script
##

from Products.CMFCore.utils import getToolByName

# context = context
# authMember = authMember

portal_jalon_properties = getToolByName(context, "portal_jalon_properties")
ga_properties = portal_jalon_properties.getPropertiesGA()
if not ga_properties["activer_ga"]:
    return ""

if authMember.has_role(["Anonymous", "Manager"]):
    return ""

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

code = codeDeb[:]
portal = context.portal_url.getPortalObject()

code[2] = code[2].replace("*id_account*", ga_properties["ga_id_account"])
code[3] = code[3].replace("*id_domain*", ga_properties["ga_id_domain"])

variable = []

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
# Si roles[0] ne fonctionne pas, c'est certainement que le ldap n'est pas bien configuré dans acl_users
variable.append("           '%s'," % roles[0])
variable.append("           1")
variable.append("           ]);")
variable.append("_gaq.push(['_setCustomVar',")
variable.append("           2,")
variable.append("           'User Id',")
variable.append("           '%s'," % portal.mes_etudiants.gaEncodeTexte(ga_properties["ga_cryptage"], authMember.getId()))
variable.append("           1")
variable.append("           ]);")

if context.Type() == "Jalon Cours":
    variable.append("_gaq.push(['_setCustomVar',")
    variable.append("           3,")
    variable.append("           'Id Cours',")
    variable.append("           '%s'," % context.getId())
    variable.append("           3")
    variable.append("           ]);")
if variable:
    code.extend(variable)

code.extend(codeFin)
return "\n".join(code)
