## Script (Python) "getTopBar"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=portal_url, user
##title=
##

SESSION = context.REQUEST.SESSION
if SESSION.get("topBar", None):
    return SESSION["topBar"]

try:
    return context.getJalonMenu(portal_url, user, context.REQUEST)
except:
    return context.etudiants.getJalonMenu(portal_url, user, context.REQUEST)