##Python Script "gerer_cours_podcast"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.setCoursUser(context.REQUEST.form)
context.REQUEST.RESPONSE.redirect("%s/@@jalon-podcast?message=1" % context.aq_parent.absolute_url())
