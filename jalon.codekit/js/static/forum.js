/***************************************************************************************************

    Jalon v4.5 (static) : forums

*/



/*
    Instanciation CKEditor specifique
*/

function instantiateForumCKEditor( textareaID ) {

    if ( window.CKEDITOR && window.CKEDITOR.dom ) {

        CKEDITOR.replace( textareaID, {
            customConfig: '',
            language: 'fr',
            toolbarGroups: [
                { 'name': "basicstyles", 'groups': [ "basicstyles" ] },
                { 'name': "links",       'groups': [ "links" ] },
                //{ 'name': "paragraph",   'groups': [ "list", "blocks" ] },
                { 'name': "paragraph",   'groups': [ "blocks" ] },
                { 'name': "insert",      'groups': [ "insert" ] },
                //{ 'name': "document",    'groups': [ "mode" ] },
            ],
            removePlugins: 'image,elementspath',
            removeButtons: 'Strike,Subscript,Superscript,Anchor',
            removeDialogTabs: 'link:advanced',
        } );

        return textareaID;

    } else {

        return false;
    }

}



/*
    Formulaire de reponse rapide

*/

function setForumQuickReplyForm( ) {

    var $inputReply = Foundation.utils.S( '#js-forum-quickreply' );
    instantiateForumCKEditor( 'js-forum-quickreply' );

    $inputReply.closest( 'form' ).submit( function( event ) {

        var $form = $( this );

        CKEDITOR.instances[ 'js-forum-quickreply' ].updateElement( );
        buffer = $inputReply.val( );

        if ( $( buffer ).text( ).trim( ) === '' ) {

            event.preventDefault( );
            $field = $inputReply.parent( '.field' );
            if ( ! $field.children( '.fieldErrorBox' ).length ) {
                $( '<div class="fieldErrorBox hide">Champ obligatoire</div>' )
                        .prependTo( $field )
                        .show( 'slow' );
            }
        }
    } );
}



/*
    Formulaire de recherche

*/

function setForumSearchForm( ) {

    Foundation.utils.S( '#js-forum-search' ).submit( function( event ) {

        var $form = $( this );

        if ( ! Boolean( $form.find( 'input[type="text"]' ).first( ).val( ).trim( ) ) ) {

            event.preventDefault( );
            if ( ! $form.children( '.fieldErrorBox' ).length ) {
                $( '<div class="fieldErrorBox hide">Champ obligatoire</div>' )
                        .prependTo( $form )
                        .show( 'slow' );
            }
        }
    } );
}



/*
    Suppression des citations dans l'affichage des resultats de recherche

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





