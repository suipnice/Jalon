## Controller Python Script "cours_retirerElement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

#context = context
request = context.REQUEST
if request.form.has_key("menu") and request.form["menu"] not in ["vide", "glossaire", "bibliographie"]:
    if request.form["menu"] == "exercices":
        context.retirerElement(request.form["idElement"], request.form["menu"], request.form["indexElement"])
    else:
        context.retirerElement(request.form["idElement"], request.form["menu"])
else:
    context.retirerElement(request.form["idElement"])

redirection = context.absolute_url()
if request.form.has_key("orig_template"):
    redirection = request.form["orig_template"]
if request.form.has_key("menu"):
    redirection = "%s?menu=%s" % (redirection, request.form["menu"])
context.REQUEST.RESPONSE.redirect(redirection)
