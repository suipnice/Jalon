##Python Script "add_course_email_registration_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# context = context

form = context.REQUEST.form
if form.has_key("invitation"):
    # Cas où on inscrit plusieurs utilisateurs d'un coup
    if "," in form["invitation"]:
        email_registration_list = form["invitation"].split(",")
    else:
        email_registration_list = [form["invitation"]]
    context.addEmailRegistration(email_registration_list)

HTTP_X_REQUESTED_WITH = False
if context.REQUEST.HTTP_X_REQUESTED_WITH == 'XMLHttpRequest':
    HTTP_X_REQUESTED_WITH = True

if not HTTP_X_REQUESTED_WITH:
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.absolute_url()
