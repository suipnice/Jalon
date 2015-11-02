# -*- coding: utf-8 -*-
##Python Script "inscrireINDELP"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
redirection = context.absolute_url()

#si l'on souhaite attacher un ELP
context.desinscrireINDELP(form["SESAME_ETU"], form["TYP_ELP_SELECT"])
#if "listeELP" in form:
context.inscrireINDELP(form["SESAME_ETU"], form["TYP_ELP_SELECT"], form["listeELP"])

context.plone_utils.addPortalMessage(u"Inscription mise à jour.", "success") 
context.REQUEST.RESPONSE.redirect("%s/page_inscription?SESAME_ETU=%s&TYP_ELP_SELECT=%s" % (redirection, form["SESAME_ETU"], form["TYP_ELP_SELECT"]))
