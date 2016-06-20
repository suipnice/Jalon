##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=format,lang
##title=
##
u"""  Script Python download_wims_scores_script (ex "listingTableur_wims").

Fournit un fichier de notes à télécharger (format CSV ou TSV)

"""

request = context.REQUEST

types = {"csv": "application/CSV", "tsv": 'text/tab-separated-values'}
format = "tsv"
lang = "fr"

#request n'est pas un veritable dico, donc pas de "in"
if request.has_key("format") and request["format"] in types:
    format = request["format"]
if request.has_key("lang"):
    lang = request["lang"].split("-")[0]

request.RESPONSE.setHeader('content-type', types[format])
request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename=liste_notes.%s' % format)

# Ici, context doit etre un jaloncourswims (autoeval / examen )
return context.getNotesTableur(format=format, site_lang=lang)
