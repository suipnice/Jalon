## Controller Python Script "cours_element_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute un élément ou un sous-element au cours
##

request = context.REQUEST
dicoParam = {}
#context.plone_log("----- cours_element_add (Start) -----")
affElement = ""
if "attacher_afficher" in request.form and request.form["attacher_afficher"] == "1":
    affElement = DateTime()

display_in_plan = True if "display_in_plan" in request.form and request.form["display_in_plan"] == "1" else False

redirection = context.absolute_url()
if request.form.has_key("page"):
   redirection = "%s/%s" % (redirection, request.form["page"])
   if "?" in request.form["page"]:
      paramUrl = request.form["page"].split("?")[-1]
      for paramb in paramUrl.split("&"):
          key, value = paramb.split("=")
          dicoParam[key] = value

position = None
if request.form.has_key("position") and request.form["position"] != "fin_racine":
    position = request.form["position"]

#cas de l'ajout d'un element
if request.form.has_key("paths"):
    for element in request.form["paths"]:
        param = element.split("*-*")
        if param[1] == "Catalogue BU":
            context.tagBU("add", param[0])
        if dicoParam.has_key("menu"):
            retour = context.ajouterElement(dicoParam["menu"], param[0], param[1], param[2], param[3], affElement)
            if retour:
                # Si l'ajout s'est mal passé, on affiche un message d'erreur a l'utilisateur.
                redirection = "%s&message=wims_bad_rep&err_desc=%s" % (redirection,retour["message"])
        elif request.form.has_key("espace") and request.form["espace"] == "Bibliographie":
            context.ajouterElement(param[0], "%s*-*%s" % ("biblio", param[1]), param[2], param[3])
        else:
            context.ajouterElement(param[0], param[1], param[2], param[3], affElement, position, display_in_plan)

HTTP_X_REQUESTED_WITH = False

# cas de l'ajout d'une activité
if request.form.has_key("type"):
    mailAnnonce = None
    publicsElement = ()
    if request.form["type"] == "Annonce":
        if request.form.has_key("publicsElement"):
            publicsElement = tuple(request.form["publicsElement"])
        if request.form.has_key("mailAnnonce"):
            mailAnnonce = tuple(request.form["mailAnnonce"])

    idactivite = context.creerSousObjet(request.form["type"], request.form["title"], request.form["description"], request.form["authMember"], publicsElement, mailAnnonce)

    if not request.form["type"] in ["Annonce", "Forum"]:
        context.ajouterElement(idactivite, request.form["type"], request.form["title"], request.form["authMember"], "", position)
    elif context.REQUEST.HTTP_X_REQUESTED_WITH == 'XMLHttpRequest':
        HTTP_X_REQUESTED_WITH = True


#context.plone_log(redirection)
#context.plone_log("----- cours_element_add (End) -----")
if not HTTP_X_REQUESTED_WITH:
    context.REQUEST.RESPONSE.redirect(redirection)
else:
    return redirection

