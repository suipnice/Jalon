## Controller Python Script "cours_boite_modifier"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

form = context.REQUEST.form

redirection = context.absolute_url()
if not "AfficherCompetences" in form:
    if int(form["CorrectionIndividuelle"]) == 0:
        NotificationCorrection = 0
    else:
        NotificationCorrection = int(form["NotificationCorrection"])
    if int(form["Notation"]) == 0:
        NotificationNotation = 0
    else:
        NotificationNotation = int(form["NotificationNotation"])
    dico = {"CorrectionIndividuelle" : int(form["CorrectionIndividuelle"]),
            "NotificationCorrection" : NotificationCorrection,
            "Notation"               : int(form["Notation"]),
            "NotificationNotation"   : NotificationNotation,
            "AccesDepots"            : int(form["AccesDepots"]),}
    #        "AccesCompetences"       : int(form["AccesCompetences"])
else:
    dico = {"AfficherCompetences": int(form["AfficherCompetences"]),
            "ModifierCompetences": int(form["ModifierCompetences"])}
    redirection = "%s?menu=competences" % context.absolute_url()

context.setProperties(dico)

context.REQUEST.RESPONSE.redirect(redirection)