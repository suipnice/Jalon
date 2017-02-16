# -*- coding: utf-8 -*-
# Controller Python Script "add_tags_objects_script"
# bind container=container
# bind context=context
# bind namespace=
# bind script=script
# bind subpath=traverse_subpath
# parameters=
# title=
##

try:
    tags_list = tuple(context.REQUEST.form["listeTag"])
except:
    tags_list = ()

for path in context.REQUEST.form["paths"]:
    #obj = getattr(home, path.split("/")[-1])
    obj = context.restrictedTraverse(path)
    subjects = list(obj.Subject())
    for tag in tags_list:
        if not tag in subjects: subjects.append(tag)
    obj.setSubject(tuple(subjects))
    obj.reindexObject()

if context.REQUEST.HTTP_X_REQUESTED_WITH != 'XMLHttpRequest':
    context.REQUEST.RESPONSE.redirect(context.absolute_url())
else:
    return context.restrictedTraverse("mes_ressources/%s" % context.getId())()
