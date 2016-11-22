## Controller Python Script "download_deposit_zip_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST

zipfile = context.telechargerDepots(request["HTTP_USER_AGENT"])

request.RESPONSE.setHeader('content-type', 'application/zip')
request.RESPONSE.setHeader('content-length', zipfile["length"])
request.RESPONSE.setHeader('Content-Disposition',' attachment; filename=ArchiveDepot%s.zip' % DateTime().Date())

#request.RESPONSE.redirect("%s/cours_boite_view?menu=depots" % context.absolute_url())

return zipfile["data"]