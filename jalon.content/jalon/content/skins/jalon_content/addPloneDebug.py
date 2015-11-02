## Controller Python Script "addPloneDebug"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=debug, sep=0
##title=
##

if sep:
    context.plone_log("---------- %s ----------" % debug)
else:
    context.plone_log("%s" % debug)
