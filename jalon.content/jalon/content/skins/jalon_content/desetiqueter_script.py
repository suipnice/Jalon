## Script (Python) "desetiqueter_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
listeTag = request.form["tagsupp"].split(",")

if request.form.has_key("paths"):
   for path in request.form["paths"]:
       obj = getattr(context, path.split("/")[-1])
       subjects = list(obj.Subject())
       for tag in listeTag:
           if tag in subjects: subjects.remove(tag)
           if context.jalon_quote(tag) in subjects: subjects.remove(context.jalon_quote(tag))
       obj.setSubject(tuple(subjects))
       obj.reindexObject()

return context.REQUEST.RESPONSE.redirect(context.absolute_url())