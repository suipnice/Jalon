# -*- coding: utf-8 -*-
##Script (Python) "creationcompte_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Validation des formulaires
##

from Products.CMFCore.utils import getToolByName

form = context.REQUEST.form
#portal_registration = getToolByName(context, 'portal_registration')
#portal_membership = getToolByName(context, 'portal_membership')

#password = portal_registration.generatePassword()
#portal_membership.addMember(form["login"], password, ("EtudiantJalon",), "", {"fullname": form["fullname"], "email": form["email"]})
#portal_registration.registeredNotify(form["email"])

context.Members.admin.ajouterUtilisateurJalon(form)
context.REQUEST.RESPONSE.redirect("%s/confirmation_inscription" % context.absolute_url())