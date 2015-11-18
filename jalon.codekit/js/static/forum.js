/***************************************************************************************************

    Jalon v4.5 (static) : forums

*/



/*
    Forums : gestion des formulaires de recherche / de reponse rapide

        - ckEditorInstanceName est un ID de textarea utilisant CKEditor.

*/

function setForumSearchReplyForm( formID, ckEditorInstanceName ) {

    if ( typeof ckEditorInstanceName !== 'undefined' ) {
        ckEditorInstanceName = instantiateCKEditor( ckEditorInstanceName );
    } else {
        ckEditorInstanceName = false;
    }

    Foundation.utils.S( '#' + formID ).submit( function( event ) {

        if ( ckEditorInstanceName ) {
            CKEDITOR.instances[ ckEditorInstanceName ].updateElement( );
        }

        var $form = $( this );

        if ( $form.find( 'input[type="text"]' ).first( ).val( ) === ""
                || $form.find( 'textarea' ).first( ).val( ) === "" ) {

            event.preventDefault( );
            $form.find( 'div.fieldErrorBox' ).fadeIn( );
        }
    } );
}



/*
    Forums : suppression des citations dans l'affichage des resultats de recherche

*/

function cleanForumSearchResults( ) {

    Foundation.utils.S( '#searchResults dd span' ).each( function( index ) {

        var resultText = $( this ).html( );
        var lastQuote = resultText.lastIndexOf( 'blockquote' );

        if ( lastQuote > 0 ) {
            $( this ).html( resultText.substr( lastQuote + 14 ) );
        }

    } );

    /* A FAIRE :

        suppression des doublons de moindre pertinence
        (cas ou le terme recherché n'apparait que dans la citation) :
        ->  parcourir le contenu et supprimer les eventuels resultats
            suivants celui en cours si la description est identique.
    */

}



/*
    Filtrage des conversations sans réponse

function setForumUnansweredConversationsFilter( ) {

    Foundation.utils.S( '#js-filter' ).on( 'click', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        var $filterButton = $( this );

        if ( !isRefreshing ) {

            if ( $filterButton.hasClass( 'unselected' ) ) {

                isRefreshing = true;
                var $answeredConversations = Foundation.utils.S( '#js-update_target tbody tr.answered' );

                if ( $answeredConversations.length < Foundation.utils.S( '#js-update_target tbody tr' ).length ) {

                    $answeredConversations.fadeOut( 200, function( ) {
                        // Suppression (pb css !important)
                        $( this ).remove( );
                    } );

                } else {

                    Foundation.utils.S( '#list-forum span.title-legend' ).fadeTo( 200, 0 );
                    Foundation.utils.S( '#js-update_target' ).fadeTo( 200, 0, function( ) {
                        $( this ).empty( ).append( '<div class="panel callout radius">' + MSG_FORUM_NO_EMPTY_CONVERSATION + '</div>' ).fadeTo( 200, 1 );
                    } );
                }

                $filterButton.toggleClass( 'unselected selected' );
                isRefreshing = false;

            } else {

                // TODO : rechargement AJAX ?
                document.location.reload( );

            }
        }
    } );
}
*/





