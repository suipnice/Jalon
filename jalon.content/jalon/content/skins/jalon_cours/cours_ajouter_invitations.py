##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFPlone import PloneMessageFactory as _

code = context.addInvitationsEmail(context.REQUEST)

HTTP_X_REQUESTED_WITH = False
if context.REQUEST.HTTP_X_REQUESTED_WITH == 'XMLHttpRequest':
    HTTP_X_REQUESTED_WITH = True

if not HTTP_X_REQUESTED_WITH:
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.absolute_url()