/*

        Jalon v4.5 (static)

*/


/***************************************************************************************************

    Communs

*/


//@codekit-prepend "static/list.js";    // Tri des tableaux
//@codekit-prepend "static/tool.js";    // Utilitaires
//@codekit-prepend "static/forum.js";   // Forums




/*
    Comportements des elements de plan de cours
*/

function setPlanChapterDisclosure( disclosureState ) {

    var $target = Foundation.utils.S( '#course_plan-plan li.branch:not(.element)' ),
        $legendBar = Foundation.utils.S( '#course_plan .legend_bar' ),
        $legendBardDown = $legendBar.find( ' > li:first-child > a' ),
        $legendBardUp = $legendBar.find( ' > li:last-child > a' );

    if ( disclosureState ) {

        $legendBardDown.addClass( 'disabled' );
        $legendBardUp.removeClass( 'disabled' );
        $target.removeClass( 'collapsed' ).addClass( 'expanded' );

    } else {

        $legendBardUp.addClass( 'disabled' );
        $legendBardDown.removeClass( 'disabled' );
        $target.removeClass( 'expanded' ).addClass( 'collapsed' );
    }
}


function setPlanBehaviors( isNotStudent ) {

    Foundation.utils.S( '#course_plan .legend_bar' ).on( 'click', 'li:not(:nth-child(2)) > a', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        var isStaff = ( typeof isNotStudent === "undefined" ) ? false : true;

        if ( ! $( this).hasClass( '.disabled' ) ) {

            if ( $( this ).parent( 'li' ).is( ':first-child' ) ) {

                if ( isStaff ) {
                    setStaffPlanChapterDisclosure( true );
                } else {
                    setPlanChapterDisclosure( true );
                }

            } else if ( $( this ).parent( 'li' ).is( ':last-child' ) ) {

                if ( isStaff ) {
                    setStaffPlanChapterDisclosure( false );
                } else {
                    setPlanChapterDisclosure( false );
                }
            }

            $( this ).blur( );

        }
    } );

    Foundation.utils.S( '#course_plan-plan' ).on( {

        mouseenter: function( ) {

            $( this ).parent( 'li' ).addClass( 'outlineTitleContainer' );
        },
        mouseleave: function( ) {

            $( this ).parent( 'li' ).removeClass( 'outlineTitleContainer' );
        }
    }, '.elemtitre' );

}


/*
    Actualisation de l'activation des boutons « Tout deplier » et « Tout replier »
*/

function setLegendBarButtonsActivation( ) {

    var $plan = Foundation.utils.S( '#course_plan-plan' ),
        $legendBar = Foundation.utils.S( '#course_plan .legend_bar' ),
        $legendBardDown = $legendBar.find( ' > li:first-child > a' ),
        $legendBardUp = $legendBar.find( ' > li:last-child > a' );

    $legendBardDown.removeClass( 'disabled' );
    $legendBardUp.removeClass( 'disabled' );

    if ( ! $plan.find( '.collapsed:visible' ).length ) {

        $legendBardDown.addClass( 'disabled' );
    }

    if ( ! $plan.find( '.expanded:visible' ).length ) {

        $legendBardUp.addClass( 'disabled' );
    }
}


/*
    Pliage / repliage des chapitres du plan de cours
*/

function setPlanChapterDisclose( $target ) {

    $target.closest( 'li' ).toggleClass( 'collapsed expanded' );
    setLegendBarButtonsActivation( );

}



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

    Specifique etudiants

*/


/*
    Commande du pliage / repliage des chapitres du plan de cours
*/

function setPlanChapterDiscloseCommand( ) {

    Foundation.utils.S( '#course_plan-plan' ).on( 'click', '.js-disclose', function( ) {

        setPlanChapterDisclose( $( this ) );
    } );
}


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
                        //console.log( "Data: " + data + "\nStatus: " + status );
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

// Chemin de base CKEditor
var CKEDITOR_BASEPATH = '/++resource++jalon.theme.javascript/ckeditor/';

// Message d'actualisation en cours
var MSG_LOADING = '<i class="fa fa-spin fa-refresh"></i>' + MSG_LOADING_TEXT;

// Message d'actualisation reussie
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

