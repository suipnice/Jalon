## Controller Python Script "deposerfichier_script"
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

#return REQUEST

portal = context.portal_url.getPortalObject()
home = getattr(getattr(portal.Members, form["authMember"]), "Fichiers")
extension = form["file_file"].filename.split(".")[-1]
if extension in ["png", "jpg", "jpeg", "bmp", "svg", "gif"]:
    idobj = home.invokeFactory(type_name='Image', id="Fichier-%s-%s" % (form["authMember"], DateTime().strftime("%Y%m%d%H%M%S")))
    is_image = 1
    type_obj = "Image"
else:
    idobj = home.invokeFactory(type_name='File', id="Fichier-%s-%s" % (form["authMember"], DateTime().strftime("%Y%m%d%H%M%S")))
    is_image = 0
    type_obj = "File"

obj = getattr(home, idobj)
if form["title"]:
    title_file = form["title"]
else:
    title_file = form["file_file"].filename.rsplit('.', 1)[0]
obj.setTitle(title_file)
obj.setDescription(form["description"])

if is_image:
    obj.setImage(form["file_file"])
else:
    obj.setFile(form["file_file"])

affElement = ""
if "attacher_afficher" in form and form["attacher_afficher"] == "1":
    affElement = DateTime()

position = None
if form["position"] != "fin_racine":
    position = form["position"]

context.ajouterElement(idobj, type_obj, title_file, form["authMember"], affElement, position)

context.REQUEST.RESPONSE.redirect(context.absolute_url())
