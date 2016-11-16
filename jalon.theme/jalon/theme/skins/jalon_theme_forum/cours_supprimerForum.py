## Controller Python Script "cours_supprimerForum"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

if context.REQUEST.form["formulaire"] == "supprimer-tous-forum":
    objectIds = [forum.getId() for forum in context.objectValues()]
    for idDelete in context.objectIds():
        context.manage_delObjects(objectIds)
    context.reindexObject()
    redirection = context.absolute_url()
else:
    forum = context.aq_parent
    forum.manage_delObjects([context.getId()])
    redirection = forum.absolute_url()
    if context.portal_type == "PloneboardComment":
        if len(forum.objectIds()) == 0:
            forum.aq_parent.manage_delObjects([forum.getId()])
            forum.aq_parent.reindexObject()
            redirection = forum.aq_parent.absolute_url()
    forum.reindexObject()

context.REQUEST.RESPONSE.redirect(redirection)