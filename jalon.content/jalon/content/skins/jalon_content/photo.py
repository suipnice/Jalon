## Controller Python Script "photo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=login=None
##title=
##

login = context.REQUEST["login"]
return context.getPhotoTrombi(login)