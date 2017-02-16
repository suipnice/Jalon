## Script (Python) "remove_tags_objects_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

tags_list = context.REQUEST.form["tagsupp"].split(",")

for path in context.REQUEST.form["paths"]:
    #obj = getattr(context, path.split("/")[-1])
    obj = context.restrictedTraverse(path)
    subjects = list(obj.Subject())
    for tag in tags_list:
        if tag in subjects: subjects.remove(tag)
        if context.jalon_quote(tag) in subjects: subjects.remove(context.jalon_quote(tag))
    obj.setSubject(tuple(subjects))
    obj.reindexObject()

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.restrictedTraverse("mes_ressources/%s" % context.getId())()
