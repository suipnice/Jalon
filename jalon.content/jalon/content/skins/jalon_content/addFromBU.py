## Controller Python Script "logged_in"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFCore.utils import getToolByName

REQUEST = context.REQUEST
redirection = context.absolute_url()

membership_tool = getToolByName(context, 'portal_membership')
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
else:
    member = membership_tool.getAuthenticatedMember()

    if not hasattr(context.Members, member.getId()):
        context.Members.invokeFactory(type_name='JalonFolder', id=member.getId())
        home = getattr(context.Members, member.getId())
        home.addSubJalonFolder(member.getId())

    if not hasattr(context.cours, member.getId()):
        context.cours.invokeFactory(type_name='JalonFolder', id=member.getId())
        cours = getattr(context.cours, member.getId())
        cours.setTitle("Mes cours")
        cours.setPortlets()

    if REQUEST.has_key("rid"):
        rep = getattr(getattr(context.Members, member.getId()), "Externes")
        idobj = rep.invokeFactory(type_name='JalonRessourceExterne', id="Externe-%s-%s-%s" % (member.getId(), REQUEST["rid"], DateTime().strftime("%Y%m%d%H%M%S")))
        obj = getattr(rep, idobj)
        obj.majCatalogueBU(REQUEST["rid"])
        redirection = rep.absolute_url()

    membership_tool.loginUser(REQUEST)

REQUEST.RESPONSE.redirect(redirection)
