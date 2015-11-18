/***************************************************************************************************

    Jalon v4.5 (static) : outils et utilitaires

*/



/*
    Instanciation CKEditor standard
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
    Gestion standard des formulaires en "reveal"

        - ckEditorInstanceName est un ID de textarea utilisant CKEditor.

*/

// Validation et chargement d'une nouvelle page
function setRevealFormNewPage( formID, revealID, ckEditorInstanceName ) {

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
                $reveal.foundation( 'reveal', 'close' );
                document.location.href = data;
            }
        } );
    } );
}



/*
    Initialisation des "reveal"
*/

function revealInit( $reveal ) {

    // Focus sur le 1er input
    //var $firstInput = $reveal.find( 'input[type=text], input[type=password], input[type=radio], input[type=checkbox], textarea, select').filter( ':visible:first' );
    var $firstInput = $reveal.find( 'input[type=text], input[type=radio], input[type=checkbox], textarea, select').filter( ':visible:first' );
    if ( $firstInput.length > 0 ) {
        $firstInput.focus( );
    }

    // Envoi du formulaire
    $reveal.find( 'form:not(.no_reveal_action)' ).submit( function( event ) {

        // Spinner
        var $h2 = $( this ).parents( '.reveal-modal' ).children( 'h2' );
        $h2.html( $h2.text( ) + '<i class="fa fa-refresh fa-spin"></i>' );

        // Protection anti double-clic
        $( this ).find( '[type="submit"]' ).prop( 'disabled', true );
    } );
}



/*
    Suppression contenu lecteur exportable à la fermeture de son conteneur (reveal)
*/

function removePlayerOnClose( ) {

    Foundation.utils.S( '#reveal-main' ).on( 'closed', function( ) {
        $( this ).children( '.flex-video' ).remove( );
    } );
}



/*
    Suppression des images inexistantes (Primo BU)
*/

function removeErrorImages( containerId ) {

    Foundation.utils.S( '#' + containerId + ' img.primo_img' ).on( 'error', function( event ) {
        $( this ).remove( );
    } );
}



/*
    Boites d'alerte

        className = alert / warning / info / success / secondary
*/

// Disparition auto
function _alertBoxRemover( $boxContainer, $box ) {

    if ( !$box.hasClass( 'alert' ) ) {
        $box.delay( 5000 ).slideUp( function( ) { $boxContainer.remove( ); } );
    }

    $box.on( 'click', '> a.close', function( event ) {
        event.preventDefault( );
        event.stopPropagation( );
        $boxContainer.slideUp( function( ) { $( this ).remove( ); } );
    } );
}

// Injection
function setAlertBox( className, text, title ) {

    var message = "";

    if ( title ) {
        message += "<h3>" + title + "</h3>";
    }
    message += text + '<a class="close"></a>';

    var $boxContainer = $( "<div>", {
        'id': "js-alert_box",
        'class': "small-12 columns",
    } );
    var $box = $( "<div>", {
        'class': "alert-box radius " + className,
        'data-alert': "data-alert",
        'html': message,
        'css': { 'display': 'none' },
    } );

    $boxContainer.prepend( $box );
    Foundation.utils.S( 'main' ).prepend( $boxContainer );

    $box.slideDown( );

    _alertBoxRemover( $boxContainer, $box );
}

// Inline
function alterAlertBox( ) {

    $box = Foundation.utils.S( '.alert-box' );

    _alertBoxRemover( $box.parent( 'div' ), $box );
}



/*
    Affichage / masquage retour haut de page
*/

// Detection de presence d'un element dans la zone visible
$.fn.isOnScreen = function( ) {

    var win = $( window );

    var viewport = {
        top : win.scrollTop( ),
        left : win.scrollLeft( )
    };
    viewport.right = viewport.left + win.width( );
    viewport.bottom = viewport.top + win.height( );

    var bounds = this.offset( );
    bounds.right = bounds.left + this.outerWidth( );
    bounds.bottom = bounds.top + this.outerHeight( );

    return ( !(viewport.right < bounds.left || viewport.left > bounds.right || viewport.bottom < bounds.top || viewport.top > bounds.bottom) );
};

// Affichage contextuel des boutons
function scrollerDisplay( ) {

    if ( Foundation.utils.S( '#breadcrumb' ).isOnScreen( ) ) {
        Foundation.utils.S( '.scroll-top' ).fadeOut( 'fast' );
    } else {
        Foundation.utils.S( '.scroll-top' ).fadeIn( 'slow' );
    }
}



/*
    Memorisation du dernier onglet actif (vie du cours)
        ./skins/jalon_cours/macro_cours_life.pt

function setTabMemory( tabId ) {

    if ( Modernizr.localstorage && ( typeof localStorage[ tabId ] !== 'undefined' ) ) {

        //console.log( localStorage[ tabId ] );
        var $tabContainer = Foundation.utils.S( '#' + tabId );
        var $activeTab = $tabContainer.find( 'ul.tabs li.tab-title.active' );

        if ( $activeTab.children( 'a' ).attr( 'href' ).substr( 1 ) !== localStorage[ tabId ] ) {
            $activeTab.removeClass( 'active' );
            $tabContainer.find( 'div.tabs-content div.content.active' ).removeClass( 'active' );
            $tabContainer.find( 'li.tab-title a[href*="#' + localStorage[ tabId ] + '"]' ).parent( ).addClass( 'active' );
            $tabContainer.find( 'div.tabs-content div#' + localStorage[ tabId ] ).addClass( 'active' );
        }
    }
}
*/

