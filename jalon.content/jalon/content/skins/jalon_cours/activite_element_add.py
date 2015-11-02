## Controller Python Script "activite_element_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Ajoute un élément une activité
##
context=context
request = context.REQUEST
dicoParam = {}

affElement = ""
if "attacher_afficher" in request.form and request.form["attacher_afficher"] == "1":
    affElement = DateTime()

redirection = context.absolute_url()
if request.form["espace"] != "Exercices Wims":
    redirection = "%s?menu=sujets" % context.absolute_url()
if request.form.has_key("paths"):
    for element in request.form["paths"]:
        param = element.split("*-*")
        if param[1] == "Catalogue BU":
            context.tagBU("add", param[0])
        retour = context.ajouterElement(param[0], param[1], param[2], param[3], affElement)
        if retour:
            # Si l'ajout s'est mal passé, on affiche un message d'erreur a l'utilisateur.
            redirection = "%s/?message=wims_bad_rep&err_desc=%s" % (redirection,retour["message"])

return context.REQUEST.RESPONSE.redirect(redirection)
