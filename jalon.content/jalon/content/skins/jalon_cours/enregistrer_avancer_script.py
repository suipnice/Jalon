## Controller Python Script "activer_depot_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
context.setLecture(form["lu"],form["element"], form["authMember"])
context.REQUEST.RESPONSE.redirect("%s?mode_etudiant=true" % context.absolute_url())