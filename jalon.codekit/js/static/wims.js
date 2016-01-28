/*

        Jalon v4.5 (static) : WIMS



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

    $form.submit( function( event ) {

        Foundation.utils.S( '#reveal-main' ).foundation( 'reveal', 'close' );
        setAlertBox( 'success', $form.data( 'success_msg' ) );
    } );


}



/***************************************************************************************************

        Creation d'un groupe d'exercices

*/

function setWimsGroupCreator( ) {

    $( document ).on( 'open.fndtn.reveal', '#group_create', function ( ) {
        /*
        var qNum = Foundation.utils.S( '#js-update_target tbody input[type="checkbox"][name="paths:list"]:checked' ).length;
        var $qNum = Foundation.utils.S( '#qnum' );
        if ( qNum > 9 ) { qNum = 9; }
        $( 'option', $qNum ).remove( );
        for ( i = 1 ; i <= qNum; i++ ) { $qNum.append( $( '<option>', { value : i, text : i } ) ); }
        */

        Foundation.utils.S( '#groupPanelMessage' ).remove( );
        Foundation.utils.S( '#noGroupPanelMessage' ).remove( );

        var $groupForm = Foundation.utils.S( '#js-wimsGroupCreator' );
        var $input;

        var groupMessage = "";
        var noGroupMessage = "";
        var nGroup = 0;
        var nNoGroup = 0;

        // Creation des elements selectionnes
        Foundation.utils.S( '#js-update_target tbody input[name="paths:list"]:checked' ).each( function( index ) {

            if ( !$( this ).data( 'no_group' ) ) {

                $input = $( "<input>", {
                    'type': "hidden",
                    'value': $( this ).val( ),
                } ).attr( 'name', "paths:list" );
                /*
                $input = $( "<input>", {
                    'type': "checkbox",
                    //'name': "paths:list",
                    'value': $( this ).val( ),
                    'checked': true,
                    'css': { 'display': 'none' },
                } ).attr( 'name', "paths:list" );
                */
                $groupForm.append( $input );

                groupMessage += '<li>' + $( this ).data( 'res_name' ) + '</li>';
                nGroup++;

            } else {

                noGroupMessage += '<li>' + $( this ).data( 'res_name' ) + '</li>';
                nNoGroup++;

            }

        } );

        // Messages d'information
        if ( nGroup ) {

            $groupForm.find( '.field' ).show( );
            //$groupForm.find( '[type="submit"]' ).removeAttr( 'disabled' ).show( );
            $groupForm.find( '[type="submit"]' ).prop( 'disabled', false ).show( );

            if ( nNoGroup ) {
                if ( nNoGroup > 1 ) {
                    noGroupMessage = $groupForm.data( 'p_no_msg' ) + '<ul>' + noGroupMessage + '</ul>';
                } else {
                    noGroupMessage = $groupForm.data( 's_no_msg' ) + '<ul>' + noGroupMessage + '</ul>';
                }
                $groupForm.prepend(
                    $( "<div>", {
                        'id': "noGroupPanelMessage",
                        'class': "panel warning radius",
                        'html': noGroupMessage
                    } )
                );
            }

            if ( nGroup > 1 ) {
                groupMessage = $groupForm.data( 'p_yes_msg' ) + '<ul>' + groupMessage + '</ul>';
            } else {
                groupMessage = $groupForm.data( 's_yes_msg' ) + '<ul>' + groupMessage + '</ul>';
            }

            $groupForm.prepend(
                $( "<div>", {
                    'id': "groupPanelMessage",
                    'class': "panel callout radius",
                    'html': groupMessage
                } )
            );

        } else {

            $groupForm.find( '.field' ).hide( );
            //$groupForm.find( '[type="submit"]' ).attr( 'disabled', "disabled" ).hide( );
            $groupForm.find( '[type="submit"]' ).prop( 'disabled', true ).hide( );

            noGroupMessage = $groupForm.data( 'all_no_msg' );

            if ( nNoGroup > 1 ) {
                noGroupMessage += " " + $groupForm.data( 'p_all_no_msg' );
            } else {
                noGroupMessage += " " + $groupForm.data( 's_all_no_msg' );
            }

            $groupForm.prepend(
                $( "<div>", {
                    'id': "groupPanelMessage",
                    'class': "panel warning radius",
                    'html': noGroupMessage
                } )
            );
        }

    } );

}



/***************************************************************************************************

        Initialisation du type d'exercice "QCM Suite"

*/

function setQCMSuite( ) {

    var suppQuestButton = Foundation.utils.S("#supprimerQuestion");

    /*
        Ajout d'une question au modele WIMS "QCM Suite"
        (question = ensemble d'input et de textareas)
    */
    Foundation.utils.S('#ajouterQuestion').on('click', function() {

        // Liste des questions
        var questionList = Foundation.utils.S('.question');

        // Nombre de questions existantes
        var n = questionList.length;

        // Clonage de la premiere question
        var firstQuestion = $(questionList[0]);
        var clonedQuestion = firstQuestion.clone();

        // Initialisation de la question clonee
        clonedQuestion.find('input, textarea').each(function() {
            // On vide la valeur
            $(this).val('');
            var name = $(this).parent().attr('data-name')+n;
            // On change le nom en ajoutant le numero
            $(this).attr('name', name);
            $(this).attr('id',  name);
        });
        clonedQuestion.find('label').each(function() {
            // On change l'attribut "for" en ajoutant le numero
            $(this).attr('for', $(this).parent().attr('data-name')+n);
        });
        clonedQuestion.find('legend').each(function() {
            // On change l'attribut "for" en ajoutant le numero
            $(this).html($(this).attr('data-titre')+(n+1));
        });

        // On l'ajoute au dom apres les autres (nombre questions = n+1)
        clonedQuestion.insertAfter($(questionList[n-1])).hide().fadeIn('slow');

        // On ajoute le lien de suppression s'il y a plus d'une question
        //if ( suppQuestButton.is(':hidden') && ( Foundation.utils.S('.question').length > 1 ) ) {
        if ( suppQuestButton.is(':hidden') && ( n > 0 ) ) {
            suppQuestButton.fadeIn();
        }

        // Maj du nombre de questions
        Foundation.utils.S('#nb_questions').val(n+1);

    });


    /*
        Supp. de la dernière question
    */
    suppQuestButton.on('click', function() {

        $('.question:last').fadeOut('slow', function() {
            $(this).remove();
            var n = Foundation.utils.S('.question').length;
            Foundation.utils.S('#nb_questions').val(n);
            // S'il y a moins de 2 questions on cache le bouton supprimer.
            if ( n < 2 ) {
                suppQuestButton.fadeOut();
            }
       });
    });

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
