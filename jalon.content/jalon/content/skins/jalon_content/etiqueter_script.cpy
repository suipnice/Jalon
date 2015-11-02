## Script (Python) "etiqueter_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=listeTag=[], paths=None
##title=
##

context.REQUEST.set("retour", context.absolute_url())

if not paths:
   if not context.REQUEST.form.has_key("lots"):
      context.setSubject(tuple(listeTag))
      context.reindexObject()
      context.REQUEST.set("retour", context.aq_parent.absolute_url())
else:
   for path in paths:
       obj = getattr(context, path.split("/")[-1])
       subjects = list(obj.Subject())
       for tag in listeTag:
           if not tag in subjects: subjects.append(tag)
       obj.setSubject(tuple(subjects))
       obj.reindexObject()

return state.set(status="success")