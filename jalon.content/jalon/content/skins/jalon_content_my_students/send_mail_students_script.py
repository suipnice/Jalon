## Controller Python Script "send_mail_students_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
form = request.form

if form["type"] in ["etape", "ue", "uel", "groupe"]:
    listeEtudiants = context.getListeEtudiants(form["code"], form["type"])
    for etudiant in listeEtudiants:
        if etudiant["EMAIL_ETU"]:
            form["a"] = etudiant["EMAIL_ETU"]
            context.envoyerMail(form)
    form["a"] = form["de"]
    context.envoyerMail(form)

request.RESPONSE.redirect(context.absolute_url())
