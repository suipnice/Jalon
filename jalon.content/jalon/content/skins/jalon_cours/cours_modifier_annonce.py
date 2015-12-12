## Controller Python Script "cours_modifier_annonce"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

redirection = "../.."
request = context.REQUEST
publicsElement = []
if request.form.has_key("publicsElement"):
    publicsElement = request.form["publicsElement"]
context.setProperties({"Title" : request.form["title"]
                      ,"Description" : request.form["description"]
                      ,"Publics" : publicsElement})
if request.form.has_key("mailAnnonce"):
    context.envoyerAnnonce()
#if request.form.has_key("redirection"): redirection = "../../cours_lister?lister=%s" % (request.form["redirection"])
if request.form.has_key("redirection"):
    redirection = "../../cours_lister_annonces"
request.RESPONSE.redirect(redirection)