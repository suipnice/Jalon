##Python Script "delete_course_email_registration_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
email_registration_list = []
if form.has_key("etu_email"):
    email_registration_list = form["etu_email"]
context.deleteEmailRegistration(email_registration_list)

context.REQUEST.RESPONSE.redirect(context.absolute_url())