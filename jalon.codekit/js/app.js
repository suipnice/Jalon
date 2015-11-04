/*

        Jalon v4.5 (static)

*/


/***************************************************************************************************

    Communs

*/


//@codekit-prepend "static/list.js";    // Tri des tableaux
//@codekit-prepend "static/tool.js";    // Utilitaires


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
    Instanciation CKEditor (dupliquée depuis staff.js)
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



/*
    Legende du plan du cours

function setPlanLegend( ) {

    var $courseElements = Foundation.utils.S( '#course_plan-plan span' );
    var $courseElements2Fade = '';
    var elementTypes = [
        "type_File",
        "type_Image",
        "type_Lienweb",
        "type_Lecteurexportable",
        "type_CatalogueBU",
        "type_Presentationssonorisees",
        "type_Webconference",
        "type_Examen",
        "type_AutoEvaluation",
        "type_BoiteDepot",
        "type_SalleVirtuelle",
    ];
    var courseElementTypes = [ ];
    var hoveredElementType = '';

    for ( var i = 0; i < 11; i++ ) {

        if ( !$courseElements.hasClass( elementTypes[ i ] ) ) {
            Foundation.utils.S( '#course_plan-legend dl.typeElement dd.' + elementTypes[ i ] ).remove( );
            //Foundation.utils.S( '#course_plan-legend dl.typeElement dd.' + elementTypes[ i ] ).hide( );
        }
    }

    Foundation.utils.S( '#course_plan-legend dl.typeElement dd:not(.hide)' ).hover(

        function( event ) {
            hoveredElementType = $( this ).attr( 'class' );
            $courseElements2Fade = Foundation.utils.S( '#course_plan-plan span:not(.' + hoveredElementType + ')' );
            $courseElements2Fade.fadeTo( 200, 0.33 );
        },
        function( event ) {
            $courseElements2Fade.fadeTo( 200, 1 );
        }
    );
}
*/



/*
    Formatage conditionnel : permet de colorer sur une echelle de 4+2 teintes une colonne d'un tableau

        column_nbr represente le numero (de 1 a nCol) de la colonne a colorer
        value_max  permet de calculer les seuils de chaque teinte
        selector permet d'identifier le corps de tableau sur lequel appliquer le style
*/

function setConditionalFormat( column_nbr, value_max, selector ) {

    // Valeur par defaut du selecteur
    selector = typeof selector !== 'undefined' ? selector : "tbody";

    $( selector + " td:nth-child(" + column_nbr + ")" ).each( function( ) {

        var valeur = parseFloat( $( this ).text( ).replace( ',', '.' ) );

        switch ( true ) {

            case ( valeur === 0 ):
                $( this ).addClass( 'zero_score' );
                break;

            case ( valeur < ( 0.25 * value_max ) ):
                $( this ).addClass( 'firstQuarter' );
                break;

            case ( valeur < ( 0.50 * value_max ) ):
                $( this ).addClass( 'secondQuarter' );
                break;

            case ( valeur < ( 0.75 * value_max ) ):
                $( this ).addClass( 'thirdQuarter' );
                break;

            case ( valeur < value_max ):
                $( this ).addClass( 'lastQuarter' );
                break;

            default:
                $( this ).addClass( 'max_score' );
                break;
        }
    } );
}




/***************************************************************************************************

    Spécifique étudiants

*/


/*
    Marqueur lu / non lu
*/

function readSwitcher( ) {

    var $updateTarget = Foundation.utils.S( '#course_plan-plan' );

    $updateTarget.on( 'click', 'a.right', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        if ( !isRefreshing ) {

            isRefreshing = true;

            var $checkBox = $( this );
            var $title = Foundation.utils.S( '#js-update_title' );
            var updateUrl = $checkBox.attr( 'href' );
            var titleOrgHtml = $title.html( );

            $title.html( MSG_LOADING );
            $updateTarget.fadeTo( 200, 0.33, function( ) {
                $.get( updateUrl, function( data, status ) {
                    $checkBox.children( 'i.fa' ).toggleClass( 'fa-check-square-o fa-square-o' );
                    $updateTarget.fadeTo( 200, 1, function( ) {
                        $title.html( titleOrgHtml );
                        isRefreshing = false;
                        //alert( "Data: " + data + "\nStatus: " + status );
                    } );
                } );
            } );

        }
    } );
}




/***************************************************************************************************

    Initialisation

*/


/*
    Pseudo-constantes et variables globales
*/

// Message d'actualisation en cours
var MSG_LOADING = '<i class="fa fa-spin fa-refresh"></i>' + MSG_LOADING_TEXT;

// Message d'actualisation réussie
var MSG_LOADING_OK = '<i class="fa fa-thumbs-o-up"></i>' + MSG_LOADING_OK_TEXT;

// Verrou de rafraichissement en cours (listes)
var isRefreshing = false;



/*
    Foundation JavaScript | http://foundation.zurb.com/docs
*/

$( document ).foundation( {
    dropdown : {
        //activeClass: 'open',
        //is_hover: true,
        //opened: function( ){ },
        //closed: function( ){ },
        align: 'left',
    },
    reveal : {
        //animation: 'fadeAndPop',
        animation: 'fade',
        animation_speed: 200,
        close_on_background_click: true,
        //opened: function( ){ },
    },
    tab: {
        callback : function ( tab ) {
            var tabContainerId = tab.parent( 'ul' ).parent( 'div' ).attr( 'id' );
            var activeTab = tab.children( 'a' ).attr( 'href' ).substr( 1 );
            if ( localStorage && ( localStorage[ tabContainerId ] !== activeTab ) ) {
               localStorage[ tabContainerId ] = activeTab;
            }
        }
    },
    tooltip : {
        disable_for_touch: true,
        //disable_for_touch: false,
        touch_close_text: MSG_TAP2CLOSE_TEXT,
    },
    topbar : {
        //is_hover: false,
        custom_back_text: false,
        mobile_show_parent_link: false,
    }
} );



/*
    Document charge : actions specifiques
*/

$( document ).ready( function ( ) {

    // Gestion des erreurs AJAX
    $( document ).ajaxError( function( event, jqXHR, ajaxSettings, thrownError ) {
        Foundation.utils.S( '[data-reveal]' ).foundation( 'reveal', 'close' );
        setAlertBox( 'alert', "Une erreur est survenue", thrownError );
    } );

    // Init. reveal
    $( document ).on( 'opened.fndtn.reveal', '[data-reveal]:not(#reveal-connect)', function( ) { revealInit( $( this ) ); } );

    // Retour en haut de page
    Foundation.utils.S( window ).scroll( function ( ) { scrollerDisplay( ); } );
    Foundation.utils.S( 'body > footer' ).on( 'click', '.scroll-top', function( event ) {
        event.preventDefault( );
        event.stopPropagation( );
        if ( !Foundation.utils.S( '#breadcrumb' ).isOnScreen( ) ) {
            Foundation.utils.S( 'html, body' ).animate( { opacity: 0.8 }, 'fast' )
                .animate( { scrollTop: 0 }, 'slow' )
                .animate( { opacity: 1 }, 'fast' );
        }
    } );

} );

