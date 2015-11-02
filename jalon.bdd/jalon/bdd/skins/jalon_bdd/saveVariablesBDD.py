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
bdd = {"typeBDD"                     : REQUEST.form["typeBDD"],
       "urlConnexion"                : REQUEST.form["urlConnexion"],
       "activerStockageConnexion"    : REQUEST.form["activerStockageConnexion"],
       "activerStockageConsultation" : REQUEST.form["activerStockageConsultation"]}

retour = context.setVariablesBDD(bdd)

REQUEST.RESPONSE.redirect("%s/@@jalon-bdd?gestion=gestion_connexion_bdd&message=%s" % (context.absolute_url(), retour))
