## Controller Python Script "affect_deposit_file_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.affectDepositFile()

context.REQUEST.RESPONSE.redirect("%s?tab=peers&amp;mode_etudiant=false" % context.absolute_url())
