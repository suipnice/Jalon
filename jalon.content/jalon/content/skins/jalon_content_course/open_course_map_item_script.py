# Controller Python Script "open_course_map_item_script"
# bind container=container
# bind context=context
# bind namespace=
# bind script=script
# bind subpath=traverse_subpath
# parameters=
# title=
##

"""
    form: {
        id: 'ID_du_li_concerne' pour un chapitre / 'all' pour l'ensemble ,
        open: 'true' = a deplier / 'false' = a replier,
    }

"""
form = context.REQUEST.form

return form # Pour affichage dans la console lors du retour Ajax.
