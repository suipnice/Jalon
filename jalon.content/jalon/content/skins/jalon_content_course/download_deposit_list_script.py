## Controller Python Script "download_deposit_list_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST

listing = context.telechargerListingDepots(request["HTTP_USER_AGENT"])

request.RESPONSE.setHeader('content-type', 'application/vnd.ms-excel')
request.RESPONSE.setHeader('content-length', listing["length"])
request.RESPONSE.setHeader('Content-Disposition',' attachment; filename=ListingDepot%s.xls' % DateTime().Date())

#request.RESPONSE.redirect("%s/cours_boite_view?menu=depots" % context.absolute_url())

return listing["data"]