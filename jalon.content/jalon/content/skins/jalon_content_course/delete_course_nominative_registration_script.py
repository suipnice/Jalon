##Python Script "delete_course_nominative_registration_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##


form = context.REQUEST.form
nominative_registration_list = []
if form.has_key("etu_groupe"):
    nominative_registration_list = form["etu_groupe"]
context.deleteNominativeRegistration(nominative_registration_list)

context.REQUEST.RESPONSE.redirect(context.absolute_url())