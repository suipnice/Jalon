## Controller Python Script "marquer_element_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.marquerElement(context.REQUEST["element"])

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect("%s?mode_etudiant=true" % context.absolute_url())
else:
    return 1

