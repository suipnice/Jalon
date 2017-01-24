## Controller Python Script "download_peers_results_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST

listing = context.downloadPeersResults(request["HTTP_USER_AGENT"])

request.RESPONSE.setHeader('content-type', 'application/vnd.ms-excel')
request.RESPONSE.setHeader('content-length', listing["length"])
request.RESPONSE.setHeader('Content-Disposition',' attachment; filename=ParLesPairs%s.xls' % DateTime().Date())

#request.RESPONSE.redirect("%s/cours_boite_view?menu=depots" % context.absolute_url())

return listing["data"]