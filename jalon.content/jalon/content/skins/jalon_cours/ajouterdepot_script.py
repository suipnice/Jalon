## Controller Python Script "ajouterdepot_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

param = {}
REQUEST = context.REQUEST

idobj = context.invokeFactory(type_name='JalonFile', id="Depot-%s-%s" % (REQUEST["authMember"], DateTime().strftime("%Y%m%d%H%M%S")))
obj = getattr(context, idobj)
param = {"Title":       REQUEST.form["title"],
         "Description": REQUEST.form["description"],
         "File":        REQUEST.form["file_file"]}
obj.setProperties(param)
context.aq_parent.setActuCours({"reference": context.getId(),
                                "code":      "nouveauxdepots"})

comp_etudiants = dict(context.getCompEtudiants())
listeEtu = comp_etudiants.keys()
if not REQUEST["authMember"] in listeEtu:
    comp_etudiants[REQUEST["authMember"]] = {}
    context.setCompEtudiants(comp_etudiants)

context.REQUEST.RESPONSE.redirect(context.absolute_url())