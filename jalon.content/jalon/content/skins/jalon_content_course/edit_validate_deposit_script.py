## Controller Python Script "edit_validate_deposit_form"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST
context.setProperties({"Actif": form["actif"]})

context.REQUEST.RESPONSE.redirect("%s?mode_etudiant=true" % context.aq_parent.absolute_url())
