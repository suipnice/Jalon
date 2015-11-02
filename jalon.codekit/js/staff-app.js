/***************************************************************************************************

    Jalon v4.5 : fonctionnalités specifiques aux roles "Personnel", "Manager" et "Secretaire"

*/


/*
    Inclusions CodeKit specifiques
*/

//@codekit-prepend "static/batch.js";   // Selection par lot
//@codekit-prepend "static/tag.js";     // Etiquetage
//@codekit-prepend "static/rsc.js";     // Mes ressources
//@codekit-prepend "static/crs.js";     // Mes cours
//@codekit-prepend "static/std.js";     // Mes etudiants
//@codekit-prepend "static/wims.js";    // WIMS



/***************************************************************************************************

    Gestion standard des formulaires en "reveal"

*/


/*
    Validation et rafraichissement du plan du cours :

        - ckEditorInstanceName est un ID de textarea utilisant CKEditor.

*/

function setRevealFormPlanRefresh( formID, revealID, ckEditorInstanceName ) {

    if ( typeof ckEditorInstanceName !== 'undefined' ) {
        ckEditorInstanceName = instantiateCKEditor( ckEditorInstanceName );
    } else {
        ckEditorInstanceName = false;
    }

    Foundation.utils.S( '#' + formID ).submit( function( event ) {

        if ( ckEditorInstanceName ) {
            CKEDITOR.instances[ ckEditorInstanceName ].updateElement( );
        }

        event.preventDefault( );

        var $form = $( this );
        var $reveal = Foundation.utils.S( '#' + revealID );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
            var html = $.parseHTML( data );
            if ( $( html ).find( '.error' ).length ) {
                $reveal.empty( ).html( data );
                revealInit( $reveal );
            } else {
                $.get( ABSOLUTE_URL + '/cours_affichage_plan' ).done( function( data ) {
                    $( '#course_plan-plan' ).html( data );
                    $reveal.foundation( 'reveal', 'close' );
                    //$( document ).foundation( 'dropdown', 'reflow' );
                    setAlertBox( 'success', $form.data( 'success_msg' ) );
                } );
            }
        } );
    } );
}



/*
    Validation et rafraichissement d'un element de la page en cours

        - ckEditorInstanceName est un ID de textarea utilisant CKEditor.

*/

function setRevealForm( formID, revealID, ckEditorInstanceName ) {

    if ( typeof ckEditorInstanceName !== 'undefined' ) {
        ckEditorInstanceName = instantiateCKEditor( ckEditorInstanceName );
    } else {
        ckEditorInstanceName = false;
    }

    Foundation.utils.S( '#' + formID ).submit( function( event ) {

        if ( ckEditorInstanceName ) {
            CKEDITOR.instances[ ckEditorInstanceName ].updateElement( );
        }

        event.preventDefault( );

        $form = $( this );
        var $reveal = Foundation.utils.S( '#' + revealID );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
            var html = $.parseHTML( data );
            if ( $( html ).find( '.error' ).length ) {
                $reveal.empty( ).html( data );
                revealInit( $reveal );
            } else {
                Foundation.utils.S( '#js-update_target' ).empty( ).html( data );
                $reveal.foundation( 'reveal', 'close' );
                setAlertBox( 'success', $form.data( 'success_msg_pre' ) + " « " + $form.find( '#title' ).val( ) + " » " + $form.data( 'success_msg_post' ) );
            }
        } );
    } );
}




/***************************************************************************************************

    Formulaires

*/


/*
    Inscription par courriel : constitution de la liste.
*/

function setMailRegistrationForm( ) {

    var $registrationForm = Foundation.utils.S( '#js-mailRegistration' );
    var $registrationFormControls = $registrationForm.children( 'div.formControls' );
    var $registrationFormButton = $registrationFormControls.children( 'button[type=submit]' );
    var $registrationList = [ ];

    var $listForm = Foundation.utils.S( '#js-mailRegistrationList' );

    var $listTableBody = $listForm.find( 'tbody' );
    var listTableRowHTML = '';

    var lastname = '';
    var firstname = '';
    var email = '';
    var invitation = '';
    var doubleCheck = false;


    switchButtonEnabledState( $registrationFormButton, false );


    $registrationForm.submit( function( event ) {

        $listTableBody.find( 'tr' ).each( function( index ) {
            //$registrationList.push( window.atob( $( this ).data( 'invitation' ) ) );
            $registrationList.push( $( this ).data( 'invitation' ) );
        } );

        $registrationForm.children( 'input[name=invitation]' ).val( $registrationList.join( ',' ) );

    } );


    $listForm.submit( function( event ) {

        event.preventDefault( );

        firstname = $listForm.find( 'input[name=firstname]' ).val( ).trim( );
        lastname = $listForm.find( 'input[name=lastname]' ).val( ).trim( );
        email = $listForm.find( 'input[name=email]' ).val( ).trim( );
        invitation = firstname + ' ' + lastname + ' <' + email + '>';
        doubleCheck = false;

        $listForm.find( 'input' ).val( '' );

        //listTableRowHTML = '<tr class="hide" data-invitation="' + window.btoa( invitation ) + '">';
        listTableRowHTML = '<tr class="hide" data-invitation="' + invitation + '">';
        listTableRowHTML += '<td class="name">' + lastname + '</td><td class="name">' + firstname + '</td><td class="email">' + email + '</td><td>';
        listTableRowHTML += '<a title="Retirer de la liste"><i class="fa fa-minus-circle fa-lg fa-fw no-pad warning"></i></a></td></tr>';

        if ( ! $listTableBody.find( 'tr' ).length ) {

            $listForm.find( 'div.panel:last-child' ).slideDown( 'slow', function( ) {
                switchButtonEnabledState( $registrationFormButton, true );
            } );

        } else {

            $listTableBody.find( 'tr' ).each( function( ) {
                if ( $( this ).data( 'invitation' ) === invitation || $( this ).children( 'td.email' ).html( ) === email ) {
                    doubleCheck = true;
                    return false;
                }
            } );
        }

        if ( ! doubleCheck ) {
            $( listTableRowHTML ).appendTo( $listTableBody ).show( 'slow' );
        }

    } );


    $listTableBody.on( 'click', 'a', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        $( this ).closest( 'tr' ).hide( 'slow', function( ) {

            $( this ).remove( );

            if ( ! $listTableBody.find( 'tr' ).length ) {
                $listForm.find( 'div.panel:last-child' ).slideUp( 'slow', function( ) {
                    switchButtonEnabledState( $registrationFormButton, false );
                } );
            }
        } );

    } );

}



/*
    Instanciation CKEditor
*/

function instantiateCKEditor( textareaID ) {

    if ( window.CKEDITOR && window.CKEDITOR.dom ) {

        CKEDITOR.replace( textareaID, {
            customConfig: '',
            language: 'fr',
            // Define the toolbar groups as it is a more accessible solution.
            toolbarGroups: [
                { 'name': "basicstyles", 'groups': [ "basicstyles" ] },
                //{ 'name': "links",       'groups': [ "links" ] },
                //{ 'name': "paragraph",   'groups': [ "list", "blocks" ] },
                { 'name': "paragraph",   'groups': [ "list" ] },
                { 'name': "insert",      'groups': [ "insert" ] },
                //{ 'name': "document",    'groups': [ "mode" ] },
            ],
            // Remove unwanted plug-ins.
            removePlugins: 'image,elementspath',
            // Remove the redundant buttons from toolbar groups defined above.
            removeButtons: 'Strike,Subscript,Superscript,Anchor',
        } );

        return textareaID;

    } else {

        return false;
    }

}



/*
    Bascule de l'etat active / desactive d'un bouton
*/

function switchButtonEnabledState( $button, state ) {

    if ( state ) {
        $button.prop( 'disabled', false );
    } else {
        $button.prop( 'disabled', true );
    }

}



/*
    Commande de l'etat active / desactive d'un bouton via checkbox
*/

function enableSubmitButtonIfCheckboxTicked( formID ) {

    var $formControls = Foundation.utils.S( '#' + formID ).children( '.formControls' );
    var $button = $formControls.children( '[type=submit]' );

    $formControls.children( '[type=checkbox]' ).on( 'click', function( event ) {

        if ( $( this ).prop( 'checked' ) ) {
            switchButtonEnabledState( $button, true );
        } else {
            switchButtonEnabledState( $button, false );
        }

    } );

}



/*
    Affichage d'un message lors de la validation d'un formulaire
*/

function displayMessageOnSubmit( formID ) {

    var $form = Foundation.utils.S( '#' + formID );
    var $formControls = $form.children( '.formControls' );
    var $messagePanel = $form.children( '.panel.hide' );

    $form.on( 'click', '[type=submit]', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        $formControls.fadeOut( "fast", function( ) {
            $messagePanel.fadeIn( "fast", function( ) {
                $form.submit( );
            } );
        } );

    } );

}



/*
    Formulaires : pas de clics multiples
*/

function preventMultipleFormSubmits( containerID ) {

    Foundation.utils.S( '#' + containerID ).find( 'form' ).submit( function( event ) {

        $( this ).find( '[type="submit"]' ).prop( 'disabled', true );

    } );
}




/***************************************************************************************************

    Etiquettes

*/


/*
    Gestion des boutons d'etiquettes
*/

function _setTagSelector( $form ) {

    $form.on( 'click', 'a.filter-button', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        updateTagButtonState( $( this ) );

    } );
}



/*
    Changement d'etat des boutons d'etiquettes / de favoris
*/

function updateTagButtonState( $button ) {

    if ( $button.hasClass( 'unselected' ) ) {
        $button.removeClass( 'unselected' ).addClass( 'selected' ).blur( );
        return true;
    } else if ( $button.hasClass( 'selected' ) ) {
        $button.removeClass( 'selected' ).addClass( 'unselected' ).blur( );
        return false;
    }
}




/***************************************************************************************************

    Divers

*/


/*
    Datepicker
*/

function setDateTimePicker( dateTimeID ) {
    /*
    var $picker = Foundation.utils.S( '#' + dateTimeID );
    $picker.val( $picker.val( ).substring( 0, 16 ) ); //*/

    if ( !Modernizr.inputtypes.datetime ) {

        var date = new Date();
        var year = date.getFullYear( );

        //$picker.datetimepicker( {
        Foundation.utils.S( '#' + dateTimeID ).datetimepicker( {
            //theme: 'dark',
            //closeOnDateSelect: true,
            inline: true,
            lang: 'fr',
            format: 'Y/m/d H:i',
            weeks: false,
            minDate: 0,
            step: 15,
            yearStart: year,
            yearEnd: year + 1,
            //scrollInput: false,
            //timepickerScrollbar: true,
            //scrollTime: true,
            scrollMonth: false,
            scrollYear: false,
        } );
    }

}



/*
    Rafraichissement de la liste de webconferences
*/

function refreshWebconfList( ) {

    function reloadWebconfList( ) {

        // Init. cibles
        var $updateTarget = Foundation.utils.S( '#js-update_target' );
        var $title = Foundation.utils.S( '#js-update_title' );

        // Titre initial
        var titleOrgHtml = $title.html( );

        // Requete Ajax + effets
        $title.html( MSG_LOADING );
        $updateTarget.fadeTo( 200, 0.33, function( ) {
            $updateTarget.load( window.location.pathname, function( ) {
                $updateTarget.fadeTo( 200, 1, function( ) {
                    $title.html( titleOrgHtml );    // Restauration titre
                } );
            } );
        } );

    }

    var $revealConnect = Foundation.utils.S( '#reveal-connect' );

    Foundation.utils.S( '#connect' ).on( 'click', function( event ) {
        $revealConnect.foundation( 'reveal', 'open' );
    } );

    $revealConnect.find( 'a.button' ).on( 'click', function( event ) {
        $revealConnect.foundation( 'reveal', 'close' );
        reloadWebconfList( );
    } );

}



/*
    refreshIframe : permet de remplacer la source d'une iframe par une autre.

        iframe_id represente l'id de l'iframe a rafraichir
        url fournit le lien de la page a recharger dans l'iframe
        tabsList contient une liste d'ids : le premier sera "selected", les autres ne le seront plus.
        ## pour ameliorer : on pourrait ne donner que l'id du conteneur des tabs
*/
function refreshIframe(iframe_id, url, tabsList) {
    for(var element_id in tabsList){
        if(element_id==="0"){
            document.getElementById(tabsList[element_id]).classList.add('selected');
        }else{
            document.getElementById(tabsList[element_id]).classList.remove('selected');
        }
    }
    $("#insert_wims").fadeOut();
    document.getElementById(iframe_id).src=url;
    $("#insert_wims").fadeIn();
}

