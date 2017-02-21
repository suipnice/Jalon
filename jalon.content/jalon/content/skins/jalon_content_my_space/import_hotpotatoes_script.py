# -*- coding: utf-8 -*-
## Controller Python Script "import_hotpotatoes_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# context = context

REQUEST = context.REQUEST
form = context.REQUEST.form

context.importHotPotatoes(form["member_auth"], form["file"])

REQUEST.RESPONSE.redirect(context.absolute_url())
