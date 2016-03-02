# -*- coding: utf-8 -*-
##Script (Python) "creationcompte_form_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validation des formulaires
##

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from quintagroup.captcha.core import ProductMessageFactory as _
from quintagroup.captcha.core.utils import decrypt, parseKey, \
    encrypt1, getWord
from DateTime import DateTime

def set_error():
    message = _(u"Please re-enter validation code.")
    context.plone_utils.addPortalMessage(message, 'error')
    state.setError('key', message, 'key_required')
    return state.set(status="failure")

error = False
request = context.REQUEST
form = request.form

if "form.button.cancel" in form:
    state.set(status="canceled")
    return state

if form["login"] not in ["", " ", None]:
    membership_tool=getToolByName(context, 'portal_membership')
    if membership_tool.getMemberById(form["login"]):
        state.setError("login", _(u"login déjà utilisé"), "login_required")
        state.set(status='failure')
        error = True

if not "@" in form["email"] or not "." in form["email"]:
    state.setError("email", _(u"Adresse électronique incorrecte"), "email_required")
    state.set(status='failure')
    error = True

if not " " in form["fullname"]:
    state.setError("fullname", _(u"Nom complet incorrect, veuillez entrer vos nom et prénom"), "fullname_required")
    state.set(status='failure')
    error = True

for obligatoire in ["login", "email", "fullname"]:
    if form[obligatoire] in ["", " ", None]:
        state.setError(obligatoire, _(u"Champ obligatoire"), "%s_required" % obligatoire)
        state.set(status='failure')
        error = True

test_key = request.get('key', '')
hashkey = request.get('hashkey', '')
try:
    decrypted_key = decrypt(context.captcha_key, hashkey)
except:
    return set_error()
parsed_key = parseKey(decrypted_key)

index = parsed_key['key']
date = parsed_key['date']

try:
    img = getattr(context, '%s.jpg' % index)
except AttributeError:
    return set_error()
solution = img.title
enc = encrypt1(test_key)
captcha_tool = getToolByName(context, 'portal_captchas')
if (enc != solution) or (captcha_tool.has_key(decrypted_key)) \
    or (DateTime().timeTime() - float(date)>3600):
    return set_error()
else:
    captcha_tool.addExpiredKey(decrypted_key)
    return state.set(status="success")

#if not error:
#    state.set(status="success")

#return state
