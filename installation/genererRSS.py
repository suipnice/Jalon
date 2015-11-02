# -*- coding: utf-8 -*-

import os
import json
import urllib

chemin = "/home/jalon/iTunesU"
source_json = "source.json"
base_url ="http://jalon.unice.fr/cours"
page_rss = "cours_rss_view"
dico = json.load(open("%s/%s" % (chemin, source_json)))

liste_repertoire = os.listdir(chemin)
for id_utilisateur in dico.keys():
    if id_utilisateur not in liste_repertoire:
        os.mkdir("%s/%s" % (chemin, id_utilisateur), 0755)
    for id_cours in dico[id_utilisateur]:
        urllib.urlretrieve("%s/%s/%s/%s" % (base_url, id_utilisateur, id_cours, page_rss), "%s/%s/%s.xml" % (chemin, id_utilisateur, id_cours))
