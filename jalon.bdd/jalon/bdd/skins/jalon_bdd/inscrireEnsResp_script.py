##Python Script "inscrireEnsResp_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=inscrireEnsResp_script
##

form = context.REQUEST.form
context.inscrireEnsResp(form)
context.REQUEST.RESPONSE.redirect("%s/@@jalon-bdd?gestion=gestion_bdd" % context.absolute_url())
