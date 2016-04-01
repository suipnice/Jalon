##Python Script "delete_course_training_offer_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
training_offer_list = [] if not form.has_key("elements") else form["elements"]
context.deleteCourseTrainingOffer(training_offer_list)

context.REQUEST.RESPONSE.redirect(context.absolute_url())
