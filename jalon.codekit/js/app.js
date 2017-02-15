/***************************************************************************************************

        Jalon v4.5 : fonctionnalités communes

*/


/*
    Inclusions CodeKit specifiques
*/

//@codekit-prepend "static/list.js";    // Tri des tableaux
//@codekit-prepend "static/tool.js";    // Utilitaires
//@codekit-prepend "static/forum.js";   // Forums



/***************************************************************************************************

        Cours

*/


/*
    Comportements des elements de plan
*/

function setPlanChapterSelection( ) {

    var $form = Foundation.utils.S( '#course-chapter_form' ),
        $plan = Foundation.utils.S( '#course_plan-plan' );

    $form.on( 'change', 'select[name="course_title"]', function( ) {

        if ( !isRefreshing ) {

            // Verrouilage
            isRefreshing = true;

            // Init
            var $title = Foundation.utils.S( '#js-update_title' ),
                titleOrgHtml = $title.html( );

            // Traitement
            $title.html( MSG_LOADING );
            $plan.fadeTo( 200, 0.33, function( ) {

                $.ajax( {
                    type: 'POST',
                    url: ABSOLUTE_URL + "/display_course_map_title_page",
                    data: $form.serialize( ),
                    success: function( data ) {
                        $title.html( MSG_LOADING_OK );
                        $plan.empty( ).html( data ).fadeTo( 200, 1, function( ) {
                            $title.html( titleOrgHtml );
                        } );
                    },
                    error: function( data, textStatus, errorThrown ) {
                        console.log( errorThrown );
                        console.log( textStatus );
                    },
                    complete: function( ) {
                        // Deverrouillage
                        isRefreshing = false;
                    }
                } );
            } );
        }
    } );

}


function setPlanChapterFolding( disclosureState ) {

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

        if ( ! $( this).hasClass( 'disabled' ) ) {

            if ( $( this ).parent( 'li' ).is( ':first-child' ) ) {

                if ( isStaff ) {
                    setStaffPlanChapterFolding( true );
                } else {
                    setPlanChapterFolding( true );
                }

            } else if ( $( this ).parent( 'li' ).is( ':last-child' ) ) {

                if ( isStaff ) {
                    setStaffPlanChapterFolding( false );
                } else {
                    setPlanChapterFolding( false );
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

function setPlanChapterFold( $target ) {

    $target.closest( 'li' ).toggleClass( 'collapsed expanded' );
    setLegendBarButtonsActivation( );

}


/*
    Initialisation de tous les chapitres du plan a l'etat deplie
*/

function expandPlanChapters( ) {

    Foundation.utils.S( '#course_plan-plan li.branch:not(.element)' )
        //.removeClass( 'collapsed' )
        .addClass( 'expanded' );
}


/*
    Barres de navigation "collantes"
*/

function setStickyItem( ) {

    function _stickyItem( $item, $stickyContainer ) {

        if ( $item.isOnScreen( ) ) {

            if ( isSticky ) {

                $stickyContainer.fadeOut( 'fast', function( ) {
                    $stickyContainer.children( ).detach( ).appendTo( $item );
                } );
                isSticky = false;
            }

        } else {

            if ( ! isSticky ) {

                $item.children( ).detach( ).appendTo( $stickyContainer );
                $stickyContainer.fadeIn( 'fast' );
                isSticky = true;
            }
        }
    }

    var isSticky = false,
        $item = Foundation.utils.S( '#has_sticky_content' ),
        $stickyContainer = Foundation.utils.S( '#sticky_container' ).find( 'nav' );

    $stickyContainer.fadeOut( 'fast' );
    $item.parent( ).css( 'min-height', function( ) {
        return $( this ).outerHeight( );
    } );

    _stickyItem( $item, $stickyContainer );

    $( window ).on( 'scroll', function( ) {

        _stickyItem( $item, $stickyContainer );
    } );
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

function setPlanChapterFoldCommand( ) {

    Foundation.utils.S( '#course_plan-plan' ).on( 'click', '.js-fold', function( ) {

        setPlanChapterFold( $( this ) );
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

    // Affichage contextuel des boutons de retour en haut de page
    Foundation.utils.S( window ).scroll( function ( ) {
        if ( Foundation.utils.S( '#breadcrumb' ).isOnScreen( ) ) {
            Foundation.utils.S( '.scroll-top' ).fadeOut( 'fast' );
        } else {
            Foundation.utils.S( '.scroll-top' ).fadeIn( 'slow' );
        }
    } );

    // Retour en haut de page
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

