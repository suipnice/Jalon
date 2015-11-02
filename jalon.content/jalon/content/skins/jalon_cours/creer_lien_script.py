## Controller Python Script "creer_lien_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
form = REQUEST.form

portal = context.portal_url.getPortalObject()
home = getattr(getattr(portal.Members, form["authMember"]), "Externes")

idobj = home.invokeFactory(type_name='JalonRessourceExterne', id="Externe-%s-%s" % (form["authMember"], DateTime().strftime("%Y%m%d%H%M%S")))

obj = getattr(home, idobj)

properties = {"Title"                : REQUEST["title"]
             ,"TypeRessourceExterne" : ""
             ,"Description"          : REQUEST["description"]}

if "iframe" in form["lien"] or "embed" in form["lien"]:
    type_obj = "Lecteur exportable"
    properties["TypeRessourceExterne"] = "Lecteur exportable"
    properties["Lecteur"] = form["lien"]
else:
    type_obj = "Lien web"
    properties["TypeRessourceExterne"] = "Lien web"
    properties["Urlbiblio"] = form["lien"]

obj.setProperties(properties)

affElement = ""
if "attacher_afficher" in form and form["attacher_afficher"] == "1":
    affElement = DateTime()

position = None
if form["position"] != "fin_racine":
    position = form["position"]

context.ajouterElement(idobj, type_obj, form["title"], form["authMember"], affElement, position)

context.REQUEST.RESPONSE.redirect(context.absolute_url())