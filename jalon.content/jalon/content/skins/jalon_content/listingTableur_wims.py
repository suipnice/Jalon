u"""  Script (Python) "listingTableur_wims".

Fournit un fichier de notes à télécharger (format CSV ou TSV)

"""
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=format
##title=
##

request = context.REQUEST

types = {"csv": "application/CSV", "tsv": 'text/tab-separated-values'}
if format not in types:
    format = "tsv"
content = types[format]

request.RESPONSE.setHeader('content-type', content)
request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=liste_notes.%s' % format)

# Ici, context doit etre un jaloncourswims (autoeval / examen )
return context.getNotesTableur(format=format)
