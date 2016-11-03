## Controller Python Script "saveConfigMaintenance"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form
dico = {"annoncer_maintenance": form["annoncer_maintenance"],
        "activer_maintenance":  form["activer_maintenance"],
        "annoncer_vider_cache": form["annoncer_vider_cache"],
        "url_news_maintenance": form["url_news_maintenance"]}

date_debut_maintenance = "%s/%s/%s %s:%s" % (form["date_debut_maintenance_year"], form["date_debut_maintenance_month"], form["date_debut_maintenance_day"], form["date_debut_maintenance_hour"], form["date_debut_maintenance_minute"])
date_fin_maintenance = "%s/%s/%s %s:%s" % (form["date_fin_maintenance_year"], form["date_fin_maintenance_month"], form["date_fin_maintenance_day"], form["date_fin_maintenance_hour"], form["date_fin_maintenance_minute"])

dico["date_debut_maintenance"] = date_debut_maintenance
dico["date_fin_maintenance"] = date_fin_maintenance

context.setPropertiesMaintenance(dico, context.REQUEST)
context.REQUEST.RESPONSE.redirect("%s/gestion_maintenance" % context.absolute_url())
