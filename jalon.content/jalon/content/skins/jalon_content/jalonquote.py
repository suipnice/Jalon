## Script (Python) "jalonquote"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=url
##title=URL quote
##
from Products.PythonScripts.standard import url_quote

return url_quote(url)
