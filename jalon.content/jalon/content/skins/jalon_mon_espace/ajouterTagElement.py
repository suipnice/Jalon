## Controller Python Script "ajouterTagElement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=tag, idElement
##
from Products.PythonScripts.standard import url_quote

obj = getattr(context, context.REQUEST.form["idElement"])

tag = context.REQUEST.form["tag"]
tags = list(obj.Subject())
if not tag in tags:
    tags.append(tag)
    obj.setSubject(tags)
    obj.reindexObject()