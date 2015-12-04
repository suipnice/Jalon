##Python Script "saveVariablesBDD"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

REQUEST = context.REQUEST
bdd = {"typeBDD":                       REQUEST.form["typeBDD"],
       "urlConnexion":                  REQUEST.form["urlConnexion"],
       "activer_stockage_connexion":    REQUEST.form["activerStockageConnexion"],
       "activer_stockage_consultation": REQUEST.form["activerStockageConsultation"],
       "use_mysql":                     REQUEST.form["useSaveMySQL"]}

retour = context.setVariablesBDD(bdd)

REQUEST.RESPONSE.redirect("%s/@@jalon-bdd?gestion=gestion_connexion_bdd&message=%s" % (context.absolute_url(), retour))
