## Controller Python Script "edit_deposit_box_skills_options_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

context.setProperties({"AfficherCompetences": int(form["AfficherCompetences"]),
                       "ModifierCompetences": int(form["ModifierCompetences"])})

context.REQUEST.RESPONSE.redirect("%s?tab=skills" % context.absolute_url())
