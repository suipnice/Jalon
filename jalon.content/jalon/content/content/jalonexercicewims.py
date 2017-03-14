# -*- coding: utf-8 -*-
"""jalonexercicewims."""
from zope.interface import implements
from Products.Archetypes import public as atpublic
from Products.ATContentTypes.content.document import ATDocumentBase, ATDocumentSchema
from Products.ATContentTypes.content.base import registerATCT
# from Products.CMFCore.utils import getToolByName

from jalon.content import contentMessageFactory as _
from jalon.content.config import PROJECTNAME
from jalon.content.interfaces import IJalonExerciceWims

from urlparse import urlparse

import jalon_utils
import re

import json
from copy import deepcopy

from logging import getLogger
LOG = getLogger('[JalonExerciceWims]')

JalonExerciceWimsSchema = ATDocumentSchema.copy() + atpublic.Schema((
    atpublic.StringField(
        'modele',
        required=False,
        accessor='getModele',
        searchable=False,
        widget=atpublic.StringWidget(
            label=_(u"Modèle CreateExo de Wims")
        )),
    atpublic.StringField(
        'permalink',
        required=False,
        accessor='getPermalink',
        searchable=False,
        widget=atpublic.StringWidget(
            label=_(u"Permalien d'un exercice wims publié")
        )),
    atpublic.StringField(
        'qnum',
        required=False,
        accessor='getQnum',
        searchable=False,
        widget=atpublic.StringWidget(
            label=_(u"Nombre d'exercices de la sélection aléatoire auxquels l'étudiant doit répondre. (dans le cas d'un groupe d'exercices)")
        )),
    atpublic.LinesField(
        "listeIdsExos",
        required=False,
        accessor="getListeIdsExos",
        searchable=False,
        widget=atpublic.LinesWidget(
            label=_(u"Liste de tous les exercices de la sélection aléatoire (dans le cas d'un groupe d'exercices)."),
            visible={'view': 'visible', 'edit': 'invisible'},
        )),
))


class JalonExerciceWims(ATDocumentBase):
    """Un Exercice Wims de Mon Espace."""

    implements(IJalonExerciceWims)
    meta_type = 'JalonExerciceWims'
    schema = JalonExerciceWimsSchema
    schema['description'].required = False
    schema['description'].mode = "r"
    schema['text'].required = False
    schema['text'].mode = "r"

    def getBreadcrumbs(self, edit_mode=False):
        """Fournit le fil d'ariane de l'exercice courant."""
        # LOG.info("----- getBreadcrumbs -----")
        portal_url = self.portal_url.getPortalObject().absolute_url()
        crumbs_list = [{"title" : _(u"Mes ressources"),
                        "icon"  : "fa fa-folder-open",
                        "link" : "%s/mes_ressources" % portal_url},
                       {"title": _(u"Mes exercices WIMS"),
                        "icon" : "fa fa-random",
                        "link" : "%s/mes_ressources/mes_exercices_wims" % portal_url},
                       {"title": self.Title(),
                        "icon" : "fa fa-random",
                        "link" : "%s/view" % self.absolute_url()}]
        if edit_mode:
            crumbs_list.append({"title": "édition",
                                "icon" : "fa fa-edit",
                                "link" : "%s/edit_wims_exercice_form" % self.absolute_url()})

        return crumbs_list

    def getIconClass(self):
        """Return the Exercice icon CSS class."""
        # LOG.info("----- getIconClass -----")
        return "fa fa-random"

    def getEditWimsExerciceMacroName(self):
        """Renvoie le nom de la macro qui permet d'editer l'exercice, en fonction du modele."""
        # LOG.info("----- getEditWimsExerciceMacroName -----")
        edit_wims_exercice_macro_name = "edit_wims_exercice_createxo"
        if self.getModele() == "externe":
            edit_wims_exercice_macro_name = "edit_wims_exercice_externe"
        return edit_wims_exercice_macro_name

    def getVariablesDefaut(self, modele):
        """Liste les valeurs par defaut a definir en fonction du modele d'exercice."""
        # LOG.info("----- getVariablesDefaut -----")
        variables_defaut = {"exercicelibre":{},
                            "qcmsimple":
                                {"enonce"          : "Cochez la(les) bonne(s) réponse(s).",
                                 "bonnesrep"       : "bon choix n°1\nbon choix n°2",
                                 "mauvaisesrep"    : "mauvais choix n°1\nmauvais choix n°2",
                                 "tot"             : "5",
                                 "givetrue"        : "2",
                                 "minfalse"        : "0",
                                 "feedback_general": "",
                                 "feedback_bon"    : "",
                                 "feedback_mauvais": "",
                                 "options"         : "checkbox split",
                                 "accolade"        : "1",
                                 "credits"         : "",
                                 "hint"            : "",
                                 "help"            : "",
                                 },
                            "equation":
                                {"precision"    : "1000",
                                 "param_a"      : "randint(1..20)",
                                 "param_b"      : "randint(1..5)",
                                 "param_c"      : "0",
                                 "param_d"      : "0",
                                 "param_e"      : "0",
                                 "equation"     : "\\a * \\b",
                                 "enonce"       : "Je vend \\a chaussette(s) au prix de \\b euros chacune. Quel est le montant de ma vente ?",
                                 "texte_reponse": "Ma réponse",
                                 "accolade"     : "2",
                                 },
                            "texteatrous":
                                {"type_rep"     : "atext",
                                 "donnees"      : "Le texte ci-dessous est incomplet. Remplissez les trous.\n\
<br/>\nL'Université de Nice fut officiellement instituée par décret du 23 octobre ??1965??.\n\
Néanmoins, ses racines historiques remontent au XVIIème siècle, avec le fameux ??Collegium jurisconsultorum niciensium, Collegius niciensius??\n\
crée en ??1639?? par les Princes de Savoie ; il comprenait un important corps de jurisconsultes et sa notoriété dura jusqu'au rattachement de Nice à la France, en ??1860,1870,1850,1840??.\n\
Au XVIIème siècle, une École de ??Médecine, Couture, Danse, Chimie?? dispensa des enseignements appréciés dans toute l'Europe.\n",
                                 "feedback_general": "",
                                 "feedback_bon"    : "",
                                 "feedback_mauvais": "",
                                 "credits"         : "",
                                 "accolade"        : "1",
                                 "list_order"      : "1",
                                 },
                            "marqueruntexte":
                                {"minmark"  : "1",
                                 "maxmark"  : "8",
                                 "data"     : "{Jack,Jean,Louis,Michel,Pierre} ??et,est?? forain, il \n\
??{tien,tiens} ,tient?? ??un,une?? baraque de tir ??a,à?? la noix de coco.\n\
??Ont,On?? ??trouvent,trouve?? des ??Baraque,Baraques?? à noix de Coco dans ??tous,toutes?? les foires.\n\
Les ??,gens?? ??arrive,arrivent??, ??donne,donnent?? des ??,sous??\n\
??est,et?? ??envoie,envoient?? des ??,boules?? sur une noix de coco \n\
??{poser,posé} ,posée?? en haut d'une ??,colonne??.\n\
Ceux qui ??fait,font?? ??{dégringolé,dégringolée} ,dégringoler?? une noix de coco \n\
??{peu,peut,peux} ,peuvent?? ??{le,les} ,la?? ??{gardée,gardé} ,garder??.\n;\
\n\
\n??{Quel,Quels,Quelles} ,Quelle?? idée ??est-je,ai-je??\n\
??{d'acheté,d'achetée,d'achetés} ,d'acheter?? ??{cept,cette,ces,ce} ,cet?? oiseau ?\n\
L'oiselier me dit : <blockquote>« ??{S'est,Cet} ,C'est?? un ??{mal,malle} ,mâle??.\n\
??Attender,Attendez?? une ??,semaine?? qu'il \n\
??{s'abitue,s'abituent,s'habituent} ,s'habitue??, ??est,et?? il chantera. »</blockquote>\n\
??Hors,Or??, l'oiseau ??sobstine,s'obstine?? ??a,à?? ??ce,se?? \n\
??tait,taire?? et il ??fais,fait?? ??tous,tout?? de ??{traver,travert} ,travers??.\n;\
\n\
\nLes ??désert,déserts?? de ??sables,sable?? ??occupe,occupent?? de\n\
??large,larges?? parties {de la planète,du monde,de la Terre} .\n\
Il n'y ??{pleu,pleus,pleuvent} ,pleut?? presque ??,pas??.<br/>\n\
Très ??peut,peu?? de plantes et ??,d'animaux?? y ??vit,vivent??.\n\
Les ??,dunes?? ??son,sont?? des collines de ??,sable?? que le vent ??à,a??\n\
??{construit,construits,construite} ,construites??.<br/>\n\
Les ??grains,graines?? de ??{certain,certaine,certains} ,certaines??\n\
plantes ??reste,restent?? sous le ??sole,sol?? du désert pendant des années.\n\
??{Ils,Elle} ,Elles?? ??ce,se?? ??met,mettent?? ??a,à?? ??{poussées,poussée,poussés} ,pousser?? dès qu'il y a ??une,un?? orage.\n;",
                                 "pre"      : "Marquez les fautes d'orthographe dans le texte ci-dessous.",
                                 "post"     : "",
                                 "options"  : "split"
                                 },
                            "marquerparpropriete":
                                {"explain"      : "Parmi les joueurs de football ci-dessous, marquez ceux qui sont dans l'équipe \prop.",
                                 "prop"         : "française, italienne, allemande",
                                 "data"         : "Fabien Barthez , francaise\nLilian Thuram , francaise\nClaude Makélélé , francaise\nZinedine Zidane , francaise\nFranck Ribéry , francaise\nThierry Henry , francaise\nDavid Trézéguet , francaise\n\
Gianluigi Buffon , italienne\nMorgan De Sanctis , italienne\nAngelo Peruzzi , italienne\nChristian Abbiati , italienne\nMarco Amelia , italienne\n\
Jens Lehmann , allemande\nOliver Kahn , allemande\nTimo Hildebrand , allemande\nPhilipp Lahm , allemande\nArne Friedrich , allemande\n",
                                 "tot"          : "12",
                                 "mingood"      : "1",
                                 "minbad"       : "4",
                                 "options"      : "split",
                                 "presentation" : "liste"
                                 },
                            "questiontextuelletolerante":
                                {"len"          : "20",
                                 "data"         : "l'intensité est : ??ampère??;\nla tension est : ??volt??;\nla résistance est : ??ohm??;\nla capacité d'un condensateur est : ??farad??. Son symbole est : ??F??;\nl'inductance d'un solénoïde est : ??henri??;\nla puissance dissipée sur une composante est : ??watt??;\nla fréquence est : ??hertz??. Son symbole est : ??Hz??;",
                                 "atype"        : "atext",
                                 "include_good" : "oui",
                                 "words"        : "électricité intensité courant tension capacité puissance fréquence",
                                 "pre"          : "En électricité, l'unité de base pour mesurer ",
                                 "post"         : "."
                                 },
                            "taperlemotassocie":
                                {"size"     : "20",
                                 "words"    : "bambou,bambous\nbijou,bijoux\ncadeau,cadeaux\ncaillou,cailloux\ncheval,chevaux\nchou,choux\nciel,cieux\nclou,clous",
                                 "type_rep" : "atext",
                                 "explain"  : "Tapez le pluriel du nom \\name :",
                                 },
                            "reordonner":
                                {"tot"      : "6",
                                 "size"     : "80x50",
                                 "data"     : "Mercure, Vénus, Terre, Mars, Jupiter, Saturne, Uranus, Neptune",
                                 "explain"  : "Mettre les planètes suivantes du système solaire dans le bon ordre, avec la plus proche du Soleil en premier."
                                 },
                            "correspondance":
                                {"tot"             : "6",
                                 "sizev"           : "50",
                                 "sizer"           : "250",
                                 "sizel"           : "250",
                                 "feedback_general": "",
                                 "data"            : "L'Allemagne, Berlin\nL'Australie, Canberra\nLe Canada, Ottawa\nLa Chine, Beijing\nL'Espagne, Madrid\nLes Etats-Unis, Washington\nLa France, Paris\nLa Grande Bretagne, Londres\nL'Inde, New Delhi\nL'Indonésie, Jakarta\nL'Italie, Rome\nLe Japon, Tokyo\nLa Russie, Moscou",
                                 "explain"         : "Établissez la correspondance entre les pays et leurs capitales.",
                                 "accolade"        : "1",
                                 },
                            "classerparpropriete":
                                {"tot"      : "8",
                                 "max1"     : "4",
                                 "size1"    : "120x120",
                                 "prop"     : "Oiseau, Mammifère",
                                 "data"     : "L'aigle, Oiseau\nL'albatros, Oiseau\nL'alouette, Oiseau\nLe canard, Oiseau\nLe corbeau, Oiseau\nLe faucon, Oiseau\nLe goéland, Oiseau\n\
\nLe lion, Mammifère\nL'éléphant, Mammifère\nLe chat <img src='http://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Black_hills_cat-tochichi.jpg/120px-Black_hills_cat-tochichi.jpg' alt='photo d'un chat'/>, Mammifère\nLe cheval, Mammifère\nLe chien, Mammifère\nLe cochon, Mammifère\nLa vache, Mammifère",
                                 "shuffle"  : "shuffle",
                                 "explain"  : "Classez les animaux ci-dessous selon leurs catégories.",
                                 "post"     : "",
                                 "estun"    : "est un",
                                 "noclass"  : "n'appartient à aucune catégorie",
                                 "feedback_general": ""
                                 },
                            "vraifauxmultiples":
                                {"tot"      : "4",
                                 "mintrue"  : "1",
                                 "minfalse" : "1",
                                 "datatrue" : "À tension égale, le courant passant par un résistor est inversement proportionnel à sa résistance.\nÀ courant égal, la tension sur un résistor est proportionnelle à sa résistance.\nLe courant passant par un résistor est proportionnel à la tension appliquée.\nLa puissance dissipée par un résistor est proportionnelle au carré de la tension appliquée.\nLa puissance dissipée par un résistor est proportionnelle au carré du courant.",
                                 "datafalse": "À tension alternative égale, le courant passant par un condensateur est inversement proportionnel à la capacité.\n\
À tension alternative égale, le courant passant par un condensateur est indépendant de la capacité.\n\
À tension alternative égale, le courant passant par un solénoïde est proportionnel à l'inductance.\n\
À tension continue égale, le courant passant par un condensateur est proportionnel à la capacité.\n\
À tension égale, le courant passant par un résistor est proportionnel à sa résistance.\n\
À tension égale, le courant passant par un résistor est indépendant de sa résistance.\n\
Le courant passant par une diode est proportionnel à la tension appliquée.\n\
La puissance dissipée par un résistor est proportionnelle à la tension appliquée.\n\
La puissance dissipée par un résistor est proportionnelle au courant.\n\
La puissance dissipée par un condensateur est proportionnelle {à,au carré de} la tension appliquée.\n\
La puissance dissipée par un condensateur est proportionnelle {au,au carré du} courant.\n\
La puissance dissipée par un solénoïde idéal est proportionnelle {à,au carré de} la tension appliquée.\n\
La puissance dissipée par un solénoïde idéal est proportionnelle {au,au carré du} courant.",
                                 "options"         : "split",
                                 "explain"         : "Parmi les affirmations suivantes, cochez les phrases vraies.",
                                 "accolade"        : "1",
                                 "feedback_general": "",
                                 "credits"         : "",
                                 "hint"            : "",
                                 "help"            : "",
                                 },
                            "texteatrousmultiples":
                                {"data"             : "Le début officiel de la Seconde Guerre Mondiale est marqué par\n\
??la déclaration de guerre,l'offensive?? de\n\
??la Grande Bretagne et la France,la France,la Grande Bretagne,l'Allemagne,l'Union Soviétique??\n\
contre ??l'Allemagne,la Pologne,l'Union Soviétique,la France??.\n;\n\
La Seconde Guerre Mondiale s'est déroulée entre ??1939?? et ??1945??.\n\
;\n\
??La Grande Bretagne et la France ont,La France a,La Grande Bretagne a,Les États-Unis ont,L'Union Soviétique a?? \n\
déclaré la guerre contre l'Allemagne en ??1939?? à la suite de l'envahissement de ??la Pologne?? par cette dernière.\n\
;\n\
Pendant la Seconde Guerre Mondiale, l'Espagne sous ??Francisco Franco|[F.|Francisco|] Franco?? est un pays\n\
??neutre,axe,allié,envahi??.\n;\n??Après avoir battu,Avant d'attaquer?? la France,\n\
{l'Allemagne,Hitler,l'Allemagne Nazie} a lancé une attaque surprise contre l'URSS en\n\
??décembre,{novembre,octobre},{septembre,août,juillet},{juin,mai,avril},{mars,février,janvier}??\n\
??1940??, sous le nom {du plan,de l'opération} ??Barbarossa??.",
                                 "pre"              : "Completez le texte suivant :",
                                 "post"             : "",
                                 "feedback_general" : "",
                                 "type_rep"         : "atext",
                                 "credits"          : "",
                                 "hint"             : "",
                                 "help"             : "",
                                 },
                             "qcmsuite":
                                {"list_id_questions": "data1 data2",
                                 "instruction"                : "Instruction globale : Répondez à chaque question d'une première série, validez, puis répondez aux questions de la seconde série.",
                                 "alea"                       : "yes",
                                 "nb_questions_max"           : "10",
                                 "nb_etapes"                  : "1",
                                 "pourcentage_validation"     : "0",
                                 "accolade"                   : "1",
                                 "questions"                  : "*-*text{data1=Énoncé de la Question 1\nFeedback affiché une fois la réponse à la question 1 envoyée\n\
1\nProposition 1\nProposition 2\nProposition 3\nProposition 4}\n\n\
:Question 2\n\n*-*text{data2=En quelle année eut lieu la bataille de Marignan ?\n\
Marignan fut la première victoire du jeune roi François Ier, la première année de son règne.\n\
1\n1515\n1414\n1313\n1616}",
                                 "boucle_data_q"              : "*-*text{data_q=\data1!= ? 1:}\n*-*text{data_q=\data2!= ? wims(append item 2 to \data_q)}",
                                 "boucle_battage"             : "*-*text{QUEST=*-*battage[\i]=1? \data1}\n *-*text{QUEST=*-*battage[\i]=2? \data2}",
                                 "boucle_answer"              : "*-*answer{}{\REP1;\CHOIX[1;]}{type=*-*anstype}{option=\option}\n*-*answer{}{\REP2;\CHOIX[2;]}{type=*-*anstype}{option=\option}",
                                 "boucle_matrix_rep"          : "\matrix{REP = \REP1\n\REP2}",
                                 "boucle_condition_questions" : "\condition{Question 1 : Aucune mauvaise réponse }{\TEST[1;3]=0}\n\
                                                                 \condition{Question 1 : Tout juste }{\TEST[1;1]=0 and \TEST[1;2]=0 and \TEST[1;3]=0}\n\
                                                                 \condition{Question 2 : Aucune mauvaise réponse }{\TEST[2;3]=0 and \step >=\CONDSTEP[2]}\n\
                                                                 \condition{Question 2 : Tout juste }{\TEST[2;1]=0 and \TEST[2;2]=0 and \TEST[2;3]=0 and \step >=\CONDSTEP[2]}",
                                 "credits"                    : "",
                                 "columns"                    : "1",
                                 "anstype"                    : "checkbox",
                                 "answer_given"               : "2",
                                 }
                            }
        if modele in variables_defaut:
            return variables_defaut[modele]
        else:
            return None

    def addExoWims(self, idobj=None, title=None, author_id=None, modele=None, form=None, sandbox=False):
        """Ajoute ou modifie un exercice wims."""
        # LOG.info("----- addExoWims (sandbox=%s)-----" % sandbox)
        title = self.formaterTitreWIMS(title)
        member = self.portal_membership.getMemberById(author_id)
        auth_email = member.getProperty("email")
        if not auth_email:
            auth_email = str(member.getProperty("mail"))
        fullname = member.getProperty("fullname")
        if not fullname:
            fullname = member.getProperty("displayName")

        source = str(getattr(self, "modele_%s.oef" % modele))
        # LOG.info("addExoWims / original source=\n%s" % source)
        # La source de départ contient des caracteres html echapés, qu'il faut rétablir avant de les renvoyer à WIMS.
        source = source.replace("&amp;", "&")
        source = source.replace("&lt;", "<")
        source = source.replace("&gt;", ">")
        source = source.replace("&quot;", '"')

        # on souhaite conserver certains '&quot;'
        source = source.replace("$$quot;", '&quot;')

        variables_base = {"author": fullname, "email": auth_email, "title": title}
        variables_modele = self.getVariablesDefaut(modele)
        # ajoute les variables communes aux variables du modele
        variables_modele.update(variables_base)

        # dico contiendra les parametres a envoyer a WIMS
        dico = {"authMember": author_id, "qexo": idobj}
        dico["qclass"] = "%s_1" % self.aq_parent.getComplement()
        # LOG.info("[addExoWims] qclass=%s" % dico["qclass"])
        # Cas d'une creation
        if not form:
            if modele == "groupe":
                return self.ajouterSerie(author_id)

            param = variables_modele
            if modele == "exercicelibre":
                for key in param.keys():
                    source = source.replace("$$%s$$" % key, param[key])
                    param["exercicelibre"] = source
            if param is None:
                # LOG.error("addExoWims / getVariablesDefaut return None")
                return None

        # Cas d'une modification (ou d'un import)
        else:
            # On copie le formulaire pour éviter de le modifier
            param = deepcopy(form)
            if "option" in param:
                # Dans le cas d'une modification, option devrait toujours contenir "force_rewrite" à priori
                # Si "option" n'est pas défini, c'est qu'on fait un import.
                dico["option"] = param["option"]

            if "options" in param and type(param["options"]) is list:
                param["options"] = " ".join(param["options"])
            if modele == "qcmsuite":
                nb_questions = 1
                for key in param.keys():
                    if key.startswith("enonce"):
                        nb_questions = nb_questions + 1
                list_id_questions = ["data1"]

                questions = [self.genererDataQuestionSuite(param["enonce0"], param["feedback0"], param["reponses0"], 1)]

                boucle_data_q = ["*-*text{data_q=\data1!= ? 1:}"]
                boucle_battage = [" *-*matrix{QUEST=*-*battage[\i]=1? \data1}"]
                boucle_answer = ["*-*answer{}{\REP1;\CHOIX[1;]}{type=*-*anstype}{option=\option}"]
                boucle_matrix_rep = ["\matrix{REP = \REP1"]
                boucle_condition_questions = ["\condition{Question 1 : Aucune mauvaise réponse }{\TEST[1;3]=0}", "\condition{Question 1 : Tout juste }{\TEST[1;3]=0 and (\\anstype issametext radio or (\TEST[1;2]=0 and \TEST[1;1]=0))}"]
                for i in range(2, nb_questions):
                    list_id_questions.append("data%s" % str(i))
                    questions.append(":Question %s" % str(i))

                    question_string = self.genererDataQuestionSuite(param["enonce%s" % str(i - 1)],
                                                                    param["feedback%s" % str(i - 1)],
                                                                    param["reponses%s" % str(i - 1)],
                                                                    i)
                    questions.append(question_string)

                    boucle_data_q.append("*-*text{data_q=\data%s!= ? wims(append item %s to \data_q)}" % (str(i), str(i)))
                    boucle_battage.append(" *-*matrix{QUEST=*-*battage[\i]=%s? \data%s}" % (str(i), str(i)))
                    boucle_answer.append("*-*answer{}{\REP%s;\CHOIX[%s;]}{type=*-*anstype}{option=\option}" % (str(i), str(i)))
                    boucle_matrix_rep.append("\REP%s" % str(i))
                    boucle_condition_questions.append("\condition{Question %s : Aucune mauvaise réponse }{\TEST[%s;3]=0 and \step >=\CONDSTEP[%s]}" % (str(i),  str(i), str(i)))
                    boucle_condition_questions.append("\condition{Question %s : Tout juste }{\TEST[%s;3]=0 and (\\anstype issametext radio or (\TEST[%s;2]=0 and \TEST[%s;1]=0)) and \step >=\CONDSTEP[%s]}" % (str(i), str(i),  str(i), str(i), str(i)))

                boucle_matrix_rep[-1] = "%s}" % boucle_matrix_rep[-1]
                param["list_id_questions"] = " ".join(list_id_questions)
                param["questions"] = "\n".join(questions)
                param["boucle_data_q"] = "\n".join(boucle_data_q)
                param["boucle_battage"] = "\n".join(boucle_battage)
                param["boucle_answer"] = "\n".join(boucle_answer)
                param["boucle_matrix_rep"] = "\n".join(boucle_matrix_rep)
                param["boucle_condition_questions"] = "\n".join(boucle_condition_questions)

        self.listeIdsGroupes = [0]

        # wims = getToolByName(self, "portal_wims")
        if modele == "exercicelibre":
            try:
                dico["source"] = param["exercicelibre"].decode("utf-8").encode("iso-8859-1")
            except:
                dico["source"] = param["exercicelibre"]

            if sandbox:
                dico["sandbox"] = True
            # result = json.loads(self.aq_parent.wims("callJob", dico))
            return self.aq_parent.wims("creerExercice", dico)
        else:
            param.update(variables_base)

            for key in variables_modele:
                if key in param:
                    # Le parametre a été envoyé par le formulaire
                    try:
                        param[key].decode("utf-8")
                    except:
                        LOG.info("[addExoWims] - Chaine non UTF-8 envoyee : %s" % key)
                        LOG.info(param[key])

                    try:
                        source = source.replace("$$%s$$" % key, param[key])
                    except UnicodeDecodeError:
                        # typiquement, dans le cas de l'admin par exemple, son nom est en unicode, pas utf-8
                        source = source.replace("$$%s$$" % key, param[key].encode("utf-8"))
                        """print e
                        LOG.info("[addExoWims] - UnicodeDecodeError")
                        LOG.info("[addExoWims] param[%s] = '%s'" % (key, param[key]))
                        #return None"""
                else:
                    # Si la variable n'est pas fournie par le formulaire, on la place à vide
                    # (cas des checkboxes décochées par exemple)
                    source = source.replace("$$%s$$" % key, "")
            # source = source.replace("--nbsp;", "&nbsp;")
            source = source.replace("*-*", "\\")

            # iso-8859-1 ne permet pas d'encoder certains caracteres speciaux comme œ ou €
            # attention : cela ajoute des ";" qui peuvent nuire à certains modèle d'exos (QCM suite par exemple)
            # pour ces derniers, on pourrait convertir chaque champ compatible ?
            if modele not in ["qcmsuite"]:
                source = jalon_utils.convertUTF8ToHTMLEntities(source)

            # try:
            # on ne peux pas empecher la creation d'un exercice pour une erreur d'encodage. on ignore donc les caracteres non reconnus.
            source = source.decode("utf-8").encode("iso-8859-1", "ignore")
            # except:
            #   print "Caractere non reconnu dans creerExercice WIMS (utility.py)"
            #  pass
            # print "utility/creerExercice qexo: %s" % param["qexo"]
            dico["source"] = source

            if sandbox:
                dico["sandbox"] = True
            retour = self.aq_parent.wims("creerExercice", dico)
            # Cas ou on modifie un modele qcm suite
            if form and modele == "qcmsuite":
                retour["list_id_questions"] = list_id_questions
            return retour

    def genererDataQuestionSuite(self, enonce, feedback, reponses, id_question):
        u"""Genere une chaine au format spécifique des questions du modele "QCM Suite"."""
        # LOG.info("----- genererDataQuestionSuite -----")
        enonce = enonce.replace("\n", "<br/>")
        # Si la premiere ligne contient "Qtitle", alors on ne remplace pas le premier saut de ligne
        if enonce.startswith("Qtitle"):
            enonce = enonce.replace("<br/>", "\n", 1)

        feedback = feedback.replace("\n", "<br/>")

        return "*-*text{data%s=asis(%s\n%s\n%s)}" % (str(id_question), enonce, feedback , reponses)

    def ajouterSerie(self, author):
        """Ajoute un groupe d'exercices wims."""
        # LOG.info("----- ajouterSerie -----")
        liste_exos = self.getListeIdsExos()
        if len(liste_exos) > 0:
            # qclass = "%s_1" % self.aq_parent.getComplement()
            # rep = json.loads(self.aq_parent.wims("callJob", {"job": "checksheet", "code": author, "qclass": qclass, "qsheet": "1"}))
            # if rep["status"] == "ERROR":
            #    self.aq_parent.wims("creerFeuille", {"authMember": author, "qclass": qclass, "title": "Feuille de tests des sélections aléatoires", "description": ""})
            for exo_id in liste_exos:
                exo = getattr(self.aq_parent, exo_id)
                if exo.getModele() != "groupe":
                    exo.addRelatedItem(self)

            return {"status": "OK", "code": "GROUP_ADDED"}

            # return self.aq_parent.wims("lierExoFeuille", {"listeExos": self.getListeIdsExos(), "qnum": self.getQnum(), "title": self.Title(), "authMember": author, "qclass": qclass, "qsheet": "1"})
        else:
            return {"status": "ERROR", "err_code": "NO_EXERCICE", "message": _(u"Aucun exercice selectionné")}

    def supprimerSerie(self):
        """Supprime un groupe d'exercices wims."""
        # LOG.info("----- supprimerSerie -----")
        liste_exos = self.getListeIdsExos()
        if len(liste_exos) > 0:
            for exo_id in liste_exos:
                exo = getattr(self.aq_parent, exo_id, None)
                if exo:
                    exo.removeRelatedItem(self)

            return {"status": "OK", "code": "GROUP_ADDED"}
        else:
            return {"status": "ERROR", "code": "NO_EXERCICE"}

    def ajouterTag(self, tag):
        """ajoute Tag."""
        # LOG.info("----- ajouterTag -----")
        return jalon_utils.setTag(self, tag)

    def authUser(self, quser=None, qclass=None, request=None):
        """AuthUser WIMS : permet d'authentifier "quser" dans une classe wims "qclass"."""
        # LOG.info("----- authUser -----")
        return jalon_utils.authUser(self.aq_parent, quser, qclass, request)

    def delExoWims(self):
        u"""Supprime l'exercice wims courant sur le serveur WIMS.

        La suppression coté jalon se fait ensuite dans folder_delete.cpy

        """
        # LOG.info("----- delExoWims -----")
        qclass = "%s_1" % self.aq_parent.getComplement()
        author = self.portal_membership.getAuthenticatedMember().getId()
        qexo = self.getId()
        modele = self.getModele()

        if modele == "groupe":
            retour = self.supprimerSerie()
        elif modele == "externe":
            retour = "TODO"
        else:
            dico = {"job": "delexo", "code": author, "qclass": qclass, "qexo": qexo}
            rep_wims = self.aq_parent.wims("callJob", dico)
            retour = self.aq_parent.wims("verifierRetourWims", {"rep": rep_wims, "fonction": "jalonexercicewims.py/delExoWims", "message": "suppression d'un exo de Mes ressources", "requete": dico})
        return retour

    def lister_modules_wims(self, authMember, module_path="/"):
        u"""Liste tous les modules wims publiés sous le niveau "module_path"."""
        # LOG.info("----- lister_modules_wims -----")
        dico = {"job": "listmodules", "option": module_path, "code": authMember}
        rep_wims = self.aq_parent.wims("callJob", dico)
        return self.aq_parent.wims("verifierRetourWims", {"rep": rep_wims, "fonction": "jalonexercicewims.py/lister_modules_wims", "message": "demande une Liste de modules wims publiés ", "requete": dico})

    def getExoXML(self, formatXML="OLX", version="latest"):
        """Appelle la fonction getExoXML de jalonexportswims."""
        # LOG.info("----- getExoXML -----")
        import jalonexportswims
        return jalonexportswims.getExoXML(context=self, formatXML=formatXML, version=version)

    def getExoZIP(self, filename_path, exo_donnees):
        """Appelle la fonction getExoXML de jalonexportswims."""
        # LOG.info("----- getExoZIP -----")
        import jalonexportswims
        return jalonexportswims.getExoZIP(filename_path=filename_path, exo_donnees=exo_donnees)

    def getListeExports(self):
        u"""Fournit la liste des formats exportables a partir du modèle courant."""
        # LOG.info("----- getListeExports -----")
        liste_formats = {"qcmsimple":                  ["QTI", "OLX", "OEF", "FLL"],
                         "equation":                   ["OEF"],
                         "texteatrous":                ["OEF"],
                         "marqueruntexte":             ["OEF"],
                         "marquerparpropriete":        ["OEF"],
                         "questiontextuelletolerante": ["OEF"],
                         "taperlemotassocie":          ["OEF"],
                         "reordonner":                 ["OEF"],
                         "correspondance":             ["OEF"],
                         "classerparpropriete":        ["OEF"],
                         "vraifauxmultiples":          ["OEF"],
                         "texteatrousmultiples":       ["OEF"],
                         "qcmsuite":                   ["QTI", "OEF"]
                         }
        if self.modele in liste_formats:
            return liste_formats[self.modele]
        else:
            return []

    def getModule(self, authMember, module_path):
        """retourne toutes les infos disponibles pour le module "module_path"."""
        # LOG.info("----- getModule -----")
        dico = {"job": "getmodule", "option": module_path, "code": authMember}
        rep_wims = self.aq_parent.wims("callJob", dico)
        return self.aq_parent.wims("verifierRetourWims", {"rep": rep_wims, "fonction": "jalonexercicewims.py/getModule", "message": "demande les infos d'un module", "requete": dico})

    def getTypeWims(self):
        """Retourne le type d'element (exercice / groupe)."""
        # LOG.info("----- getTypeWims -----")
        if self.modele == "groupe":
            return "Groupe"
        else:
            return "Exercice"

    def cleanData(self, input_data):
        """clean Data."""
        # Il faut verifier quelques points à l'interieur des parametres :
        # 1/ attention aux caracteres speciaux
        # 2/ attention aux }\n qui pourraient etre contenus.
        #   1ere Solution envisagee ==> remplacer "}" par "&#125;" ? ==> non car le code doit etre interprete par wims.
        #   2e solution ==> remplacer "}\n" par  "}\t\n". Les \t ne seront pas affiches en HTML
        # LOG.info("----- cleanData -----")
        input_data = input_data.replace("\r\n", "\n")
        input_data = input_data.replace("\r", "\n")
        input_data = input_data.replace("\n\n", "\n")
        input_data = input_data.replace("  ", " ")
        input_data = input_data.replace("}\n", "}\t\n")
        input_data = input_data.replace("}", "}\t")
        input_data = input_data.replace("\t\t", "\t")

        return input_data

    def getExoOEF(self, modele, authMember, requete={}):
        """permet d'obtenir le code source brut (OEF) d'un exercice WIMS."""
        # LOG.info("----- getExoOEF -----")
        fichier = self.aq_parent.wims("callJob", {"job": "getexofile", "qclass": "%s_1" % self.aq_parent.getComplement(), "qexo": self.getId(), "code": authMember})
        try:
            json.loads(fichier)
            # LOG.error("[getExoOEF] ERREUR WIMS / retour = %s" % retour)
            # Si json arrive a parser la reponse, c'est une erreur. WIMS doit être indisponible (ou mal configuré).
            # autre erreur possible : l'exercice demandé a disparu de WIMS ?

            self.aq_parent.wims("verifierRetourWims", {"rep": fichier,
                                                       "fonction": "jalonexercicewims.py/getExoOEF",
                                                       "message": "Impossible d'obtenir un exo WIMS (demandeur = %s)" % authMember,
                                                       "jalon_request": requete
                                                       })
            message = _(u"Impossible d'obtenir cet exercice. Le serveur WIMS semble temporairement inaccessible. Merci de retenter ultérieurement svp.")
            self.plone_utils.addPortalMessage(message, type='error')
            # [TODO] : ici on pourrait peut-etre renvoyer un dico avec un eventuel code d'erreur pour pouvoir prendr en charge plus de cas.
            return {"request_status": "ERROR", "code_source": None, "error_message": message}
        except:
            # Si "fichier" n'est pas un JSON correct, ce doit bien etre un OEF.
            return {"request_status": "OK", "code_source": fichier}

    def getExoWims(self, modele, authMember, requete={}):
        """Permet de parser le code source d'un exercice WIMS."""
        # LOG.info("[getExoWims] modele = %s" % modele)
        # Il faudra faire un traitement specifique aux exercices externes ici
        if modele == "externe":
            if "permalink" in requete :
                # Cas où on recharge la page de modification (permalien incorrect).
                # LOG.info("[getExoWims] PERMALINK = %s" % requete["permalink"])
                return requete
            else:
                if self.permalink != "":
                    displayed_permalink = "%s?%s&cmd=new" % (self.getUrlServeur(), self.permalink)
                else:
                    displayed_permalink = ""
                return {"status": "OK", "permalink": displayed_permalink}
        # Cas où on recharge la page de modification (un parametre doit etre manquant).
        # on recharge alors simplement le formulaire precedent.
        if "option" in requete and requete["option"] == "force_rewrite":
            requete["options_split"] = 0
            requete["options_eqweight"] = 0
            requete["options_checkbox"] = 0
            if "options" in requete:
                variable = requete["options"]
                if "split" in variable:
                    requete["options_split"] = 1
                if "eqweight" in variable:
                    requete["options_eqweight"] = 1
                if "checkbox" in variable:
                    requete["options_checkbox"] = 1
            return requete

        parsed_exercice = self.getExoOEF(modele, authMember, requete)
        fichier = parsed_exercice["code_source"]

        if fichier is None or modele == "exercicelibre":
            return parsed_exercice
        else:
            variables_parse = {"qcmsimple": {"enonce":           "text{explain",
                                             "bonnesrep":        "matrix{datatrue",
                                             "mauvaisesrep":     "matrix{datafalse",
                                             "tot":              "integer{tot",
                                             "givetrue":         "integer{givetrue",
                                             "minfalse":         "integer{minfalse",
                                             "feedback_general": "text{feedback_general",
                                             "feedback_bon":     "text{feedback_bon",
                                             "feedback_mauvais": "text{feedback_mauvais",
                                             "options":          "text{option",
                                             "accolade":         "text{accolade=item\(",
                                             "credits":          "credits{",
                                             "hint":             "hint{",
                                             "help":             "help{",
                                             },
                               "equation": {"precision":     "precision{",
                                            "equation":      "real{ans",
                                            "enonce":        "text{explain",
                                            "texte_reponse": "answer{",
                                            "accolade":      "text{accolade=item\(",
                                            },
                               "texteatrous": {"type_rep":  "text{type_rep",
                                               "donnees":   "text{data",
                                               "feedback_general": "text{feedback_general",
                                               "feedback_bon"    : "text{feedback_bon",
                                               "feedback_mauvais": "text{feedback_mauvais",
                                               "credits":          "credits{",
                                               "accolade":         "text{accolade=item\(",
                                               "list_order":       "text{list_order=item\(",
                                               },
                               "marqueruntexte": {"minmark": "integer{minmark",
                                                  "maxmark": "integer{maxmark",
                                                  "data":    "text{data",
                                                  "pre":     "text{pre",
                                                  "post":    "text{post",
                                                  "options": "text{option"
                                                  },
                               "marquerparpropriete": {"explain":      "text{explain",
                                                       "prop":         "text{prop",
                                                       "data":         "matrix{data",
                                                       "tot":          "integer{tot",
                                                       "mingood":      "integer{mingood",
                                                       "minbad":       "integer{minbad",
                                                       "options":      "text{option",
                                                       "presentation": "text{presentation"
                                                       },
                               "questiontextuelletolerante": {"len":          "integer{len",
                                                              "data":         "text{data",
                                                              "atype":        "text{atype",
                                                              "include_good": "text{include_good",
                                                              "words":        "text{words",
                                                              "pre":          "text{pre",
                                                              "post":         "text{post"
                                                              },
                               "taperlemotassocie": {"size":     "integer{size",
                                                     "words":    "atrix{data",
                                                     "type_rep": "text{atype",
                                                     "explain":  "text{explain"
                                                     },
                               "reordonner": {"tot":     "integer{tot",
                                              "size":    "text{size",
                                              "data":    "text{data",
                                              "explain": "text{explain"
                                              },
                               "correspondance": {"tot":              "integer{tot",
                                                  "sizev":            "integer{sizev",
                                                  "sizer":            "integer{sizer",
                                                  "sizel":            "integer{sizel",
                                                  "feedback_general": "text{feedback_general",
                                                  "data":             "matrix{data",
                                                  "explain":          "text{explain",
                                                  "accolade":         "text{accolade=item\(",
                                                  },
                               "classerparpropriete": {"tot":              "integer{tot",
                                                       "max1":             "integer{max1",
                                                       "size1":            "text{size1",
                                                       "prop":             "text{prop",
                                                       "data":             "matrix{data",
                                                       "shuffle":          "text{option",
                                                       "explain":          "text{pre",
                                                       "post":             "text{post",
                                                       "estun":            "text{estun",
                                                       "noclass":          "text{noclass",
                                                       "feedback_general": "text{feedback_general"
                                                       },
                               "vraifauxmultiples": {"tot":              "integer{tot",
                                                     "mintrue":          "integer{mintrue",
                                                     "minfalse":         "integer{minfalse",
                                                     "datatrue":         "matrix{datatrue",
                                                     "datafalse":        "matrix{datafalse",
                                                     "options":          "text{option",
                                                     "explain":          "text{explain",
                                                     "accolade":         "text{accolade=item\(",
                                                     "feedback_general": "text{feedback_general",
                                                     "credits":          "credits{",
                                                     "hint":             "hint{",
                                                     "help":             "help{",
                                                     },
                               "texteatrousmultiples": {"data":             "text{data",
                                                        "pre":              "text{pre",
                                                        "post":             "text{post",
                                                        "feedback_general": "text{feedback_general",
                                                        "type_rep":         "text{type_rep",
                                                        "credits":          "credits{",
                                                        "hint":             "hint{",
                                                        "help":             "help{",
                                                        },
                                "qcmsuite": {"instruction"            : "text{instruction",
                                             "alea"                   : "text{alea",
                                             "accolade"               : "text{accolade=item\(",
                                             "nb_questions_max"       : "text{N",
                                             "nb_etapes"              : "text{MAX",
                                             "pourcentage_validation" : "text{percent",
                                             "credits"                : "credits{",
                                             "columns"                : "text{columns",
                                             "anstype"                : "text{anstype",
                                             "answer_given"           : "text{answer_given=item\(",
                                             }
                               }

            if modele == "equation":
                lettres = ["a", "b", "c", "d", "e"]
                for lettre in lettres:
                    variables_parse["equation"]["param_%s" % lettre] = "real{%s" % lettre

            fichier = fichier.replace("\n", "_ENDLINE_")

            for key in variables_parse[modele].keys():
                # Certaines instructions de wims fonctionnent differement (comme "precision")
                if key not in ["precision", "texte_reponse", "accolade", "credits", "hint", "help", "answer_given", "list_order"]:
                    pattern = "%s=(.*?)}_ENDLINE_" % variables_parse[modele][key]
                else:
                    if key in ["precision", "credits", "hint", "help"]:
                        # exemple : \precision{100}
                        pattern = "%s(.*?)}_ENDLINE_" % variables_parse[modele][key]
                    if key == "texte_reponse":
                        # exemple : \answer{Votre reponse est}{\ans}{type=number}
                        pattern = "%s([^\}]*)\}" % variables_parse[modele][key]
                    if key in ["accolade", "answer_given", "list_order"]:
                        # exemple : \text{accolade=item($$variable$$,1 oui,\n2 non)}
                        pattern = "%s([^,]*)" % variables_parse[modele][key]

                m = re.compile(pattern)
                recherche = m.search(fichier)
                # LOG.info("[getExoWims] variable : %s // valeur : %s" % (key, recherche.group(1)))
                if recherche is not None:
                    variable = recherche.group(1)
                    # Au cas ou la chaine "}_ENDLINE_" avait été introduite dans la variable, le nombre d'accolades sera impair.
                    # On continue alors la recherche jusqu'à la prochaine occurence.
                    if key not in ["texte_reponse", "accolade", "answer_given", "list_order"]:
                        variable = self.extendResearch(variable, fichier, recherche.end())

                else:
                    variable = self.getVariablesDefaut(modele)[key]
                if key == "options":
                    if "split" in variable:
                        parsed_exercice["%s_split" % key] = 1
                    else:
                        parsed_exercice["%s_split" % key] = 0
                    if "checkbox" in variable:
                        parsed_exercice["%s_checkbox" % key] = 1
                    else:
                        parsed_exercice["%s_checkbox" % key] = 0
                    if "eqweight" in variable:
                        parsed_exercice["%s_eqweight" % key] = 1
                    else:
                        parsed_exercice["%s_eqweight" % key] = 0
                else:
                    variable = variable.replace("_ENDLINE_", "\n")
                    # when variable = asis(variable)
                    if variable.startswith("asis("):
                        parsed_exercice[key] = variable[5:-1]
                    else:
                        parsed_exercice[key] = variable
                    # On détecte un eventuel souci dans le modèle (cas ou variable = $$key$$)
                    if parsed_exercice[key] == ("&#36;&#36;%s&#36;&#36;" % key):
                        parsed_exercice[key] = self.getVariablesDefaut(modele)[key]
                        # parsed_exercice[key] = variable.decode("iso-8859-1").encode("utf-8")

            if modele == "qcmsuite":
                i = 0
                pattern = 'textarea="(.*?)"_ENDLINE_'
                m = re.compile(pattern)
                recherche = m.search(fichier)
                variable = recherche.group(1)
                variable = variable.replace("_ENDLINE_", "")
                list_id_questions = variable.split(" ")
                parsed_exercice["list_id_questions"] = list_id_questions
                for id_question in list_id_questions:
                    pattern = "text{%s=(.*?)}_ENDLINE_" % id_question
                    m = re.compile(pattern)
                    recherche = m.search(fichier)
                    variable = recherche.group(1)
                    variable = self.extendResearch(variable, fichier, recherche.end())
                    variable = variable.replace("_ENDLINE_", "\n")

                    # when variable = asis(variable)
                    if variable.startswith("asis("):
                        variable = variable[5:-1]

                    # Si variable commence par "Qtitle", le premier saut de ligne est remplacé par un  "<br/>"
                    if variable.startswith("Qtitle"):
                        variable = variable.replace("\n", "<br/>", 1)
                    list_variable = variable.split("\n")
                    parsed_exercice["enonce%s" % str(i)] = list_variable[0].replace("<br/>", "\n")
                    parsed_exercice["feedback%s" % str(i)] = list_variable[1]
                    parsed_exercice["reponses%s" % str(i)] = "\n".join(list_variable[2:])
                    i = i + 1
            return parsed_exercice

    def extendResearch(self, variable, fichier, end_offset):
        u"""Permet d'etendre une recherche d'expression reguliere dans le cas ou le caractere d'arret aurait été imbriqué dans la variable."""
        # LOG.info("----- extendResearch -----")
        CountLeft = len(re.findall("\{", variable))
        CountRight = len(re.findall("\}", variable))
        if CountLeft > CountRight:
            # Au cas ou la chaine "}_ENDLINE_" avait été introduite dans la variable, le nombre d'accolades sera impair.
            # On continue alors la recherche jusqu'à la prochaine occurence.
            string = fichier[end_offset:]
            m2 = re.search("}_ENDLINE_", string)
            variable = "%s}_ENDLINE_%s" % (variable, string[:m2.start()])
            # Et on recommence en récursif tant que le nombre d'accolades n'est pas pair.
            new_offset = end_offset + len(string[:m2.start()]) + len("}_ENDLINE_")
            return self.extendResearch(variable, fichier, new_offset)
        else:
            return variable

    def getParamListeExos(self, exo_params, mode="autoeval"):
        u"""permet d'obtenir des parametres par défaut pour visualiser un exo en dehors d'une feuille."""
        # LOG.info("----- getParamListeExos -----")
        if exo_params:
            exo = exo_params.replace("*-*", "&")
            return exo
        else:
            if self.getModele() == "groupe":
                exo = "&exo=".join(self.getListeIdsExos())
            else:
                exo = self.getId()

            if mode == "examen":
                intro_check = "1,2,4"
            else:
                intro_check = "1,2,3,4"
            # Apparament, classes/fr n'a plus d'influence sur la langue. c'est le paremetre "lang" qui prime.

            # Valeur du parametre "intro_check" :
            # 1 = Toujours proposer une bonne réponse.
            # 2 = Pénalité pour une mauvaise réponse.
            # 3 = Afficher la bonne réponse. (A EVITER EN EXAMEN)
            # 4 = Permettre les indications (si disponibles).

            # parametre random = [0]: Proposer les exercices de la série dans l'ordre.
            # parametre scoredelay = x : nbre de secondes du chronometre
            # parametre intro_presentsol = [0:jamais, 1:si note non maxi, 2:toujours ] : Donner une solution (si disponible)?

            # qnum représente le nombre d'exercices à effectuer pour avoir une note.
            # qcmlevel représente la sévérité de notation.
            return "exo=%s&qnum=%s&qcmlevel=1&intro_qcmpresent=4&intro_presentsol=1&intro_check=%s&intro_expert=yes&scoredelay=0&module=classes/fr" % (exo, self.getQnum(), intro_check)

    def convertLangToWIMS(self, portal_lang):
        """Permet d'obtenir le code de langue WIMS a partir du code de langue de Plone."""
        # LOG.info("----- convertLangToWIMS -----")
        return jalon_utils.convertLangToWIMS(portal_lang)

    def test(self, condition, valeurVrai, valeurFaux):
        """permet de tester une condition, puis de renvoyer une valeur en fonction."""
        # LOG.info("----- test condition (%s) -----" % condition)
        return jalon_utils.test(condition, valeurVrai, valeurFaux)

    def getUrlServeur(self):
        """fournit l'URL du serveur WIMS."""
        # LOG.info("----- getUrlServeur -----")
        return self.aq_parent.wims("getAttribut", "url_connexion")

    def formaterTitreWIMS(self, titre):
        u"""Renvoit une chaine dépourvye d'un ensemble de caracteres susceptibles de corrompre un exercice."""
        # LOG.info("----- formaterTitreWIMS -----")
        listeReplace_titre_wims = ["<", ">", "{", "}", "(", ")", "[", "]", "$", "&", "?", "!", ",", "\"", "\'", ";", "\\", "/"]
        for lettre in listeReplace_titre_wims:
            titre = titre.replace(lettre, " ")
        # Replace multiple spaces by one (and remove starting&ending spaces)
        return re.sub(' +', ' ', titre.strip())

    def setProperties(self, dico):
        u"""Définit les propriétés d'un jalonexercicewims."""
        # LOG.info("----- setProperties -----")
        for key in dico.keys():
            if key == "Title":
                dico[key] = self.formaterTitreWIMS(dico[key])
            self.__getattribute__("set%s" % key)(dico[key])
        self.reindexObject()

        # Changement du titre de l'exo en cascade dans les autoeval/examens quand on le modifie dans "Mon Espace"
        items = self.getRelatedItems()
        for item in items:
            if item.Type() == "AutoEvaluation-Examen":
                # dico = item.getInfosElement()
                dico = item.getDocumentsProperties()
                if dico:
                    if self.getId() in dico:
                        dico[self.getId()]["titreElement"] = self.Title()
                    item.setDocumentsProperties(dico)
                    item.reindexObject()

    def parser_permalien(self, permalien):
        u"""vérifie qu'un permalien est correct, et renvoit sa version corrigée.

        Cette fonction ne renvoit que les variables de l'URL. Inutile de sauvegarder le DNS et "http://"...

        """
        # LOG.info("----- parser_permalien -----")
        new_permalink = ""
        message = ""
        # On applique un ensemble de filtre pour éviter que des utilisateurs collent des liens mal formés, du style
        # http://ticewims.unice.fr/wims/wims.cgi?module=local/qcmC2i.fr" title="
        # ==> sera remplacé par
        # http://ticewims.unice.fr/wims/wims.cgi?module=local/qcmC2i.fr&cmd=new
        # strip retire les espace avant/apres, split[0] coupe au premier espace, et split('"') ne prend que ce qui se trouve avant un guillemet
        new_permalink = permalien.strip().split()[0].split('"')[0]

        test_string = "http://"
        if new_permalink.count(test_string) > 1:
            # We take only the last URL.
            new_permalink = "%s%s" % (test_string, new_permalink.split(test_string)[-1])
            message = _(u"Un exercice ne peux avoir qu'un seul permalien.<br/>")

        if new_permalink != permalien:
            message = message + _(u"Votre permalien était incorrect, et il a été corrigé automatiquement. Merci de vérifier son bon fonctionnement.")

        url = urlparse(new_permalink)
        params = {}
        for part in url[4].split('&'):
            variable = part.split('=')
            # S'il n'y a aucun "=" dans la chaine, variable ne contiendra qu'un element.
            if (len(variable) > 1):
                if variable[0] not in params.keys():
                    params[variable[0]] = variable[1]
                else:
                    params[variable[0]] = params[variable[0]] + "," + variable[1]
        if "module" in params.keys():
            new_permalink = "module=%s" % params['module']
            for key in sorted(params.iterkeys()):
                if key not in ['cmd', 'session', 'module']:
                    new_permalink = "%s&%s=%s" % (new_permalink, key, params[key])
            if message != "":
                self.plone_utils.addPortalMessage(message, type='warning')
            return new_permalink
        else:
            message = _(u"Permalien incorrect. Assurez-vous de coller un permalien correct svp.")
            self.plone_utils.addPortalMessage(message, type='warning')
            # Dans ce cas, l'exercice ne sera pas modifié.
            return ""

    def addRelatedItem(self, item_a_ajouter):
        u"""Ajoute un objet aux relatedItems du JalonExerciceWims actuel, puis réindexe l'exo."""
        # LOG.info("----- addRelatedItem -----")
        relatedItems = self.getRelatedItems()
        if item_a_ajouter not in relatedItems:
            relatedItems.append(item_a_ajouter)
            self.setRelatedItems(relatedItems)
            self.reindexObject()

    def removeRelatedItem(self, item_a_retirer):
        u"""Retire un objet des relatedItems du JalonExerciceWims actuel, puis réindexe l'exo."""
        # LOG.info("----- removeRelatedItem -----")
        relatedItems = self.getRelatedItems()
        if item_a_retirer in relatedItems:
            relatedItems.remove(item_a_retirer)
            self.setRelatedItems(relatedItems)
            self.reindexObject()

    def updateRelatedItems(self):
        """Update the exercice related items (checks if each related item still exists, and if they are really still connected."""
        # LOG.info("----- updateRelatedItems -----")
        relatedItems = self.getRelatedItems()
        self_id = self.getId()
        deleted = []
        for item in relatedItems:
            # LOG.info("item_type = %s" % item.portal_type)
            if item.portal_type == "JalonCoursWims":
                # Cas de l'activité WIMS
                if self_id not in item.getListeExercices():
                    # LOG.info("L'exercice n'est plus dans l'activité reliée ! On le retire.")
                    deleted.append(item)
                    if self in item.getRelatedItems():
                        item.removeRelatedExercice(self)
                    else:
                        relatedItems.remove(item)
            elif item.portal_type == "JalonExerciceWims":
                # Cas du groupement d'exercice
                if self_id not in item.getListeIdsExos():
                    # LOG.info("L'exercice n'est plus dans le groupe relié ! On le retire.")
                    deleted.append(item)
                    if self in item.getRelatedItems():
                        item.removeRelatedItem(self)
                    relatedItems.remove(item)
        self.setRelatedItems(relatedItems)
        self.reindexObject()
        # Renvoit la liste des corrections effectuées
        return deleted

    def checkRoles(self, user, context, action="view"):
        u"""Permet de vérifier si l'utilisateur courant a le droit d'accéder à un exercice.

        # Si le droit n'est pas accordé, un message est affiché à l'utilisateur.
        # Si on suspecte une tentative de fraude, l'administrateur recoit un message.
        # action indique si l'utilisateur tente d'y accéder en lecture ("view") ou écriture ("edit")

        """
        # Pour le moment, action n'est pas utile. Le même role permet d'acceder en lecture / ecriture.
        # LOG.info("----- checkRoles -----")
        user_roles = user.getRolesInContext(context)
        if 'Owner' in user_roles or 'Manager' in user_roles:
            return True
        else:
            if 'Anonymous' in user_roles:
                # Normalement, le mecanisme de gestion des droits de Plone ne pemretrra de toute facon pas un anonyme d'accéder à un exercice.
                # Mais ceci peux tout de même se produire dans le cas ou un exercice a été rendu public via son insertion dans un cours public justement.
                message = _(u"Vous êtes déconnecté. Merci de vous connecter pour accéder à cette page.")
                mess_type = "info"
            else:
                message = _(u"Vous tentez d'accéder à une page qui ne vous appartient pas. Une suspicion de fraude vous concernant a été envoyée à l'administrateur du site.")
                mess_type = "alert"
                self.aq_parent.wims("verifierRetourWims", {"rep": '{"status":"ERROR", "message":"checkRoles Failed"}',
                                                           "fonction": "jalonexercicewims.py/checkRoles",
                                                           "message": "Suspicion de fraude de l'utilisateur %s" % user.getId(),
                                                           "jalon_request": context.REQUEST
                                                           })

        context.plone_utils.addPortalMessage(message, type=mess_type)
        return False


registerATCT(JalonExerciceWims, PROJECTNAME)
