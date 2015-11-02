## Controller Python Script "ajouterglossaire_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

param = {}
REQUEST = context.REQUEST
if not REQUEST.form.has_key("idobj"):
   idobj = context.invokeFactory(type_name='JalonTermeGlossaire', id="Glossaire-%s-%s" % (REQUEST["authMember"], DateTime().strftime("%Y%m%d%H%M%S")))
   obj = getattr(context, idobj)
   param = {"Title" : REQUEST["title"]
           ,"Description" : REQUEST["description"]}
   redirection = "%s" % context.absolute_url()
else:
   obj = context
   dicoAttribut = obj.getAttributsTypeMod()
   for attribut in REQUEST.form.keys():
       if dicoAttribut.has_key(attribut): param[dicoAttribut[attribut]] = REQUEST.form[attribut]
   redirection = "%s" % context.aq_parent.absolute_url()

obj.setProperties(param)

context.REQUEST.RESPONSE.redirect(redirection)