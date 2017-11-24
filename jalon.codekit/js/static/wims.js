/*

        javascripts for the Jalon-WIMS plugin



/***************************************************************************************************

        Exportation d'exercices : accordeon dans formulaire

*/

function setWimsExportAccordionRadio( accordionID ) {

    var $accordion = Foundation.utils.S( '#' + accordionID );
    var $form = $accordion.parent( 'form' );
    var $submitButton = $form.children( '.formControls' ).children( '[type=submit]' );

    $accordion.on( 'toggled', function ( event, accordion ) {

        var targetID = $( this ).find( '.content.active' ).attr( 'id' );

        if ( targetID !== undefined ) {
            switchButtonEnabledState( $submitButton, true );
            Foundation.utils.S( '#js-export_format' ).prop( 'value', targetID );
            Foundation.utils.S( '#' + targetID + '_default' ).prop( 'checked', true );
        } else {
            switchButtonEnabledState( $submitButton, false );
        }
    });
}

/* Permet a la fois de fermer une fenetre modale lors d'un téléchargement,
   et d'afficher le message indiqué dans l'attribiut "data-success_msg" du formulaire. */
function closeDownloadModal( formID ) {

    var $form= Foundation.utils.S( '#' + formID );

    $form.submit( function( event ) {

        Foundation.utils.S( '#reveal-main' ).foundation( 'reveal', 'close' );
        setAlertBox( 'info', $form.data( 'success_msg' ) );
    } );
}



/***************************************************************************************************

    Filtre une selection d'exercices en 2 groupes :
        * les compatibles avec l'action suivante qui seront vraiment sélectionnés
        * les autres, qui seront indiqués comme incompatibles à l'utilisateur.
        l'attribut "filter" permet de savoir si l'exercice est compatible.
    Utilisé pour la création de groupe d'exos (un groupe n'inclue pas un autre groupe ni un exo externe)
    et pour l'export d'exos multiples (seuls certains modèles sont exportables)
*/

function setWimsSelectionFilter( selectionForm_id, reveal_id, filter ) {

    $( document ).on( 'open.fndtn.reveal', reveal_id, function ( ) {

        /*
        var qNum = Foundation.utils.S( '#js-update_target tbody input[type="checkbox"][name="paths:list"]:checked' ).length;
        var $qNum = Foundation.utils.S( '#qnum' );
        if ( qNum > 9 ) { qNum = 9; }
        $( 'option', $qNum ).remove( );
        for ( i = 1 ; i <= qNum; i++ ) { $qNum.append( $( '<option>', { value : i, text : i } ) ); }
        */

        Foundation.utils.S( '#includedPanelMessage' ).remove( );
        Foundation.utils.S( '#excludedPanelMessage' ).remove( );

        var $selectionForm = Foundation.utils.S( "#"+selectionForm_id );
        var $input;

        var includedMessage = "";
        var excludedMessage = "";
        var nIncluded = 0;
        var nExcluded = 0;

        // Creation des elements selectionnes
        Foundation.utils.S( '#js-update_target tbody input[name="paths:list"]:checked' ).each( function( index ) {

            if ( !$( this ).data( filter ) ) {

                $input = $( "<input>", {
                    'type': "hidden",
                    'value': $( this ).val( ),
                } ).attr( 'name', "paths:list" );

                $selectionForm.append( $input );

                includedMessage += '<li>' + $( this ).data( 'res_name' ) + '</li>';
                nIncluded++;

            } else {

                excludedMessage += '<li>' + $( this ).data( 'res_name' ) + '</li>';
                nExcluded++;

            }

        } );

        // Messages d'information
        if ( nIncluded ) {

            $selectionForm.find( '.field' ).show( );
            //$selectionForm.find( '[type="submit"]' ).removeAttr( 'disabled' ).show( );
            $selectionForm.find( '[type="submit"]' ).prop( 'disabled', false ).show( );

            if ( nExcluded ) {
                if ( nExcluded > 1 ) {
                    excludedMessage = $selectionForm.data( 'p_no_msg' ) + '<ul>' + excludedMessage + '</ul>';
                } else {
                    excludedMessage = $selectionForm.data( 's_no_msg' ) + '<ul>' + excludedMessage + '</ul>';
                }
                $selectionForm.prepend(
                    $( "<div>", {
                        'id': "excludedPanelMessage",
                        'class': "panel warning radius",
                        'html': excludedMessage
                    } )
                );
            }

            if ( nIncluded > 1 ) {
                includedMessage = $selectionForm.data( 'p_yes_msg' ) + '<ul>' + includedMessage + '</ul>';
            } else {
                includedMessage = $selectionForm.data( 's_yes_msg' ) + '<ul>' + includedMessage + '</ul>';
            }

            $selectionForm.prepend(
                $( "<div>", {
                    'id': "includedPanelMessage",
                    'class': "panel callout radius",
                    'html': includedMessage
                } )
            );

        } else {

            $selectionForm.find( '.field' ).hide( );
            $selectionForm.find( '[type="submit"]' ).prop( 'disabled', true ).hide( );

            excludedMessage = $selectionForm.data( 'all_no_msg' );

            if ( nExcluded > 1 ) {
                excludedMessage += " " + $selectionForm.data( 'p_all_no_msg' );
            } else {
                excludedMessage += " " + $selectionForm.data( 's_all_no_msg' );
            }

            $selectionForm.prepend(
                $( "<div>", {
                    'id': "includedPanelMessage",
                    'class': "panel warning radius",
                    'html': excludedMessage
                } )
            );
        }
        // prepare la fermeture du popup au telechargement.
        closeDownloadModal(selectionForm_id);

    } );

}


/***************************************************************************************************

        Initialisation du type d'exercice "QCM Suite"

*/

function setQCMSuite( ) {
    var suppQuestButton = Foundation.utils.S("#supprimerQuestion");
    var addQuestButton = Foundation.utils.S("#ajouterQuestion");
    var maxQuestHelper = Foundation.utils.S("#js-max_questions_helper");

    // Nombre maximum autorisé de questions dans un exo
    var max_questions = 40;

    // Texte du nombre de questions
    input_nb_questions = Foundation.utils.S('#nb_questions');

    refreshQCMSuite();
    /*
        Ajout d'une question au modele WIMS "QCM Suite"
        (question = ensemble d'input et de textareas)
    */
    addQuestButton.on('click', function() {
        var questionList = Foundation.utils.S('.question');

        var n = questionList.length;
        // Clonage de la premiere question
        var firstQuestion = Foundation.utils.S(questionList[0]);
        var clonedQuestion = firstQuestion.clone();

        // Initialisation de la question clonee
        clonedQuestion.find('input, textarea').each(function() {
            // On vide la valeur
            Foundation.utils.S(this).val('');
            var name = Foundation.utils.S(this).parent().attr('data-name')+n;
            // On change le nom en ajoutant le numero
            Foundation.utils.S(this).attr('name', name);
            Foundation.utils.S(this).attr('id',  name);
        });
        clonedQuestion.find('label').each(function() {
            // On change l'attribut "for" en ajoutant le numero
            Foundation.utils.S(this).attr('for', Foundation.utils.S(this).parent().attr('data-name')+n);
        });
        clonedQuestion.find('legend').each(function() {
            // On change l'attribut "for" en ajoutant le numero
            Foundation.utils.S(this).html(Foundation.utils.S(this).attr('data-titre')+(n+1));
        });

        // On l'ajoute au dom apres les autres (nombre questions = n+1)
        clonedQuestion.insertAfter(Foundation.utils.S(questionList[n-1])).hide().fadeIn('slow');
        Foundation.utils.S("html, body").animate({ scrollTop: clonedQuestion.offset().top }, 1000);
        refreshQCMSuite( );
    });


    /*
        Supprime la dernière question
    */
    suppQuestButton.on('click', function() {
        var questionList = $.makeArray(Foundation.utils.S('.question'));
        var last_quest = Foundation.utils.S(questionList.pop());
        var new_last_quest = Foundation.utils.S(questionList.pop());
        Foundation.utils.S("html, body").animate({ scrollTop: new_last_quest.offset().top }, 900);
        last_quest.fadeOut('slow', function() {
            Foundation.utils.S(this).remove();
            refreshQCMSuite( );
       });
    });

    function refreshQCMSuite( ) {
        var n = Foundation.utils.S('.question').length;

        // Maj du nombre de questions
        input_nb_questions.val(n);

        if (n >= (max_questions/2)){
            maxQuestHelper.fadeIn();
        }
        // S'il y a plus de max_questions, on masque le bouton 'ajouter'
        if (n>=max_questions){
            addQuestButton.fadeOut();
        } else {
            // S'il y a moins de max_questions questions, on s'assure que le bouton 'ajouter' est présent.
            addQuestButton.fadeIn();
        }

        // S'il y a moins de 2 questions on cache le bouton supprimer.
        if ( n < 2 ) {
            suppQuestButton.fadeOut();
        } else {
            suppQuestButton.fadeIn();
        }
    }

}




/***************************************************************************************************

        Mise en page CORS -> exercicewims_view_CORS.pt


function setWimsContent( ) {

    var $insertWims = Foundation.utils.S( '#insert_wims' );

    $.ajax( {
            url: $insertWims.data( 'src' ),
            async: false,
            crossDomain: true,
            cache: false,
            dataType: 'html',
            beforeSend : function ( ) {

            },
        } )
        .done( function( data ) {

            var $content = $( data ).find( '#wimspagebox' ).contents( );

            $insertWims.remove( );
            $content.find( 'p.send_answer > [type="submit"], #oef_actions span a' ).addClass( 'button small radius' );
            $( '#wims' ).append( $content );
    } );

}
*/


/***************************************************************************************************

        Edition d'un exercice


function setWimsExerciceEditor( ) {

    var $wimsEditorContainer = Foundation.utils.S( '#wims-edit' );

    // if ( $wimsEditorContainer.data( 'modele' ) !== "externe" ) { }

    // Foundation-isation : affichage de l'aide
    $wimsEditorContainer.find( 'div.field > .savoirplus_lien' ).each( function( index ) {

        var revealId = "wims-edit_reveal-" + index;

        $( this )
            .removeClass( )
            .addClass( 'button tiny radius' )
            .attr( 'data-reveal-id', revealId )
            .removeAttr( 'href' )
            .prepend( '<i class="fa fa-question"></i>' );

        $( this ).parent( 'div.field' ).find( '.savoirplus_contenu' )
            .removeClass( )
            .attr( 'id', revealId )
            .addClass( 'reveal-modal large wims-edit_reveal' )
            .attr( 'data-reveal', "data-reveal" )
            .attr( 'data-options', "close_on_background_click: true;" )
            .prepend( '<h2>' + $( this ).parent( 'div.field' ).find( 'label' ).text( ) + '<a class="close-reveal-modal"></a></h2>' );

    } );


    // Foundation-isation : param. avancés etc.
    var $accElement, $accElLink, $accElDiv;

    $wimsEditorContainer.find( 'div.savoirplus' ).each( function( index ) {

        $accElement = $( "<dd>", {
            'class': "accordion-navigation",
        } );

        var $advancedParamElement = $( this ).find( '#param_avances' );

        if ( $advancedParamElement.length > 0 ) {

            $advancedParamElement.find( 'legend' ).remove( );
            $accElLink = $( "<a>", {
                'href': "#wims_adv_opt",
                'text': "Options avancées",
            } );
            $accElDiv = $( "<div>", {
                'id': "wims_adv_opt",
                'class': "content",
            } ).html( $advancedParamElement.html( ) );

        } else {

            $accElLink = $( "<a>", {
                'href': "#wims_adv_use",
                'text': "Usages avancés",
            } );
            $accElDiv = $( "<div>", {
                'id': "wims_adv_use",
                'class': "content",
            } ).html( $( this ).find( '.savoirplus_contenu' ).html( ) );

        }

        $( this ).remove( );
        $accElement.append( $accElLink ).append( $accElDiv );
        $wimsEditorContainer.find( 'dl.accordion' ).prepend( $accElement );

    } );


    // Foundation-isation : saisies obligatoires
    $wimsEditorContainer.find( 'div.field > .fieldRequired' ).each( function( index ) {

        $( this ).parent( ).find( 'input, textarea' ).attr( 'required', "required" ).attr( 'placeholder', "Saisie obligatoire" );

    } );


    // Foundation-isation : initialisation et affichage
    $wimsEditorContainer.foundation( {
        reveal : {
            animation: 'fade',
            animation_speed: 300,
            close_on_background_click: true,
        },
        accordion: {
            active_class: 'active',
            multi_expand: false,
            toggleable: true,
        }
    } );

    $wimsEditorContainer.fadeIn( );

}
*/
