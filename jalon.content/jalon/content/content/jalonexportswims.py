# -*- coding: utf-8 -*-
u"""jalonexportswims : librairie de scripts permettant d'exporter des EXO WIMS dans différents formats."""

import xml.etree.ElementTree as ET
# import HTMLParser

import jalon_utils

from zipfile import ZipFile, ZIP_DEFLATED
import os

from random import shuffle

import string
import lxml

from logging import getLogger
LOG = getLogger('jalonExportsWims')
"""
# Log examples :
LOG.debug('debug message')
# LOG.info('info message')
LOG.warn('warn message')
LOG.error('error message')
LOG.critical('critical message')
"""

alphabet = list(string.ascii_uppercase)

# lxml parser est plus permissif qu'elementTree : grace a l'option "recover" il est capable d'ignorer les balises attributs html non conforms en XML.
parser_lxml = lxml.etree.XMLParser(recover=True)


def getExoTXT(context, format="GIFT", version="latest"):
    """Permet de renvoyer un exo WIMS au format plain text (GIFT).

    # Plus d'infos sur le format GIFT : https://docs.moodle.org/30/en/GIFT_format

    """


def getExoZIP(filename_path, exo_donnees):
    """Fournit les donnees "exo_donnees" compressees au format zip."""
    import tempfile
    fd, path = tempfile.mkstemp('.zipfiletransport')
    os.close(fd)

    zipFile = ZipFile(path, 'w', ZIP_DEFLATED)

    zipFile.writestr(filename_path, exo_donnees)
    zipFile.close()

    fp = open(path, 'rb')
    data = fp.read()
    fp.close()
    return {"length": str(os.stat(path)[6]), "data": data}


def getExoXML(context, formatXML="OLX", version="latest"):
    """Permet de renvoyer un exo WIMS au format XML (QTI, OLX, Moodle, ...).

    # Plus d'infos sur le format OLX (format XML d'EDX) : http://edx-open-learning-xml.readthedocs.org/en/latest/problem-xml/index.html
    # Plus d'infos sur le format IMS QTI : https://webapps.ph.ed.ac.uk/qtiworks
    # Plus d'infos sur le format Moodle XML : https://docs.moodle.org/30/en/Moodle_XML_format
    # Plus d'infos sur le format "Flow Lesson Builder 2" (.fll) : impossible de trouver des infos sur ce format... :/ - http://www.turningtechnologies.eu/downloads/

    """
    """
    Imports supportés par TurningPoint 5.3 :
    # Attention : TurningPoint 5 n'est plus supporté par Turning Techs depuis janvier 2016...
    # Un document Word (.doc,.docx) doit contenir le texte de la question en titre 1 et le texte de la réponse en titre 2.
        Seules les questions à choix multiples peuvent être importées.
        Le type de question peut être modifié après l'importation.
    # Un document QTI peut être importé à partir de :
        * Respondus® (3.5 à 4.0) (fichier zip XML RAA) - Logiciel Windows uniquement, tarif $150.
        * Examview® (5.1 à 7.0) (fichier HTML sans les polices).
    # Un document RTF peut être importé à partir d'Examview® (7.0 - 8.0) (galerie de style: par défaut).
    """
    modele = context.getModele()
    # LOG.info("[getExoXML] modele = %s" % modele)
    portal = context.portal_url.getPortalObject()
    membership_tool = portal.portal_membership

    if not membership_tool.isAnonymousUser():
        demandeur = membership_tool.getAuthenticatedMember()
        """
        try:
            source = str(getattr(self, "%s_%s.xml" % (format, modele)))
        except:
            return ("<error>Désolé, ce modèle ne peut être exporté dans le format %s.</error>" % format)
        tree = ET.ElementTree(root)
        for key in dicoXML.keys():
            source = source.replace("$$%s$$" % key, ET.tostring(dicoXML[key])
        """
        parsed_exo = context.getExoWims(modele, demandeur)
        if parsed_exo["code_source"] is None:
            return "<error>%s</error>" % parsed_exo["error_message"]

        parsed_exo["id"] = context.getId()
        # Parametres communs :
        parsed_exo["titre"] = context.Title().decode("utf-8")

        if formatXML == "OLX":
            # apparement, EDX ne prend pas en compte les attributs du problem. (oct. 2015)
            # attention, en choisissant ""rerandomize": "always"", le bouton "check" disparait lors des tests sur EDX... :/
            exoXML = ET.Element("problem", attrib={"rerandomize": "always", "title": parsed_exo["titre"], "display_name": parsed_exo["titre"]})
            elementXML = ET.SubElement(exoXML, "legend")
            elementXML.text = parsed_exo["titre"]
            exoXML = __qcmsimple_to_olx(exoXML, parsed_exo)

        # Format Moodle XML
        elif formatXML == "Moodle_XML":
            if modele == "qcmsimple":
                exoXML = __qcmsimple_to_moodleXML(parsed_exo)

        # Format QTI
        elif formatXML == "QTI":
            if version == "1.1":
                # Format QTI v1.1
                exoXML = ET.Element("assessmentItem",
                                    attrib={"xmlns"             : "http://www.imsproject.org/xsd/ims_qti_rootv1p1",
                                            "xmlns:xsi"         : "http://www.w3.org/2001/XMLSchema-instance",
                                            "xsi:schemaLocation": "http://www.imsproject.org/xsd/ims_qti_rootv1p1 http://www.imsproject.org/xsd/ims_qti_rootv1p1.xsd",
                                            "identifier"        : parsed_exo["id"],
                                            "title"             : parsed_exo["titre"]})
                if modele == "qcmsimple":
                    exoXML = __qcmsimple_to_qti_11(exoXML, parsed_exo)
            elif version == "1.2.1":
                # Format QTI v1.2.1

                # Plus d'infos sur le format QTI v1.2.1 :
                # http://www.imsglobal.org/question/qtiv1p2/imsqti_litev1p2.html
                # http://www.imsglobal.org/question/qtiv1p2/imsqti_oviewv1p2.html
                # http://www.imsglobal.org/question/qtiv1p2/imsqti_asi_outv1p2.html  "ASI Outcomes Processing"
                # http://www.imsglobal.org/question/qtiv1p2/imsqti_asi_bestv1p2.html "ASI Best Practice & Implementation Guide"
                # http://www.imsglobal.org/question/qtiv1p2/imsqti_asi_bindv1p2.html "ASI XML Binding Specification"
                # XSD :
                # ASI LITE                        https://www.imsglobal.org/sites/default/files/xsd/ims_qtilitev1p2p1.xsd
                # ASI (Assessment, Section, Item) https://www.imsglobal.org/sites/default/files/xsd/ims_qtiasiv1p2p1.xsd
                # RES (Results Reporting)         https://www.imsglobal.org/sites/default/files/xsd/ims_qtiresv1p2p1.xsd

                exoXML = ET.Element("questestinterop",
                                    attrib={"xmlns"             : "http://www.imsglobal.org/xsd/ims_qtiasiv1p2",
                                            "xmlns:xsi"         : "http://www.w3.org/2001/XMLSchema-instance",
                                            "xsi:schemaLocation": "http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd"
                                            })
                elementXML = ET.SubElement(exoXML,
                                           "assessment",
                                           attrib={"ident" : parsed_exo["id"],
                                                   "title" : parsed_exo["titre"]
                                                   })
                elementXML = ET.SubElement(elementXML, "section", attrib={"ident" : parsed_exo["id"]})

                if modele == "qcmsimple":
                    __qcmsimple_to_qti_121(elementXML, parsed_exo)
                elif modele == "qcmsuite":
                    __qcmsuite_to_qti_121(elementXML, parsed_exo)
            else:
                # Format QTI v2.1
                # Plus d'infos sur le format QTI v2.1 :
                # XML Binding : http://www.imsglobal.org/question/qtiv2p1/imsqti_bindv2p1.html

                exoXML = ET.Element("assessmentTest",
                                    attrib={"xmlns"             : "http://www.imsglobal.org/xsd/imsqti_v2p1",
                                            "xmlns:xsi"         : "http://www.w3.org/2001/XMLSchema-instance",
                                            "xsi:schemaLocation": "http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/imsqti_v2p1.xsd",
                                            "identifier"        : parsed_exo["id"],
                                            "title"             : parsed_exo["titre"],
                                            "adaptive"          : "false",
                                            "timeDependent"     : "false"})

                if modele == "qcmsimple":
                    exoXML = __qcmsimple_to_qti_21(exoXML, parsed_exo)
                elif modele == "qcmsuite":
                    exoXML = __qcmsuite_to_qti_21(exoXML, parsed_exo)
                else:
                    exoXML.text = u"Désolé, ce modèle n'est pas pris en charge dans ce format."

        # Format "Flow Lecon", généré par "Lesson Builder" de Turning Technologies
        elif formatXML == "FLL":
            # <TestDefinition xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            exoXML = ET.Element("TestDefinition",
                                attrib={"xmlns:xsd"         : "http://www.w3.org/2001/XMLSchema",
                                        "xmlns:xsi"         : "http://www.w3.org/2001/XMLSchema-instance"
                                        })

            elementXML = ET.SubElement(exoXML, "name")
            elementXML.text = u"Leçon importée de Jalon"
            elementXML = ET.SubElement(exoXML, "description")
            elementXML.text = u"Leçon importée depuis un exercice WIMS sous Jalon 4.5"
            elementXML = ET.SubElement(exoXML, "author")
            elementXML.text = demandeur.getId()
            # Il faut donner un temps superieur au temps total des questions (unité : s)
            elementXML = ET.SubElement(exoXML, "lessonMaxTime")
            elementXML.text = "30"
            elementXML = ET.SubElement(exoXML, "shuffleQuestions")
            elementXML.text = "true"

            if modele == "qcmsimple":
                exoXML = __qcmsimple_to_FlowXML(exoXML, parsed_exo)

        else:
            exoXML = ET.Element("error")
            exoXML.text = u"Le format '%s' n'est pas pris en charge." % formatXML
        return ET.tostring(exoXML, encoding="utf-8")

    else:
        return "<error>Vous n'avez pas le droit de télécharger ce fichier. Vous devez vous identifier en tant qu'enseignant d'abord.</error>"


def __qcmsimple_to_olx(exoXML, parsed_exo):
    # Modele "QCM Simple" vers OLX:
    # LOG.info("[__qcmsimple_to_olx] parsed_exo = %s" % parsed_exo)
    enonce = jalon_utils.convertHTMLEntitiesToUTF8(parsed_exo["enonce"])
    # enonce = jalon_utils.convertHTMLToXHTML(enonce)
    enonce = '<div class="enonce">%s</div>' % enonce

    exoXML.append(ET.fromstring(enonce, parser=parser_lxml))

    if parsed_exo["options_checkbox"] == 1:
        # Checkbox buttons
        element = "choiceresponse"
        attributs_element = {}
        if parsed_exo["options_checkbox"] == 1:
            # Les modes partiels "halves" et "EDC" existent, mais aucun d'eux ne semble fonctionner avec EDX (oct. 2015)
            if parsed_exo["options_eqweight"] == 1:
                attributs_element["partial_credit"] = "EDC"
            else:
                attributs_element["partial_credit"] = "halves"

        sousElement = "checkboxgroup"
        attributs_sousElement = {"label": parsed_exo["id"],
                                 "answer-pool": parsed_exo["tot"]
                                 }
    else:
        # Radio buttons
        element = "multiplechoiceresponse"
        attributs_element = {"targeted-feedback": ""}
        # partial_credit = "points"

        sousElement = "choicegroup"
        attributs_sousElement = {"label": parsed_exo["id"],
                                 "shuffle": "true",
                                 # EDX est incapable de gérer à la fois "answer-pool" et "shuffle"... :/
                                 # "answer-pool": parsed_exo["tot"]
                                 }

    elementXML = ET.SubElement(exoXML, element, attrib=attributs_element)
    elementXML = ET.SubElement(elementXML,
                               sousElement,
                               attrib=attributs_sousElement)
    liste_bons = parsed_exo["bonnesrep"].decode("utf-8").split("\n")
    liste_id_bons = []
    liste_id_mauvais = []
    nb_rep = 0
    for ligne in liste_bons:
        rep = ligne.strip()
        if rep != "":
            liste_id_bons.append(alphabet[nb_rep])
            nb_rep = nb_rep + 1
            reponse = ET.SubElement(elementXML, "choice", attrib={"correct": "true", "explanation-id": "correct"})
            reponse.text = rep

    liste_mauvais = parsed_exo["mauvaisesrep"].decode("utf-8").split("\n")
    for ligne in liste_mauvais:
        rep = ligne.strip()
        if rep != "":
            liste_id_mauvais.append(alphabet[nb_rep])
            nb_rep = nb_rep + 1
            reponse = ET.SubElement(elementXML, "choice", attrib={"correct": "false", "explanation-id": "incorrect"})
            reponse.text = ligne

    if parsed_exo["options_checkbox"] == 1:
        # en mode "checkbox", on place les feedbacks en compoundhint, a l'interieur du checkboxgroup
        if parsed_exo["feedback_bon"] != "":
            reps = " ".join(liste_id_bons)
            feedback = ET.SubElement(elementXML, "compoundhint", attrib={"value": reps})
            feedback.text = parsed_exo["feedback_bon"].decode("utf-8")
        # Malheuresement, avec cette méthode le feedback de mauvaise réponse n'apparait que si toutes les mauvaises sont cochées.
        # il faudrait trouver le moyen de les afficher si au moins une est cochée.
        if parsed_exo["feedback_mauvais"] != "":
            reps = " ".join(liste_id_mauvais)
            feedback = ET.SubElement(elementXML, "compoundhint", attrib={"value": reps})
            feedback.text = parsed_exo["feedback_mauvais"].decode("utf-8")

    if parsed_exo["hint"] != "" or parsed_exo["help"] != "":
        elementXML = ET.SubElement(exoXML, "demandhint")
        if parsed_exo["hint"] != "":
            aide = ET.SubElement(elementXML, "hint")
            aide.text = parsed_exo["hint"].decode("utf-8")
        if parsed_exo["help"] != "":
            aide = ET.SubElement(elementXML, "hint")
            aide.text = parsed_exo["help"].decode("utf-8")

    if parsed_exo["options_checkbox"] == 0:
        # en mode "radio", on place les feedbacks en feedbacksets
        if parsed_exo["feedback_bon"] != "" or parsed_exo["feedback_mauvais"] != "":
            elementXML = ET.SubElement(exoXML, "targetedfeedbackset")
            if parsed_exo["feedback_mauvais"] != "":
                feedback = ET.SubElement(elementXML, "targetedfeedback", attrib={"explanation-id": "incorrect"})
                chaine = '<div class="detailed-targeted-feedback feedback-hint-incorrect"><div class="hint-label">Incorrect :</div><div class="hint-text">%s</div></div>' % parsed_exo["feedback_mauvais"]
                feedback.append(ET.fromstring(chaine, parser=parser_lxml))
            if parsed_exo["feedback_bon"] != "":
                feedback = ET.SubElement(elementXML, "targetedfeedback", attrib={"explanation-id": "correct"})
                chaine = '<div class="detailed-targeted-feedback feedback-hint-correct"><div class="hint-label">Correct :</div><div class="hint-text">%s</div></div>' % parsed_exo["feedback_bon"]
                feedback.append(ET.fromstring(chaine, parser=parser_lxml))

    if parsed_exo["feedback_general"] != "":
        elementXML = ET.SubElement(exoXML, "solution")
        chaine = '<div class="detailed-solution"><p>Solution</p><p>%s</p></div>' % parsed_exo["feedback_general"]
        elementXML.append(ET.fromstring(chaine, parser=parser_lxml))

    return exoXML


def __qcmsimple_to_qti_11(exoXML, parsed_exo):
    # Modele "QCM Simple" vers QTI 1.1:
    # TODO !!
    ###

    elementXML = ET.SubElement(exoXML,
                               "responseDeclaration",
                               attrib={"identifier":  "RESPONSE",
                                       "cardinality": "multiple",
                                       "baseType":    "identifier"})

    correctResponse = ET.SubElement(elementXML, "correctResponse")

    elementXML = ET.SubElement(exoXML,
                               "outcomeDeclaration",
                               attrib={"identifier":  "SCORE",
                                       "cardinality": "single",
                                       "baseType":    "float"})

    elementXML = ET.SubElement(exoXML, "itemBody")
    choiceInteraction = ET.SubElement(elementXML,
                                      "choiceInteraction",
                                      attrib={"responseIdentifier": "RESPONSE",
                                              "shuffle":            "true",
                                              "maxChoices":         "0"})

    elementXML = ET.SubElement(choiceInteraction, "prompt")
    elementXML.text = parsed_exo["enonce"].decode("utf-8")

    liste_bons = parsed_exo["bonnesrep"].decode("utf-8").split("\n")
    nb_rep = 0
    for ligne in liste_bons:
        nb_rep = nb_rep + 1
        rep_id = "rep_%s" % nb_rep
        elementXML = ET.SubElement(correctResponse, "value")
        elementXML.text = rep_id
        elementXML = ET.SubElement(choiceInteraction,
                                   "simpleChoice",
                                   attrib={"identifier": rep_id,
                                           "fixed":      "false"})
        elementXML.text = ligne

    liste_mauvais = parsed_exo["mauvaisesrep"].decode("utf-8").split("\n")
    for ligne in liste_mauvais:
        nb_rep = nb_rep + 1
        rep_id = "rep_%s" % nb_rep
        elementXML = ET.SubElement(choiceInteraction,
                                   "simpleChoice",
                                   attrib={"identifier": rep_id,
                                           "fixed":      "false"})
        elementXML.text = ligne
    return exoXML


def __qcmsimple_to_qti_121(exoXML, parsed_exo):
    """Modele "QCM Simple" vers QTI 1.2.1."""
    # TODO !!

    ###
    # Pour TurningPoint, le title doit absolument ressembler à ca "parsed_exo["titre"] Question MC #N"
    element_item = ET.SubElement(exoXML, "item",
                                 attrib={"ident" : parsed_exo["id"],
                                         "title" : "%s Question MC #1" % parsed_exo["titre"]})

    element_metadata = ET.SubElement(element_item, "itemmetadata")
    elementXML = ET.SubElement(element_metadata, "qmd_itemtype")
    elementXML.text = "qcmsimple"
    elementXML = ET.SubElement(element_metadata, "qmd_toolvendor")
    elementXML.text = "Jalon @ http://jalon.unice.fr"

    elementXML = ET.SubElement(element_item, "presentation")
    element_flow = ET.SubElement(elementXML, "flow")
    __add_matttext(element_flow, parsed_exo["enonce"].decode("utf-8"), flow_type=None)

    # rcardinality (optional - enumerated list: Single, Multiple, Ordered. Default=Single). Indicates the number of responses expected from the user.
    if parsed_exo["options_checkbox"] == 1:
        rcardinality = "Multiple"
    else:
        rcardinality = "Single"

    elementXML = ET.SubElement(element_flow,
                               "response_lid",
                               attrib={"ident": "%s_RL" % parsed_exo["id"],
                                       "rcardinality": rcardinality,
                                       "rtiming":      "No"})
    element_renderchoice = ET.SubElement(elementXML,
                                         "render_choice",
                                         attrib={"shuffle": "Yes"})

    element_resprocessing = ET.SubElement(element_item, "resprocessing")
    elementXML = ET.SubElement(element_resprocessing, "outcomes")
    elementXML = ET.SubElement(elementXML, "decvar")

    # Vu que TurningPoint 5 est incapable de faire de l'aléatoire, on mélange les propositions...
    rep_items = __randomize_responses_qcmsimple(parsed_exo["bonnesrep"], parsed_exo["mauvaisesrep"])

    for rep_id, rep_item in rep_items:
        elementXML = ET.SubElement(element_renderchoice,
                                   "response_label",
                                   attrib={"ident": rep_id})
        __add_matttext(elementXML, rep_item["data"])

        """ apparament, TT ne supporte qu'un varequal par conditionvar.
        Du coup il faut boucler sur respcondition au lieu de varequal..."""
        element_respcondition = ET.SubElement(element_resprocessing,
                                              "respcondition",
                                              attrib={"title": rep_item["type"],
                                                      "continue": "Yes"})
        elementXML = ET.SubElement(element_respcondition, "conditionvar")
        elementXML = ET.SubElement(elementXML,
                                   "varequal",
                                   attrib={"respident": parsed_exo["id"]})
        elementXML.text = rep_id

        elementXML = ET.SubElement(element_respcondition,
                                   "setvar",
                                   attrib={"action": "Add"})

        elementXML.text = rep_item["value"]
        if rep_item["value"] == "0":
            feedbacktype = "Solution"
        else:
            feedbacktype = "Response"
        elementXML = ET.SubElement(element_respcondition,
                                   "displayfeedback",
                                   attrib={"feedbacktype": feedbacktype,
                                           "linkrefid":    rep_item["type"]})

    # Feedbacks #

    # Feedback bon #
    elementXML = ET.SubElement(element_item,
                               "itemfeedback",
                               attrib={"ident": "Correct"})
    __add_matttext(elementXML, parsed_exo["feedback_bon"].decode("utf-8"))

    # Feedback Mauvais (+Solution) #
    elementXML = ET.SubElement(element_item,
                               "itemfeedback",
                               attrib={"ident": "Incorrect"})
    elementXML = ET.SubElement(elementXML,
                               "solution",
                               attrib={"feedbackstyle": "Complete"})
    elementXML = ET.SubElement(elementXML, "solutionmaterial")
    __add_matttext(elementXML, parsed_exo["feedback_mauvais"].decode("utf-8"))

    """
                                 "tot"             : "5",
                                 "givetrue"        : "2",
                                 "minfalse"        : "0",
                                 "feedback_general": "",
                                 "options"         : "checkbox split",
                                 "accolade"        : "1",
                                 "credits"         : "",
                                 "hint"            : "",
                                 "help"            : "",
    """
    return exoXML


def __add_matttext(elementXML, texte, flow_type="flow_mat"):
    if flow_type is not None:
        elementXML = ET.SubElement(elementXML, flow_type)
    elementXML = ET.SubElement(elementXML, "material")
    elementXML = ET.SubElement(elementXML, "mattext",
                               attrib={"texttype": "text/html"})
    elementXML.text = texte


def __qcmsimple_to_qti_21(exoXML, parsed_exo):
    # Modele "QCM Simple" vers QTI 2.1:

    assessmentItem = ET.SubElement(exoXML,
                                   "assessmentItem",
                                   attrib={"xmlns"             : "http://www.imsglobal.org/xsd/imsqti_v2p1",
                                           "xmlns:xsi"         : "http://www.w3.org/2001/XMLSchema-instance",
                                           "xsi:schemaLocation": "http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/imsqti_v2p1.xsd",
                                           "identifier"        : parsed_exo["id"],
                                           "title"             : parsed_exo["titre"],
                                           "adaptive"          : "false",
                                           "timeDependent"     : "false"})

    if parsed_exo["options_checkbox"] == 1:
        cardinality = "multiple"
    else:
        cardinality = "single"

    elementXML = ET.SubElement(assessmentItem,
                               "responseDeclaration",
                               attrib={"identifier":  "RESPONSE",
                                       "cardinality": cardinality,
                                       "baseType":    "identifier"})

    correctResponse = ET.SubElement(elementXML, "correctResponse")

    elementXML = ET.SubElement(assessmentItem,
                               "outcomeDeclaration",
                               attrib={"identifier":  "SCORE",
                                       "cardinality": "single",
                                       "baseType":    "float"})

    elementXML = ET.SubElement(assessmentItem, "itemBody")
    choiceInteraction = ET.SubElement(elementXML,
                                      "choiceInteraction",
                                      attrib={"responseIdentifier": "RESPONSE",
                                              "shuffle":            "true",
                                              "maxChoices":         "0"})

    elementXML = ET.SubElement(choiceInteraction, "prompt")
    elementXML.text = parsed_exo["enonce"].decode("utf-8")

    liste_bons = parsed_exo["bonnesrep"].decode("utf-8").split("\n")
    nb_rep = 0
    for ligne in liste_bons:
        rep = ligne.strip()
        if rep != "":
            nb_rep = nb_rep + 1
            rep_id = "rep_%s" % nb_rep
            elementXML = ET.SubElement(correctResponse, "value")
            elementXML.text = rep_id
            elementXML = ET.SubElement(choiceInteraction,
                                       "simpleChoice",
                                       attrib={"identifier": rep_id,
                                               "fixed":      "false"})
            elementXML.text = rep

    liste_mauvais = parsed_exo["mauvaisesrep"].decode("utf-8").split("\n")
    for ligne in liste_mauvais:
        rep = ligne.strip()
        if rep != "":
            nb_rep = nb_rep + 1
            rep_id = "rep_%s" % nb_rep
            elementXML = ET.SubElement(choiceInteraction,
                                       "simpleChoice",
                                       attrib={"identifier": rep_id,
                                               "fixed":      "false"})
            elementXML.text = rep

    if parsed_exo["feedback_general"] != "":
        elementXML = ET.SubElement(assessmentItem,
                                   "modalFeedback",
                                   attrib={"outcomeIdentifier": "FEEDBACK",
                                           "identifier": "COMMENT",
                                           "showHide": "show"})
        elementXML.text = parsed_exo["feedback_general"].decode("utf-8")

    # "options"         : "checkbox split",
    # <modalFeedback outcomeIdentifier="FEEDBACK" showHide="show" identifier="correct">correct</modalFeedback>
    # <modalFeedback outcomeIdentifier="FEEDBACK" showHide="show" identifier="incorrect">incorrect</modalFeedback>
    elementXML = ET.SubElement(assessmentItem, "responseProcessing", attrib={"template": "http://www.imsglobal.org/question/qti_v2p1/rptemplates/match_correct"})
    return exoXML


def __qcmsimple_to_moodleXML(parsed_exo):
    """Modele "QCM Simple" vers moodle XML."""
    exoXML = ET.Element("question", attrib={"type": "multichoice"})

    elementXML = ET.SubElement(exoXML, "name")
    elementXML = ET.SubElement(elementXML, "text")
    elementXML.text = parsed_exo["titre"]

    elementXML = ET.SubElement(exoXML, "questiontext", attrib={"format": "html"})
    elementXML = ET.SubElement(elementXML, "text")
    chaine = "<![CDATA[%s]]>" % parsed_exo["enonce"]
    elementXML.append(ET.fromstring(chaine))

    """
    <question type="multichoice">
        <name>
          <text>MULTIPLE CHOICE</text>
        </name>
        <questiontext format="html">
          <text><![CDATA[<p>Couleur du cheval ?</p>]]></text>
        </questiontext>
        <generalfeedback format="html">
          <text><![CDATA[<p>BRAVO !!</p>]]></text>
        </generalfeedback>
        <defaultgrade>1.0000000</defaultgrade>
        <penalty>0.3333333</penalty>
        <hidden>0</hidden>
        <single>true</single>
        <shuffleanswers>true</shuffleanswers>
        <answernumbering>abc</answernumbering>
        <correctfeedback format="html">
          <text>Your answer is correct.</text>
        </correctfeedback>
        <partiallycorrectfeedback format="html">
          <text>Your answer is partially correct.</text>
        </partiallycorrectfeedback>
        <incorrectfeedback format="html">
          <text>Your answer is incorrect.</text>
        </incorrectfeedback>
        <shownumcorrect/>
        <answer fraction="0" format="html">
          <text><![CDATA[<p>Bleu</p>]]></text>
          <feedback format="html">
            <text></text>
          </feedback>
        </answer>
        <answer fraction="100" format="html">
          <text><![CDATA[<p>Blanc</p>]]></text>
          <feedback format="html">
            <text></text>
          </feedback>
        </answer>
    </question>

    """


def __qcmsimple_to_FlowXML(exoXML, parsed_exo):
    """Modele "QCM Simple" vers le format XML Flow Lecon (.fll)."""
    elementXML = ET.SubElement(exoXML, "questions")
    element_question = ET.SubElement(elementXML, "QuestionDefinition")

    elementXML = ET.SubElement(element_question, "qExternalId")
    elementXML.text = "1"

    elementXML = ET.SubElement(element_question, "qInternalId")
    elementXML.text = parsed_exo["id"]

    elementXML = ET.SubElement(element_question, "qname")
    elementXML.text = "<![CDATA[%s]]>" % parsed_exo["titre"].decode("utf-8")

    elementXML = ET.SubElement(element_question, "questionMaxTime")
    elementXML.text = "30"

    elementXML = ET.SubElement(element_question, "useLetters")
    elementXML.text = "true"

    # nombre de points de la question
    elementXML = ET.SubElement(element_question, "grade")
    elementXML.text = "1"

    # Types : {0:"Radio Button", 1:"Checkbox", 5:"vrai/faux", ... ?}
    elementXML = ET.SubElement(element_question, "questionType")

    if parsed_exo["options_checkbox"] == 1:
        elementXML.text = "1"
    else:
        elementXML.text = "0"

    elementXML = ET.SubElement(element_question, "allowPartialCredit")
    if parsed_exo["options_split"] == 1:
        elementXML.text = "true"
    else:
        elementXML.text = "false"

    elementAnswers = ET.SubElement(element_question, "questionAnswers")

    # Vu que Lesson Builder 2 est incapable de faire de l'aléatoire, on mélange les propositions...
    rep_items = __randomize_responses_qcmsimple(parsed_exo["bonnesrep"], parsed_exo["mauvaisesrep"])
    liste_questions = []
    nb_rep = 0
    # for ligne in liste_bons:
    for rep_id, rep_item in rep_items:
        if nb_rep <= len(alphabet):
            elementReponse = ET.SubElement(elementAnswers, "answer")
            elementXML = ET.SubElement(elementReponse, "aId")
            elementXML.text = "%s" % nb_rep
            elementXML = ET.SubElement(elementReponse, "aKey")
            elementXML.text = alphabet[nb_rep]
            # elementXML = ET.SubElement(elementReponse, "aText")
            # elementXML.text = alphabet[nb_rep]
            elementXML = ET.SubElement(elementReponse, "isCorrect")
            if rep_item["value"] == "1":
                elementXML.text = "true"
            else:
                elementXML.text = "false"
            liste_questions.append("<li>%s - %s</li>" % (alphabet[nb_rep], rep_item["data"]))
            nb_rep = nb_rep + 1

    elementXML = ET.SubElement(element_question, "questionContent")

    # On intègre les proposition dans l'enoncé pour les faire apparaitre.
    # Pour le moment, un bug d'affichage dans Flow empeche d'utiliser les puces autres que numériques pour les <ol>...
    # questionContent = "<div class=\"oef_explain\" style=\"font-size:24px;\">%s</div><ol type=\"A\" style=\"list-style-type: upper-alpha;font-size:24px;\">%s</ol>" % (parsed_exo["enonce"].decode("utf-8"), "\n".join(liste_questions))
    questionContent = "<div class=\"oef_explain\" style=\"font-size:24px;\">%s</div><ul style=\"font-size:24px;\">%s</ul>" % (parsed_exo["enonce"].decode("utf-8"), "\n".join(liste_questions))

    elementXML.text = "<![CDATA[%s]]>" % questionContent

    # Il semblerait que questionContentType = 6 correspondrait a du contenu HTML
    elementXML = ET.SubElement(element_question, "questionContentType")
    elementXML.text = "6"
    return exoXML
    # elementXML = ET.SubElement(element_question, "advancedMode")
    # elementXML.text = "false"

    """  Checkbox :
      <questionType>1</questionType>
      <questionMaxTime>30</questionMaxTime>
      <useLetters>true</useLetters>
      <allowChangeAnswer>false</allowChangeAnswer>

      <advancedMode>false</advancedMode>
      <rightAnswerTolerance>0</rightAnswerTolerance>
      <grade>1</grade>
      <penalty>0</penalty>
      <questionAnswers>
        <answer>
          <aId>0</aId>
          <aKey>A</aKey>
          <aPercentValue>50</aPercentValue>
          <aText>A</aText>
          <isCorrect>true</isCorrect>
        </answer>
        <answer>
          <aId>1</aId>
          <aKey>B</aKey>
          <aPercentValue>0</aPercentValue>
          <aText>B</aText>
          <isCorrect>false</isCorrect>
        </answer>
        <answer>
          <aId>2</aId>
          <aKey>C</aKey>
          <aPercentValue>50</aPercentValue>
          <aText>C</aText>
          <isCorrect>true</isCorrect>
        </answer>
        <answer>
          <aId>3</aId>
          <aKey>D</aKey>
          <aPercentValue>0</aPercentValue>
          <aText>D</aText>
          <isCorrect>false</isCorrect>
        </answer>
      </questionAnswers>
    </QuestionDefinition>
    """


def __qcmsuite_to_qti_121(exoXML, parsed_exo):
    u"""Modele "QCM à la suite" vers QTI 1.2.1 (principalement pour TurningPoint 5)."""
    for index, id_question in enumerate(parsed_exo["list_id_questions"]):
        element_item = ET.SubElement(exoXML, "item",
                                     attrib={"ident" : id_question,
                                             "title" : "%s Question MC #%s" % (parsed_exo["titre"], index + 1)})

        element_metadata = ET.SubElement(element_item, "itemmetadata")
        elementXML = ET.SubElement(element_metadata, "qmd_itemtype")
        elementXML.text = "qcmsuite"
        elementXML = ET.SubElement(element_metadata, "qmd_toolvendor")
        elementXML.text = "Jalon @ http://jalon.unice.fr"

        elementXML = ET.SubElement(element_item, "presentation")
        element_flow = ET.SubElement(elementXML, "flow")
        __add_matttext(element_flow, parsed_exo["enonce%s" % index].decode("utf-8"), flow_type=None)

        # rcardinality (optional - enumerated list: Single, Multiple, Ordered. Default=Single). Indicates the number of responses expected from the user.
        if parsed_exo["anstype"] == "checkbox":
            rcardinality = "Multiple"
        else:
            rcardinality = "Single"

        elementXML = ET.SubElement(element_flow,
                                   "response_lid",
                                   attrib={"ident": "%s_RL" % id_question,
                                           "rcardinality": rcardinality,
                                           "rtiming":      "No"})

        element_renderchoice = ET.SubElement(elementXML,
                                             "render_choice",
                                             attrib={"shuffle": "Yes"})

        element_resprocessing = ET.SubElement(element_item, "resprocessing")
        elementXML = ET.SubElement(element_resprocessing, "outcomes")
        elementXML = ET.SubElement(elementXML, "decvar")

        nb_rep = 0

        dico_reponses = {}
        # answers
        liste_reponses = parsed_exo["reponses%s" % index].split("\n")

        for num_ligne, ligne in enumerate(liste_reponses):
            if num_ligne == 0:
                bonnes_reps = ligne.split(",")
            else:
                nb_rep = nb_rep + 1
                rep_id = "rep_%s" % nb_rep
                # LOG.info("[__qcmsuite_to_qti_121] bonnes_reps = %s" % bonnes_reps)
                if str(num_ligne) in bonnes_reps:
                    # LOG.info("[__qcmsuite_to_qti_121] correct == %s" % num_ligne)
                    type_rep = "Correct"
                    value = "1"  # On donne "+1" par bonne réponse.
                else:
                    type_rep = "Incorrect"
                    value = "0"
                dico_reponses[rep_id] = {"type":        type_rep,
                                         "data":        ligne.decode("utf-8"),
                                         "value":       value,
                                         "feedbacktype": "Response"}

        rep_items = dico_reponses.items()
        shuffle(rep_items)

        for rep_id, rep_item in rep_items:
            elementXML = ET.SubElement(element_renderchoice,
                                       "response_label",
                                       attrib={"ident": rep_id})
            __add_matttext(elementXML, rep_item["data"])

            """ apparament, TP5 ne supporte qu'un varequal par conditionvar.
            Du coup il faut boucler sur respcondition au lieu de varequal..."""
            element_respcondition = ET.SubElement(element_resprocessing,
                                                  "respcondition",
                                                  attrib={"title": rep_item["type"],
                                                          "continue": "Yes"})
            elementXML = ET.SubElement(element_respcondition, "conditionvar")
            elementXML = ET.SubElement(elementXML,
                                       "varequal",
                                       attrib={"respident": id_question})
            elementXML.text = rep_id

            elementXML = ET.SubElement(element_respcondition,
                                       "setvar",
                                       attrib={"action": "Add"})

            elementXML.text = rep_item["value"]
            elementXML = ET.SubElement(element_respcondition,
                                       "displayfeedback",
                                       attrib={"feedbacktype": rep_item["feedbacktype"],
                                               "linkrefid":    "general"})

        # Feedbacks #

        elementXML = ET.SubElement(element_item,
                                   "itemfeedback",
                                   attrib={"ident": "general"})
        __add_matttext(elementXML, parsed_exo["feedback%s" % index].decode("utf-8"))

    return exoXML


def __qcmsuite_to_qti_21(exoXML, parsed_exo):
    # Modele "QCM a la Suite" vers QTI 2.1:

    if parsed_exo["anstype"] == "checkbox":
        cardinality = "multiple"
    else:
        cardinality = "single"

    for index, id_question in enumerate(parsed_exo["list_id_questions"]):

        assessmentItem = ET.SubElement(exoXML,
                                       "assessmentItem",
                                       attrib={"identifier"        : id_question,
                                               "title"             : parsed_exo["titre"],
                                               "adaptive"          : "false",
                                               "timeDependent"     : "false"})

        elementXML = ET.SubElement(assessmentItem,
                                   "responseDeclaration",
                                   attrib={"identifier":  "RESPONSE",
                                           "cardinality": cardinality,
                                           "baseType":    "identifier"})

        correctResponse = ET.SubElement(elementXML, "correctResponse")

        elementXML = ET.SubElement(assessmentItem,
                                   "outcomeDeclaration",
                                   attrib={"identifier":  "SCORE",
                                           "cardinality": "single",
                                           "baseType":    "float"})

        elementXML = ET.SubElement(assessmentItem, "itemBody")
        choiceInteraction = ET.SubElement(elementXML,
                                          "choiceInteraction",
                                          attrib={"responseIdentifier": "RESPONSE",
                                                  "shuffle":            "true",
                                                  "maxChoices":         "0"})

        elementXML = ET.SubElement(choiceInteraction, "prompt")
        elementXML.text = parsed_exo["enonce%s" % index].decode("utf-8")

        liste_reponses = parsed_exo["reponses%s" % index].split("\n")
        for num_ligne, ligne in enumerate(liste_reponses):
            if num_ligne == 0:
                bonnes_reps = ligne.split(",")
            else:
                rep = ligne.strip()
                if rep != "":
                    rep_id = "rep_%s" % num_ligne
                    if str(num_ligne) in bonnes_reps:
                        elementXML = ET.SubElement(correctResponse, "value")
                        elementXML.text = rep_id
                    elementXML = ET.SubElement(choiceInteraction,
                                               "simpleChoice",
                                               attrib={"identifier": rep_id,
                                                       "fixed":      "false"})
                    elementXML.text = rep.decode("utf-8")

        if parsed_exo["feedback%s" % index] != "":
            elementXML = ET.SubElement(assessmentItem,
                                       "modalFeedback",
                                       attrib={"outcomeIdentifier": "FEEDBACK",
                                               "identifier": "COMMENT",
                                               "showHide": "show"})
            elementXML.text = parsed_exo["feedback%s" % index].decode("utf-8")
        elementXML = ET.SubElement(assessmentItem, "responseProcessing", attrib={"template": "http://www.imsglobal.org/question/qti_v2p1/rptemplates/match_correct"})
    return exoXML


def __randomize_responses_qcmsimple(liste_bons, liste_mauvais):
    # Renvoit un tuple mélangeant les 2 listes en parametres

    liste_bons = liste_bons.decode("utf-8").split("\n")
    liste_mauvais = liste_mauvais.decode("utf-8").split("\n")

    dico_reponses = {}
    nb_rep = 0
    # Correct answers #
    for ligne in liste_bons:
        rep = ligne.strip()
        if rep != "":
            nb_rep = nb_rep + 1
            rep_id = "rep_%s" % nb_rep

            dico_reponses[rep_id] = {"type": "Correct",
                                     "data": rep,
                                     "value": "1",  # On donne "+1" par bonne réponse.
                                     }
    # Incorrect answers #
    liste_mauvais
    for ligne in liste_mauvais:
        rep = ligne.strip()
        if rep != "":
            nb_rep = nb_rep + 1
            rep_id = "rep_%s" % nb_rep
            dico_reponses[rep_id] = {"type": "Incorrect",
                                     "data": rep,
                                     "value": "0",  # On donne "0" par mauvaise réponse.
                                     }

    # Vu que TurningPoint 5 est incapable de faire de l'aléatoire, on mélange les propositions...
    rep_items = dico_reponses.items()
    shuffle(rep_items)
    return rep_items
