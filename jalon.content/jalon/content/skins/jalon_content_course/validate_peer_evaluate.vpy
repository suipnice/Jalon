# -*- coding: utf-8 -*-
##Script (Python) "validate_peer_evaluate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validation des formulaires
##

from logging import getLogger

LOG = getLogger('----- validate_peer_evaluate -----')

from Products.CMFPlone import PloneMessageFactory as _

error = False
form = context.REQUEST.form

index = 1
error_index = []
criteria_order = form["criteria_order"].replace("[", "").replace("]", "").replace("'", "").split(",")
# LOG.info("***** criteria_order : %s" % criteria_order)

for tmp in criteria_order:
    if not form.has_key("teacher"):
        criteria_comment = "criteria%i-comment" % index
        # LOG.info("***** criteria_comment : %s" % criteria_comment)
        criteria_comment_code = "criteria%i-comment-code" % index
        # LOG.info("***** criteria_comment_code : %s" % form[criteria_comment_code])
        criteria_comment_min = "criteria%i-comment-min" % index
        # LOG.info("***** criteria_comment_min : %s" % form[criteria_comment_min])
        criteria_comment_max = "criteria%i-comment-max" % index
        # LOG.info("***** criteria_comment_max : %s" % form[criteria_comment_max])
        #if criteria_comment_code == "2":
        #    if not form[criteria_comment]:
        #        state.setError(criteria_comment, _(u"Champ obligatoire"), "%s_required" % criteria_comment)
        #        error = True
        #        error_index.append(str(index))
        if form[criteria_comment_code] in ["1", "2"]:
            comment_length = len(form[criteria_comment])
            if comment_length != 0 or form[criteria_comment_code] == "2":
                if comment_length < int(form[criteria_comment_min])  or comment_length > int(form[criteria_comment_max]):
                    state.setError(criteria_comment, _(u"Commentaire invalide, taille min : %s, taille max : %s, taille actuelle : %s") % (form[criteria_comment_min], form[criteria_comment_max], comment_length), "%s_required" % criteria_comment)
                    error = True
                    error_index.append(str(index))

    criteria_note = "criteria%i-note" % index
    criteria_note_max = "criteria%i-note_max" % index
    if int(form[criteria_note]) < 0  or int(form[criteria_note]) > int(form[criteria_note_max]):
        state.setError(criteria_note, _(u"Note invalide"), "%s_required" % criteria_note)
        error = True
        if not index in error_index: error_index.append(str(index))
    index = index + 1

if not error:
    state.set(status="success")
else:
    state.setError("error_index", _(u"Veuillez corriger les critères d'évaluations : %s" % ",".join(error_index)), "")
    state.set(status='failure')

return state
