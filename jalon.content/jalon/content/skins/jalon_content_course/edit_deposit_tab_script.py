## Controller Python Script "edit_deposit_tab_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

if int(form["CorrectionIndividuelle"]) == 0:
    NotificationCorrection = 0
else:
    NotificationCorrection = int(form["NotificationCorrection"])
if int(form["Notation"]) == 0:
    NotificationNotation = 0
else:
    NotificationNotation = int(form["NotificationNotation"])
dico = {"CorrectionIndividuelle": int(form["CorrectionIndividuelle"]),
        "NotificationCorrection": NotificationCorrection,
        "Notation":               int(form["Notation"]),
        "NotificationNotation":   NotificationNotation,
        "AccesDepots":            int(form["AccesDepots"])}

context.setProperties(dico)

context.REQUEST.RESPONSE.redirect(context.absolute_url())
