##Python Script "add_course_training_offer_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##


form = context.REQUEST.form
if form.has_key("username"):
    context.addNominativeRegistration(form["username"].split(","))

context.REQUEST.RESPONSE.redirect(context.absolute_url())