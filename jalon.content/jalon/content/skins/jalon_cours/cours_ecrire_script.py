## Controller Python Script "cours_ecrire_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFPlone import PloneMessageFactory as _

errors = {}
request = context.REQUEST
if not request.form.has_key("a"): errors["a"] = _(u"Champ obligatoire")
else: request.SESSION.set("a", request.form["a"])
if not request.form["objet"]:  errors["objet"] = _(u"Champ obligatoire")
else: request.SESSION.set("objet", request.form["objet"])
if not request.form["message"]: errors["message"] = _(u"Champ obligatoire")
else: request.SESSION.set("message", request.form["message"])

if errors: 
   request.SESSION.set("errors", errors)
   redirection = "%s/cours_ecrire_view?section=ecrire" % context.absolute_url()
else:
   context.envoyerMail(request.form)
   for champ in ["errors", "a", "objet", "message"]:
       if request.SESSION.has_key(champ): del request.SESSION[champ]
   redirection = "%s/cours_ecrire_view?section=ecrire&message=mail" % context.absolute_url()
   
return request.RESPONSE.redirect(redirection)
