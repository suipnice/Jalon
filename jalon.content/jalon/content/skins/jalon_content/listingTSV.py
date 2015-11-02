## Script (Python) "listingTSV"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=cod_etp, cod_vrs_vet
##title=
##

request = context.REQUEST

request.RESPONSE.setHeader('content-type', 'text/tab-separated-values')
request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=Listing_%s.tsv' % cod_etp)

# Ici, context doit etre un jalonfolder
return context.getListeEtudiantsTSV(cod_etp, cod_vrs_vet)
