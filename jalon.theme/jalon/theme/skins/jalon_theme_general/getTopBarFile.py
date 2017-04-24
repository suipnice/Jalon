## Script (Python) "getTopBarFile"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=user
##title=
##

# from logging import getLogger
# LOG = getLogger('[getTopBarFile]')

roles = user.getRoles()
try:
    roles.remove("Authenticated")
except:
    pass

try:
    roles.remove("Member")
except:
    pass

# LOG.info("top_bar_%s" % roles[0].lower())

return "top_bar_%s" % roles[0].lower()
