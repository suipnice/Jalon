## Script (Python) "mail_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Mail a user's password
##
from Products.CMFPlone import PloneMessageFactory as pmf
from AccessControl import Unauthorized

REQUEST = context.REQUEST
try:
    response = context.portal_registration.mailPassword(REQUEST.get('userid'), REQUEST)
    redirection = "mail_password_confirm"
except ValueError, e:
    try:
        msg = pmf(str(e))
    except Unauthorized:
        # If we are not allowed to tell the user, what is wrong, he
        # should get an error message and contact the admins
        raise e
    context.plone_utils.addPortalMessage(msg)
    response = context.mail_password_form()
    redirection = "mail_password_form"
return REQUEST.RESPONSE.redirect("%s/%s" % (context.absolute_url(), redirection))