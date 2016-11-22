## Controller Python Script "correct_and_evaluate_deposit_file_script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cours edit
##

objet = context
form = context.REQUEST.form

correction = False
note = False
properties = {}
if "correction" in form:
    properties["Correction"] = form["correction"].strip()
    if form["correction"].strip() and form["correction"] != context.getCorrectionDepot():
        correction=True
if "note" in form:
    properties["Note"] = form["note"].strip()
    if form["note"].strip() and form["note"] != context.getNote():
        note=True
if properties:
    context.setProperties(properties)

if "file_file" in form and form["file_file"]:
    boite = context.aq_parent
    corrections = getattr(boite, "corrections", None)
    if not corrections:
        boite.invokeFactory(type_name='JalonFolder', id="corrections")
        corrections = getattr(boite, "corrections")
    try:
        idobj = corrections.invokeFactory(type_name='JalonFile', id="Correction_%s" % context.getId())
    except:
        idobj = "Correction_%s" % context.getId()
    obj = getattr(corrections, idobj)
    param = {"Title":       "%s (Correction)" % context.Title(),
             "Description": "",
             "File":        form["file_file"]}
    obj.setProperties(param)
    context.reindexObject()
    correction=True

if correction or note:
    context.notifierCorrection(correction, note)

return context.REQUEST.RESPONSE.redirect(context.aq_parent.absolute_url())
