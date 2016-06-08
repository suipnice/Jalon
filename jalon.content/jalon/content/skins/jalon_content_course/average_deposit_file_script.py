## Controller Python Script "average_deposit_file_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.setAveragePeer()
return "OK"

#return context.getAveragePeer()