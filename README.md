# Sources du Hub pédagogique Jalon

Pour une installation en production, rendez vous sur [jalon.unice.fr/telecharger](http://jalon.unice.fr/telecharger)

## Guide du développeur (à compléter) :

### Hierarchie globale des fichiers
* Les scripts des vues se trouvent dans jalon.content/skins
* Les templates se trouvent dans jalon.theme/skins

### Convention de nommage
* Les noms des fonctions python sont en anglais
* Les macro ont le suffixe "_macro"
* Les scripts ont le suffixe "_script"

### Charte ergonomique
La structure de base d'une page principale est la suivante :

	<main class="row">
	      <div class="small-12 columns">
	      </div>
	</main>

La structure de base d'une page de type "reveal" est la suivante :

	<metal:main fill-slot="content">
	    <h2>
	        <i class="fa fa-$ICON_ID"></i>
	        <tal:block i18n:translate="">$TITRE</tal:block>
	        <a class="close-reveal-modal"></a>
	    </h2>

	    <form tal:attributes="action string:${context/absolute_url}/$MONSCRIPT_script" method="post">
	        <div class="formControls">
	            <button type="submit" class="button small">
	                <i class="fa fa-$ICON_ID"></i>
	                <tal:block i18n:translate="">Envoyer</tal:block>
	            </button>
	        </div>
	    </form>
	</metal:main>
