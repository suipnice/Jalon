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
       "use_mysql":                     REQUEST.form["useSaveMySQL"],
       "host_mysql":                    REQUEST.form["hostMySQL"],
       "port_mysql":                    REQUEST.form["portMySQL"],
       "db_name_mysql":                 REQUEST.form["dbNameMySQL"],
       "user_mysql":                    REQUEST.form["userMySQL"],
       "password_mysql":                REQUEST.form["passwordMySQL"]}

retour = context.setVariablesBDD(bdd)

REQUEST.RESPONSE.redirect("%s/@@jalon-bdd?gestion=gestion_connexion_bdd&message=%s" % (context.absolute_url(), retour))
