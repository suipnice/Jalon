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


/*
    Localisation datetimepicker
*/

jQuery.datetimepicker.setLocale('fr');


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
    Changement de label suivant etat du filtre des contenus Pod
*/

function setPodFilterSelector( ) {

    var $form = Foundation.utils.S( '#js-podFilterSelector' );
    var $searchLabel = Foundation.utils.S( '#term_search_label' );
    var $searchInput = Foundation.utils.S( '#term_search' );
    var label1 = $form.data( 'term_search_label1' );
    var label2 = $form.data( 'term_search_label2' );
    var placeholder1 = $form.data( 'term_search_placeholder1' );
    var placeholder2 = $form.data( 'term_search_placeholder2' );

    Foundation.utils.S( '#type_search' ).on( 'change', function( ) {

        if ( $( this ).val( ) === 'mes_videos' ) {
            $searchLabel.text( label2 );
            $searchInput.attr( 'placeholder', placeholder2 );
        } else {
            $searchLabel.text( label1 );
            $searchInput.attr( 'placeholder', placeholder1 );
        }

    } );

}



/*
    Selection multiple des contenus Pod
*/

function setPodContentMultipleSelection( ) {

    var $listForm = Foundation.utils.S( '#js-podContentsList' );
    var $listFormSubmit = $listForm.find( '[name="form.button.save"]' );
    var $pageChangeForm = Foundation.utils.S( '#pagination-page_number' );
    var $pageNumberInput = $pageChangeForm.find( '[name="page"]' );
    var pageChangeMessage = $pageChangeForm.data( 'page_change_msg1' ) + "\n" + $pageChangeForm.data( 'page_change_msg2' );
    var actualPageNumber = $pageNumberInput.val( );

    function _displayMessageOnPageChange( event ) {

        if ( $listForm.find( 'ul > li .switch > [type="checkbox"]:checked' ).length ) {

            if ( ! confirm( pageChangeMessage ) ) {

                event.preventDefault( );
                event.stopPropagation( );

                return false;
            }
        }

        return true;
    }

    switchButtonEnabledState( $listFormSubmit, false );

    $listForm.on( 'change', 'ul > li .switch > [type="checkbox"]', function( ) {

        if ( $listForm.find( 'ul > li .switch > [type="checkbox"]:checked' ).length ) {
            switchButtonEnabledState( $listFormSubmit, true );
        } else {
            switchButtonEnabledState( $listFormSubmit, false );
        }

    } );

    Foundation.utils.S( '#pagination-container' ).on( 'click', 'a.button', function( event ) {

        _displayMessageOnPageChange( event );
    } );

    $pageChangeForm.submit( function( event ) {

        if ( ! _displayMessageOnPageChange( event ) ) {
            $pageNumberInput.val( actualPageNumber );
        }
    } );

}



/*
    Constitution de la liste des inscriptions par courriel
*/

function setMailRegistrationForm( ) {

    var $registrationForm = Foundation.utils.S( '#js-mailRegistration' );
    var $registrationFormFieldset = $registrationForm.children( 'fieldset' );
    var $registrationFormButton = $registrationForm.find( 'button[type=submit]' );
    var registrationList = [ ];

    var $listForm = Foundation.utils.S( '#js-mailRegistrationList' );
    var $listFormFirstInput = $listForm.find( 'input[name=lastname]' );
    var $listInput = Foundation.utils.S( '#mailUserList' );

    var $listTableBody = $listForm.find( 'tbody' );
    var listTableRowHTML = '';

    var lastname = '';
    var firstname = '';
    var email = '';
    var mailUserList = '';
    var doubleCheck = false;

    function _validateUsersList( inputString ) {

        if ( ! Boolean( inputString.trim( ).length ) ) {

            return false;

        } else {

            var users = inputString.split( ',' );
            var index, len;

            users = users.filter( function( n ){ return n !== ''; } );

            for ( index = 0, len = users.length; index < len; ++index ) {

                users[ index ] = users[ index ].trim( );

                if ( users[ index ].search( '>' ) !== users[ index ].length - 1 ) {

                    return false;

                } else {

                    var userData = users[ index ].replace( '>', '' ).split( '<' );

                    if ( userData.length === 2 ) {

                        var reName = new RegExp( $listForm.find( 'input[name=lastname]' ).attr( 'pattern' ) );
                        var reMail = new RegExp( $listForm.find( 'input[name=email]' ).attr( 'pattern' ) );

                        if ( ! reName.test( userData[ 0 ] ) || ! reMail.test( userData[ 1 ] ) ) {

                            return false;
                        }

                    } else {

                        return false;
                    }
                }
            }

            return true;
        }

    }


    switchButtonEnabledState( $registrationFormButton, false );


    Foundation.utils.S( '#js-modeSwitcher' ).on( 'click', function( event ) {

        if ( $listForm.is( ':visible' ) ) {

            $listTableBody.fadeOut( 'fast', function( ) {

                $listForm.fadeOut( 'slow', function( ) {

                    $registrationFormFieldset.fadeIn( 'slow' );
                    switchButtonEnabledState( $registrationFormButton, true );
                    $listInput.focus( ).attr( 'required', "required" );
                } );
            } );

        } else {

            $registrationFormFieldset.fadeOut( 'slow', function( ) {

                $listForm.fadeIn( 'slow', function( ) {

                    $listTableBody.fadeIn( 'fast', function( ) {

                        if ( $listTableBody.find( 'tr' ).length ) {

                            switchButtonEnabledState( $registrationFormButton, true );

                        } else {

                            switchButtonEnabledState( $registrationFormButton, false );
                        }

                        $listFormFirstInput.focus( );
                        $listInput.removeAttr( 'required' );
                    } );
                } );
            } );
        }

    } );


    $registrationForm.submit( function( event ) {

        if ( $listForm.is( ':visible' ) ) {

            $listTableBody.find( 'tr' ).each( function( index ) {
                registrationList.push( $( this ).data( 'user_info' ) );
            } );

            $listInput.val( registrationList.join( ', ' ) );
            revealFormOnSubmitBehavior( $listForm );

        } else {

            if ( ! _validateUsersList( $listInput.val( ) ) ) {

                event.preventDefault( );
                $registrationFormFieldset.find( '.fieldErrorBox' ).html( MSG_FORM_VALIDATION_ERROR );

            } else {

                revealFormOnSubmitBehavior( $registrationForm );
            }
        }

    } );


    $listForm.submit( function( event ) {

        event.preventDefault( );

        firstname = $listForm.find( 'input[name=firstname]' ).val( ).trim( );
        lastname = $listFormFirstInput.val( ).trim( );
        email = $listForm.find( 'input[name=email]' ).val( ).trim( );
        mailUserList = firstname + ' ' + lastname + ' <' + email + '>';
        doubleCheck = false;

        $listForm.find( 'input' ).val( '' );

        listTableRowHTML = '<tr class="hide" data-user_info="' + mailUserList + '">';
        listTableRowHTML += '<td class="name">' + lastname + '</td><td class="name">' + firstname + '</td><td class="email">' + email + '</td><td>';
        listTableRowHTML += '<a title="Retirer de la liste"><i class="fa fa-minus-circle fa-lg fa-fw no-pad warning"></i></a></td></tr>';

        if ( ! $listTableBody.find( 'tr' ).length ) {

            $listForm.find( 'div.panel:last-child' ).slideDown( 'slow', function( ) {
                switchButtonEnabledState( $registrationFormButton, true );
            } );

        } else {

            $listTableBody.find( 'tr' ).each( function( ) {

                if ( $( this ).data( 'user_info' ) === mailUserList || $( this ).children( 'td.email' ).html( ) === email ) {

                    doubleCheck = true;
                    return false;
                }
            } );
        }

        if ( ! doubleCheck ) {

            $( listTableRowHTML ).appendTo( $listTableBody ).show( 'slow' );
            $listFormFirstInput.focus( );
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

            $listFormFirstInput.focus( );
        } );

    } );

}



/*
    Bascule de l'etat active / desactive d'un bouton
*/

function switchButtonEnabledState( $button, state ) {

    if ( state ) {
        $button.prop( 'disabled', false );
        //$button.removeClass( 'disabled' );
    } else {
        $button.prop( 'disabled', true );
        //$button.addClass( 'disabled' );
    }

}



/*
    Commande de l'etat active / desactive d'un bouton via checkbox
*/

function enableSubmitButtonIfCheckboxTicked( formID ) {

    var $formControls = Foundation.utils.S( '#' + formID ).children( '.formControls' );
    var $button = $formControls.children( '[type=submit]' );

    $formControls.find( '[type=checkbox]' ).on( 'click', function( event ) {

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

