/*

        Jalon v4.5 (static) : etiquetage et traitements par lot


/***************************************************************************************************

        Filtrage d'une liste d'elements lors de la selection d'etiquettes

*/

function setTagFilter( inPopup ) {

    var inReveal = ( typeof inPopup === "undefined" ) ? false : true;

    Foundation.utils.S( '#js-tag_filter' ).on( 'click', 'li > a.filter-button', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        if ( !isRefreshing ) {

            // Verrouilage
            isRefreshing = true;

            // Init. cibles
            var $tagButton = $( this );
            var $updateTarget, $title, $submitButton;
            if ( inReveal ) {
                $updateTarget = Foundation.utils.S( '#js-popup-update_target' );
                $title = Foundation.utils.S( '#js-popup-update_title' );
                $submitButton = $updateTarget.parent( 'form' ).find( 'button[type=submit]' );
            } else {
                $updateTarget = Foundation.utils.S( '#js-update_target' );
                $title = Foundation.utils.S( '#js-update_title' );
                $submitButton = false;
            }

            // Mise a jour de l'etat
            updateTagButtonState( $tagButton );

            // Titre initial
            var titleOrgHtml = $title.html( );

            // Parametres du "load"
            var subjects = [ ];
            var updateUrl = $updateTarget.data( 'href' );
            Foundation.utils.S( '#js-tag_filter > li > a.selected' ).each( function( index ) {
                subjects.push( $( this ).attr( 'id' ) );
            } );

            // Requete Ajax + effets + maj bouton
            $title.html( MSG_LOADING );
            $updateTarget.fadeTo( 200, 0.33, function( ) {
                $updateTarget.load( updateUrl, 'subject=' + subjects.join( ), function( ) {
                    $updateTarget.fadeTo( 200, 1, function( ) {
                        // Restauration titre
                        $title.html( titleOrgHtml );
                        // Forcage de la perte du focus pour le bouton (chgmt de couleur)
                        $tagButton.blur( );
                        // Desactivation du bouton "submit" le cas echeant.
                        if ( $submitButton ) {
                            $submitButton.prop( 'disabled', true );
                        }
                        // Deverrouilage
                        isRefreshing = false;
                    } );
                } );
            } );
        }

    } );
}



/***************************************************************************************************

        Creation / suppression d'etiquettes et etiquetage d'une ressource

*/


/*
    Recherche de doublon
*/

function _checkDuplicateTag( tag, excludeId ) {

    var tag2Check = removeDiacritics( tag.trim( ).replace( /\s/g, " " ) ).toLowerCase( ),
        suppCriteria = "",
        isDupe = false;

    if ( typeof excludeId !== "undefined" ) {
        suppCriteria = ":not(#" + excludeId + ")";
    }

    console.log( "tag = " + tag + " / excludedId = " + excludeId );

    $( '#js-tag_filter > li > a:not(#last)' + suppCriteria ).each( function( index ) {

        existingTag = removeDiacritics( $( this ).text( ).trim( ).replace( /\s/g, " " ) ).toLowerCase( );
        console.log( index + " : " + existingTag );

        if ( existingTag === tag2Check ) {
            isDupe = true;
            return false;
        }
    } );

    return isDupe;
}


/*
    Creation d'une etiquette
*/

function createTag( ) {

    Foundation.utils.S( '#js-createTag' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this ),
            $reveal = Foundation.utils.S( '#reveal-tags' ),
            $tagTitleContainer = $reveal.find( '#archetypes-fieldname-title' ),
            $tagTitleErrorBox = $tagTitleContainer.find( '> .fieldErrorBox' ),
            id = $form.find( 'input[name="tag_id"]' ).val( ),
            title = $form.find( 'input[name="title"]' ).val( );

        if ( ! _checkDuplicateTag( title ) ) {

            if ( $tagTitleErrorBox.length ) {
                $tagTitleErrorBox.remove( );
            }

            revealFormOnSubmitBehavior( $form );

            $.post( $form.attr( 'action' ), $form.serialize( ), null, 'html' ).done( function( data ) {
                var html = $.parseHTML( data );
                if ( $( html ).find( '.error' ).length ) {
                    $reveal.html( data );
                    revealInit( $reveal );
                } else {
                    Foundation.utils.S( '#js-tag_filter' ).append( ' <li><a id="' + id + '" class="filter-button unselected"><i class="fa fa-circle no-pad"></i><i class="fa fa-circle-thin no-pad"></i> ' + title + '</a>' );
                    Foundation.utils.S( '#js-update_target' ).empty( ).html( data );
                    $reveal.foundation( 'reveal', 'close' );
                    setAlertBox( 'success', $form.data( 'success_msg_pre' ) + ' « ' + title + ' » ' + $form.data( 'success_msg_post' ) );
                }
            } );

        } else {

            if ( $tagTitleErrorBox.length ) {
                $tagTitleErrorBox.text( $form.data( 'error_msg_duplicate' ) );
            } else {
                $tagTitleContainer.append( '<div class="fieldErrorBox">'
                    + $form.data( 'error_msg_duplicate' ) + '</div>' );
            }
        }

    } );
}


/*
    Edition d'une etiquette
*/

function editTag( ) {

    var $form = Foundation.utils.S( '#js-editTag' ),
        $tagId = $form.find( 'input[name="tag_id"]' ),
        $tagTitle = $form.find( 'input[name="title"]' ),
        tagTitle = "",
        //$submitButton = $form.find( 'button[type="submit"]' );
        $submitButton = $form.find( 'button[name="form.button.edit_tag"]' );


    $form.on( 'change', 'select[name="tag_list"]', function( ) {

        var tagId = $( this ).find( 'option:selected' ).val( ),
            emptyText = $form.data( 'empty_text' );

        tagTitle = $( this ).find( 'option:selected' ).text( ).trim( );

        if ( tagId === "0" ) {

            $tagId.val( "0" );
            $tagTitle.val( emptyText ).attr( 'readonly', "readonly" );
            $submitButton.attr( 'disabled', "disabled" );

        } else {

            $tagId.val( tagId );
            $tagTitle.val( tagTitle ).removeAttr( 'readonly' );
            $submitButton.removeAttr( 'disabled' );
        }

    } );


    $form.submit( function( event ) {

        event.preventDefault( );

        var $reveal = Foundation.utils.S( '#reveal-tags' ),
            $tagTitleContainer = $reveal.find( '#archetypes-fieldname-title' ),
            $tagTitleErrorBox = $tagTitleContainer.find( '> .fieldErrorBox' ),
            tagId = $form.find( 'input[name="tag_id"]' ).val( ),
            title = $form.find( 'input[name="title"]' ).val( ).trim( ),
            errorMessage = "";

        if ( title === tagTitle ) {
            errorMessage = $form.data( 'error_msg_identical' );
        } else if ( _checkDuplicateTag( title, tagId ) ) {
            errorMessage = $form.data( 'error_msg_duplicate' );
        }

        if ( errorMessage === "" ) {

            if ( $tagTitleErrorBox.length ) {
                $tagTitleErrorBox.remove( );
            }

            revealFormOnSubmitBehavior( $form );

            $.post( $form.attr( 'action' ), $form.serialize( ), null, 'html' ).done( function( data ) {

                var html = $.parseHTML( data );

                if ( $( html ).find( '.error' ).length ) {

                    $reveal.html( data );
                    revealInit( $reveal );

                } else {

                    $( '#' + tagId ).html( '<i class="fa fa-circle no-pad"></i><i class="fa fa-circle-thin no-pad"></i> ' + title );
                    $reveal.foundation( 'reveal', 'close' );
                    setAlertBox( 'success',
                                 $form.data( 'success_msg_pre' )
                                 + ' « ' + tagTitle + ' » '
                                 + $form.data( 'success_msg_post' )
                                 + ' « ' + title + ' ».' );
                }
            } );

        } else {

            if ( $tagTitleErrorBox.length ) {
                $tagTitleErrorBox.text( errorMessage );
            } else {
                $tagTitleContainer.append( '<div class="fieldErrorBox">'
                    + errorMessage + '</div>' );
            }
        }

    } );
}


/*
    Suppression d'une etiquette
*/

function delTag( ) {

    Foundation.utils.S( '#js-delTag' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this ),
            $updateTarget = Foundation.utils.S( '#js-update_target' ),
            $title = Foundation.utils.S( '#js-update_title' ),
            titleOrgHtml = $title.html( );

        $title.html( MSG_LOADING );

        $updateTarget.fadeTo( 200, 0.33, function( ) {

            $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {

                $( '#' + $form.children( 'input[name=tag_id]' ).val( ) )
                    .parent( 'li' ).remove( );

                $updateTarget.empty( ).html( data );

                $updateTarget.fadeTo( 200, 1, function( ) {

                    $title.html( titleOrgHtml );
                    setAlertBox( 'success',
                                 $form.data( 'success_msg_pre' )
                                 + ' « ' + $form.data( 'tag_name' )
                                 + ' » ' + $form.data( 'success_msg_post' ) );
                } );
            } );
        } );

    } );
}


/*
    Etiquetage d'une ressource
*/

function setResTagger( ) {

    var $form = Foundation.utils.S( '#js-resTagger' );

    _setTagSelector( $form );

    $form.submit( function( event ) {

        event.preventDefault( );
        var param = "form.submitted=1&formulaire=etiqueter";

        $form.find( 'a.selected' ).each( function( index ) {
            //param += '&listeTag:list=' + encodeURIComponent( $( this ).attr( 'id' ) );
            param += '&listeTag:list=' + $( this ).attr( 'id' );
        } );

        $.post( $form.attr( 'action' ), param ).done( function( data ) {
            $( '#js-update_target' ).empty( ).html( data );
            $form.parent( '.reveal-modal' ).foundation( 'reveal', 'close' );
            setAlertBox( 'success',
                         $form.data( 'success_msg_pre' )
                         + ' « ' + $form.data( 'res_name' )
                         + ' » ' + $form.data( 'success_msg_post' ) );
        } );

    } );
}



/***************************************************************************************************

        Traitements par lot (etiquetage / desetiquetage / suppression de ressources)

*/

function setActionBatch( ) {

    /*
        Etiquetage par lot : macro_form.pt -> etiqueter-lots
    */

    var $tagForm = Foundation.utils.S( '#tag_sel > form' );
    var $tagFormSubmit = $tagForm.find( '[type="submit"]' );

    // Bascule de selection des etiquettes
    _setTagSelector( $tagForm );

    // Activation du submit
    $tagForm.on( 'click', 'a.filter-button', function( ) {

        if ( $tagForm.find( 'a.filter-button.selected' ).length ) {

            //$tagFormSubmit.removeAttr( 'disabled' );
            $tagFormSubmit.prop( 'disabled', false );

        } else {

            //$tagFormSubmit.attr( 'disabled', "disabled" );
            $tagFormSubmit.prop( 'disabled', true );
        }

    } );

    // Affichage de la liste des ressources concernees
    $( document ).on( 'open.fndtn.reveal', '#tag_sel', function ( ) {

        $tagForm.find( '#tagPanelMessage' ).remove( );
        $tagForm.find( 'a.filter-button.selected' ).removeClass( 'selected' ).addClass( 'unselected' );
        //$tagFormSubmit.attr( 'disabled', "disabled" );
        $tagFormSubmit.prop( 'disabled', true );

        var tagMessage = "";
        var nRes = 0;

        Foundation.utils.S( '#js-update_target tbody input[name="paths:list"]:checked' ).each( function( index ) {
            tagMessage += '<li>' + $( this ).data( 'res_name' ) + '</li>';
            nRes++;
        } );

        if ( nRes > 1 ) {
            tagMessage = $tagForm.data( 'p_tag_msg' ) + '<ul>' + tagMessage + '</ul>';
        } else {
            tagMessage = $tagForm.data( 's_tag_msg' ) + '<ul>' + tagMessage + '</ul>';
        }

        $tagForm.prepend(
            $( "<div>", {
                'id': "tagPanelMessage",
                'class': "panel callout radius",
                'html': tagMessage
            } )
        );

    } );

    // Envoi des donnees du formulaire
    $tagForm.submit( function( event ) {

        event.preventDefault( );

        var param = "lots=lots";

        $tagForm.find( 'a.selected' ).each( function( index ) {
            //param += '&listeTag:list=' + encodeURIComponent( $( this ).attr( 'id' ) );
            param += '&listeTag:list=' + $( this ).attr( 'id' );
        } );

        Foundation.utils.S( '#js-update_target tbody input[name="paths:list"]:checked' ).each( function( index ) {
            param += '&paths:list=' + $( this ).attr( 'value' );
        } );

        $.post( $tagForm.attr( 'action' ), param ).done( function( data ) {
            Foundation.utils.S( '#tag_sel' ).foundation( 'reveal', 'close' );
            setAlertBox( 'success', $tagForm.data( 'success_msg' ) );
        } );

    } );


    /*
        Desetiquetage par lot : macro_form.pt -> desetiqueter-lots
    */

    Foundation.utils.S( '#untag_sel > form' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );
        var tags = [ ];
        var param = "lots=lots";

        Foundation.utils.S( '#js-tag_filter a.selected' ).each( function( index ) {
            tags.push( $( this ).attr( 'id' ) );
        } );
        param += '&tagsupp=' + tags.join( );

        Foundation.utils.S( '#js-update_target tbody input[name="paths:list"]:checked' ).each( function( index ) {
            param += '&paths:list=' + $( this ).attr( 'value' );
        } );

        $.post( $form.attr( 'action' ), param ).done( function( data ) {
            $( '#js-update_target' ).empty( ).html( data );
            Foundation.utils.S( '#untag_sel' ).foundation( 'reveal', 'close' );
            setAlertBox( 'success', $form.data( 'success_msg' ) );
        } );

    } );

    // Affichage de la liste des ressources concernees
    $( document ).on( 'open.fndtn.reveal', '#untag_sel', function ( ) {

        Foundation.utils.S( '#untagPanelMessage' ).remove( );

        var $untagForm = Foundation.utils.S( '#untag_sel > form' );
        var tmpMessage = "";
        var untagMessage = "";
        var nRes = 0;

        Foundation.utils.S( '#js-tag_filter a:not(#last).selected' ).each( function( index ) {
            tmpMessage += '<li>' + $( this ).text( ) + '</li>';
        } );
        untagMessage = $untagForm.data( 'untag_msg' ) + '<ul>' + tmpMessage + '</ul>';

        tmpMessage = "";

        Foundation.utils.S( '#js-update_target tbody input[name="paths:list"]:checked' ).each( function( index ) {
            tmpMessage += '<li>' + $( this ).data( 'res_name' ) + '</li>';
            nRes++;
        } );
        if ( nRes > 1 ) {
            untagMessage = untagMessage + $untagForm.data( 'p_untag_msg' ) + '<ul>' + tmpMessage + '</ul>';
        } else {
            untagMessage = untagMessage + $untagForm.data( 's_untag_msg' ) + '<ul>' + tmpMessage + '</ul>';
        }

        $untagForm.prepend(
            $( "<div>", {
                'id': "untagPanelMessage",
                'class': "panel warning radius",
                'html': untagMessage
            } )
        );

    } );


    /*
        Suppression par lot : macro_form.pt -> supprimer-lots
    */

    Foundation.utils.S( '#del_sel > form' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );
        var nonSup = "";
        var param = $form.serialize( );

        Foundation.utils.S( '#js-update_target tbody input[name="paths:list"]:checked' ).each( function( index ) {
            if ( !$( this ).data( 'attached' ) ) {
                param += '&paths:list=' + $( this ).attr( 'value' );
            }
        } );

        $.post( $form.attr( 'action' ), param ).done( function( data ) {
            $( '#js-update_target' ).empty( ).html( data );
            Foundation.utils.S( '#del_sel' ).foundation( 'reveal', 'close' );
            setAlertBox( 'success', $form.data( 'success_msg' ) );
        } );

    } );

    // Affichage de la liste des ressources concernees
    $( document ).on( 'open.fndtn.reveal', '#del_sel', function ( ) {

        Foundation.utils.S( '#suppPanelMessage' ).remove( );
        Foundation.utils.S( '#attPanelMessage' ).remove( );

        var $delForm = Foundation.utils.S( '#del_sel > form' );
        var suppMessage = "";
        var attMessage = "";
        var nSupp = 0;
        var nAtt = 0;

        Foundation.utils.S( '#js-update_target tbody input[name="paths:list"]:checked' ).each( function( index ) {
            if ( !$( this ).data( 'attached' ) ) {
                suppMessage += '<li>' + $( this ).data( 'res_name' ) + '</li>';
                nSupp++;
            } else {
                attMessage += '<li>' + $( this ).data( 'res_name' ) + '</li>';
                nAtt++;
            }
        } );

        if ( nSupp ) {

            $delForm.find( 'div.alert' ).show( );
            //$delForm.find( '[type="submit"]' ).removeAttr( 'disabled' ).show( );
            $delForm.find( '[type="submit"]' ).prop( 'disabled', false ).show( );

            if ( nAtt ) {
                if ( nAtt > 1 ) {
                    attMessage = $delForm.data( 'p_att_msg' ) + '<ul>' + attMessage + '</ul>';
                } else {
                    attMessage = $delForm.data( 's_att_msg' ) + '<ul>' + attMessage + '</ul>';
                }
                $delForm.prepend(
                    $( "<div>", {
                        'id': "attPanelMessage",
                        'class': "panel callout radius",
                        'html': attMessage
                    } )
                );
            }

            if ( nSupp > 1 ) {
                suppMessage = $delForm.data( 'p_supp_msg' ) + '<ul>' + suppMessage + '</ul>';
            } else {
                suppMessage = $delForm.data( 's_supp_msg' ) + '<ul>' + suppMessage + '</ul>';
            }

            $delForm.prepend(
                $( "<div>", {
                    'id': "suppPanelMessage",
                    'class': "panel warning radius",
                    'html': suppMessage
                } )
            );

        } else {

            $delForm.find( 'div.alert' ).hide( );
            //$delForm.find( '[type="submit"]' ).attr( 'disabled', "disabled" ).hide( );
            $delForm.find( '[type="submit"]' ).prop( 'disabled', true ).hide( );

            suppMessage = $delForm.data( 'all_att_msg' );

            if ( nAtt > 1 ) {
                suppMessage += " " + $delForm.data( 'p_all_att_msg' );
            } else {
                suppMessage += " " + $delForm.data( 's_all_att_msg' );
            }

            $delForm.prepend(
                $( "<div>", {
                    'id': "suppPanelMessage",
                    'class': "panel warning radius",
                    'html': suppMessage
                } )
            );
        }

    } );
}

