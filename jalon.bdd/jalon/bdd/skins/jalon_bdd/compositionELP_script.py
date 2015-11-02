# -*- coding: utf-8 -*-
##Python Script "compositionELP"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=compositionELP
##

form = context.REQUEST.form
redirection = context.absolute_url()

if form["TYP_ELP"] == 'etape':
    context.detacherToutesELP(form)
    #if "listeELP" in form:
    context.attacherELP(form)

if form["TYP_ELP"] == 'groupe':
    context.seDetacherToutesELP(form)
    #if "listeELP" in form:
    context.sattacherAELP(form)

if form["TYP_ELP"] == 'ue' or form["TYP_ELP"] == 'uel':
    if form["TYP_ELP_SELECT"] == 'groupe':
        context.detacherToutesELP(form)
        #if "listeELP" in form:
        context.attacherELP(form)
    else:
        # C'est un diplôme
        context.seDetacherToutesELP(form)
        #if "listeELP" in form:
        context.sattacherAELP(form)

"""
#si l'on souhaite attacher un ELP
if form["from"] == "listeTousELP:list":
    if form["TYP_ELP"] == 'ue' or form["TYP_ELP"] == 'uel':
        if form["TYP_ELP_SELECT"] == 'groupe':
            context.attacherELP(form)
        else:
            #si c'est un diplôme
            context.sattacherAELP(form)
    elif form["TYP_ELP"] == 'etape':
        context.attacherELP(form)
    else:
        # form["TYP_ELP"] == 'groupe':
        context.sattacherAELP(form)
else:
    #si l'on souhaite détacher un ELP
    if form["TYP_ELP"] == 'ue' or form["TYP_ELP"] == 'uel':
        if form["TYP_ELP_SELECT"] == 'groupe':
            context.detacherELP(form)
        else:
            #si c'est un diplôme
            context.seDetacherDeELP(form)
    elif form["TYP_ELP"] == 'etape':
        context.detacherELP(form)
    else:
        # form["TYP_ELP"] == 'groupe':
        context.seDetacherDeELP(form)

if "redirection" in form.keys():
    redirection = form["redirection"]
"""
context.plone_utils.addPortalMessage(u"Composition mise à jour.", "success")
context.REQUEST.RESPONSE.redirect("%s/page_composition?codeELP=%s&TYP_ELP_SELECT=%s" % (redirection, form["COD_ELP"], form["TYP_ELP_SELECT"]))
#return context.REQUEST