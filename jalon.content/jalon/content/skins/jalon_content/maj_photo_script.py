## Controller Python Script "maj_photo_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

param = {}
REQUEST = context.REQUEST

obj = getattr(context, REQUEST["authMember"], None)
if not obj:
    idobj = context.invokeFactory(type_name='Image', id=REQUEST["authMember"])
    obj = getattr(context, REQUEST["authMember"])
    obj.setTitle("Photo de %s" % idobj)
obj.setImage(REQUEST.form["file_file"])

context.REQUEST.RESPONSE.redirect("%s" % context.absolute_url())