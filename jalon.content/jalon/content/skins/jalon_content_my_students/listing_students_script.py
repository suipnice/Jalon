## Script (Python) "listingEtudiantsXLS"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=cod_etp
##title=
##

request = context.REQUEST

listing = context.getListeEtudiantsXLS(cod_etp)

request.RESPONSE.setHeader('content-type', 'application/vnd.ms-excel')
request.RESPONSE.setHeader('content-length', listing["length"])
request.RESPONSE.setHeader('Content-Disposition',' attachment; filename=Listing%s.xls' % cod_etp)

return listing["data"]