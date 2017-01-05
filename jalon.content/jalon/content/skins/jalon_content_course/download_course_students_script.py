## Controller Python Script "download_course_students_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST

listing = context.telechargerListingParticipants()

if listing:
    request.RESPONSE.setHeader('content-type', 'application/vnd.ms-excel')
    request.RESPONSE.setHeader('content-length', listing["length"])
    request.RESPONSE.setHeader('Content-Disposition',' attachment; filename=ListingParticipants%s.xls' % DateTime().Date())
    return listing["data"]
else:
    request.RESPONSE.redirect(context.absolute_url())