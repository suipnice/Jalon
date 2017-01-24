# [DOC] - Traduction de Jalon (développeur)

## Installer i18ndude :
La méthode recommandée est d'installer `i18ndude` via buildout.

Ajoutez les lignes suivantes au `buildout.cfg`:

	parts =
	    ...
	    i18ndude

	[i18ndude]
	unzip = true
	recipe = zc.recipe.egg
	eggs = i18ndude

Une fois fait, `i18ndude` sera disponible depuis le dossier `buildout/bin`.

	bin/i18ndude -h
	Usage: i18ndude command [options] [path | file1 file2 ...]]

> **ATTENTION !** Ne pas utiliser `easy_install i18ndude`.
>
> i18ndude importe plusieurs packages Zope, et l'insatller au niveau du système vous provoquera indéniablement des conflits.

[Plus d'infos...](http://docs.plone.org/develop/plone/i18n/internationalisation.html#installing-i18ndude)


## Ajouter une langue
*(exemple avec le code "de" pour l'allemand)*

	cd CHEMIN_PLONE/zinstance/src/jalon.content/jalon/content/locales/
	mkdir -p de/LC_MESSAGES
	cp fr/LC_MESSAGES/jalon.content.po de/LC_MESSAGES/

## A chaque modification de texte dans les templates :

mettre à jour les fichiers de traduction :

	cd CHEMIN_PLONE/zinstance/src/jalon.content/jalon/content/locales/
	./update_pot.sh

...et en cas d'erreur(s), consulter le fichier "rebuild_i18n.log" pour plus de détals...

## Conventions de nommage des id de traduction

Attention : un ID de traduction doit etre écrit en ASCII (pas UTF-8)

* => aucun accent dans un `msgid`
* => vous ne pouvez mettre un `i18n:translate=""` dans une .PT que si le texte affiché ne contient aucun accent.

Quelques conventions de nommage des msgid :

* **heading_**: for `<h>` elements
* **description_**: Explanatory text directly below
* **legend_**: Used in `<legend>` elements
* **label_**: For field labels, input labels, i.e. `<label>`, and for `<a>` elements
* **help_**: Any text that provides help for form input.
* **box_**: Content inside portlets.
* **listingheader_**: For headers in tables (normally of class `listing`).
* **date_**: For date/time-related stuff. E.g. `Yesterday`, `Last week`.
* **text_**: Messages that do not fit any other category, normally inside `<p>`
* **batch_**: for batch-related things - such as `Displaying X to Y of Z total documents`

[Plus d'infos...](http://docs.plone.org/develop/plone/i18n/internationalisation.html)