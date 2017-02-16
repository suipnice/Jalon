##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=modify_streaming_script
##

form = context.REQUEST.form
context.modifyStreaming(form)

context.REQUEST.RESPONSE.redirect("%s/gestion_mes_ressources?gestion=gestion_wowza&onglet=wowza_extraits" % context.absolute_url())
