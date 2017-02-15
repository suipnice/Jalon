/***************************************************************************************************

        Jalon v4.5 (static) : Mes cours (staff)

*/



/***************************************************************************************************

        Liste des cours

*/


/*
    Duplication d'un cours
*/

function setCourseDuplicator( ) {

    Foundation.utils.S( '#js-courseDuplicator' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
            Foundation.utils.S( '#js-update_target' ).empty( ).html( data );
            Foundation.utils.S( '#reveal-main' ).foundation( 'reveal', 'close' );
            setAlertBox( 'success', $form.data( 'success_msg_pre' ) + " « " + $form.data( 'course_name' ) + " » " + $form.data( 'success_msg_post' ) );
        } );
    } );
}



/*
    Filtrage des cours favoris

function setFavoritesFilter( ) {

    Foundation.utils.S( '#js-list-cours a.filter-button' ).on( 'click', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        if ( !isRefreshing ) {

            // Verrouilage
            isRefreshing = true;

            // Init.
            var $favButton = $( this );
            var $updateTarget = Foundation.utils.S( '#js-update_target' );
            var $title = Foundation.utils.S( '#js-update_title' );
            var titleOrgHtml = $title.html( );

            // Mise a jour de l'etat / de l'url
            var hRef = $favButton.data( 'href' );
            if ( updateTagButtonState( $favButton ) ) {
                hRef += "favori";
            }

            // Requete Ajax + effets
            $title.html( MSG_LOADING );
            $updateTarget.fadeTo( 200, 0.33, function( ) {
                $updateTarget.load( hRef, function( ) {
                    $updateTarget.fadeTo( 200, 1, function( ) {
                        // Restauration titre
                        $title.html( titleOrgHtml );
                        // Forcage de la perte du focus pour le bouton (chgmt de couleur)
                        $favButton.blur( );
                        // Deverrouilage
                        isRefreshing = false;
                    } );
                } );
            } );
        }

    } );
}
*/



/*
    Bascule de cours favoris

    http://tice221.unice.fr:8080/jalon/cours/ppomedio/Cours-ppomedio-20140117155843/setFavori?fav=Oui

function setFavoriteState( ) {

    Foundation.utils.S( '#js-list-cours .list' ).on( 'click', 'a.favorite-selector', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        if ( !isRefreshing ) {

            // Verrouilage
            isRefreshing = true;

            // Init.
            var $favSwitch = $( this );
            var $updateTarget = Foundation.utils.S( '#js-update_target' );
            var $title = Foundation.utils.S( '#js-update_title' );
            var toFavori = $favSwitch.data( 'to_favori' );
            var message = $favSwitch.data( 'success_msg_pre' ) + " « " + $favSwitch.data( 'item_name' ) + " » ";
            var titleOrgHtml = $title.html( );

            // Assemblage du message / maj attribut
            if ( toFavori === "Oui" ) {
                message += $favSwitch.data( 'success_msg_post_fav' );
            } else {
                message += $favSwitch.data( 'success_msg_post_nofav' );
            }

            // Requete Ajax + effets
            $title.html( MSG_LOADING );
            $updateTarget.fadeTo( 200, 0.33, function( ) {
                $updateTarget.load( $favSwitch.attr( 'href' ), function( ) {
                    $updateTarget.fadeTo( 200, 1, function( ) {
                        setAlertBox( 'success', message );          // Affichage du message
                        $title.html( titleOrgHtml );                // Restauration titre
                        Foundation.utils.S( '.tooltip' ).hide( );   // Masquege tooltip residuel
                        isRefreshing = false;                       // Deverrouilage
                    } );
                } );
            } );
        }

    } );
}
*/




/***************************************************************************************************

        Plan du cours

*/


/*
    Attachement d'un element de "Mon espace" hors Biblio. / Glossaire
*/

function setAttachmentCreator( ) {

    setTagFilter( true );

    Foundation.utils.S( '#js-attachmentCreator' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( url ) {
            $.get( url ).done( function( data ) {
                $( '#course_plan-plan' ).html( data );
                Foundation.utils.S( '#reveal-main-large' ).foundation( 'reveal', 'close' );
                $( document ).foundation( 'dropdown', 'reflow' );
                //$( document ).foundation( { dropdown: { align: 'left' } } );
                setAlertBox( 'success', $form.data( 'success_msg' ) );
            } );
        } );
    } );
}



/*
    Tri des elements et fonctionnalites attachees
*/

function setSortablePlan( ) {

    if ( matchMedia( Foundation.media_queries.small ).matches
        && !matchMedia( Foundation.media_queries.medium ).matches ) {

        //setAlertBox( 'warning', "Small media detected" );
        /*
            Une fois la position depliee / repliee memorisee cote srv,
            l'appel à app/setPlanChapterFolding( ) devra être supprime
            et remplace par app/setLegendBarButtonsActivation( ).
        */
        setPlanChapterFolding( true );
        //setLegendBarButtonsActivation( );
        setPlanBehaviors( true );
        setStaffPlanChapterFoldCommand( );

    } else {

        //setAlertBox( 'warning', "Medium & up media detected" );
        var $coursePlan = Foundation.utils.S( '#course_plan-plan' );

        $coursePlan.find( '.elemtextelibre > span:first-of-type li' ).addClass( 'js-unsortable' );

        $coursePlan.nestedSortable( {

            items: 'li:not(.js-unsortable)',
            handle: 'div',
            tabSize: 20,
            isTree: true,
            maxLevels: 5,
            doNotClear: true,
            expandOnHover: 700,
            startCollapsed: false,
            placeholder: 'placeholder',
            expression: '([^-=_]*)[-=_](.+)',
            rootID: 'course_plan-plan',

            leafClass: 'leaf',
            branchClass: 'branch',
            disabledClass: 'legend',        // N'est pas prise en compte par la serialisation.
            hoveringClass: 'hovering',
            expandedClass: 'expanded',
            collapsedClass: 'collapsed',
            disableNestingClass: 'element', // Ne prend pas de sous-element.
            errorClass: 'error',

            update: function( event, ui ) {

                if ( !isRefreshing ) {

                    // Verrouilage
                    isRefreshing = true;

                    // Init.
                    var $title = Foundation.utils.S( '#js-update_title' );
                    var titleOrgHtml = $title.html( );

                    // Actualisation
                    $title.html( MSG_LOADING );
                    Foundation.utils.S( '.tooltip' ).hide( );
                    $coursePlan.fadeTo( 200, 0.33, function( ) {

                        $.ajax( {
                            type: "POST",
                            url: ABSOLUTE_URL + "/order_course_map_item_script",
                            //dataType: "json",
                            data: {
                                plan: $coursePlan.nestedSortable( 'serialize' ),
                                classe: ui.item[ 0 ].className,
                                idAttente: ui.item[ 0 ].id
                            },
                            /*success: function( data ) {
                                console.log( data );
                            },*/
                            error: function( data, textStatus, errorThrown ) {
                                console.log( errorThrown );
                                console.log( textStatus );
                            },
                            complete: function( ) {
                                $title.html( MSG_LOADING_OK );
                                //$coursePlan.delay( 600 ).fadeTo( 200, 1, function( ) {
                                $coursePlan.fadeTo( 200, 1, function( ) {
                                    $title.html( titleOrgHtml );
                                    isRefreshing = false;
                                } );
                            }
                        } );
                    } );
                }
            }
        } );

        setPlanBehaviors( true );
        //setLegendBarButtonsActivation( ); // Decommenter quand etat des chapitres memorise cote srv
        setStaffPlanChapterFoldCommand( );

    }
}



/*
    Memorisation du pliage / repliage de tous les chapitres du plan de cours
*/

function setStaffPlanChapterFolding( disclosureState ) {

    if ( !isRefreshing ) {

        // Verrouilage
        isRefreshing = true;

        // Init
        var $plan = Foundation.utils.S( '#course_plan-plan' ),
            $title = Foundation.utils.S( '#js-update_title' ),
            titleOrgHtml = $title.html( );

        // Actualisation
        $title.html( MSG_LOADING );
        $plan.fadeTo( 200, 0.33, function( ) {

            $.ajax( {
                type: "GET",
                url: ABSOLUTE_URL + "/open_course_map_item_script",
                data: {
                    id: "all" ,
                    open: disclosureState,
                },
                success: function( data ) {
                    $title.html( MSG_LOADING_OK );
                    setPlanChapterFolding( disclosureState );
                    $plan.fadeTo( 200, 1, function( ) {
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
}



/*
    Commande et memorisation du pliage / repliage d'un chapitre du plan de cours
*/

function setStaffPlanChapterFoldCommand( ) {

    var $plan = Foundation.utils.S( '#course_plan-plan' );

    $plan.on( 'click', '.js-fold', function( ) {

        if ( !isRefreshing ) {

            // Verrouilage
            isRefreshing = true;

            // Init
            var $target = $( this ),
                $parentListItem = $target.closest( 'li' ),
                $title = Foundation.utils.S( '#js-update_title' ),
                titleOrgHtml = $title.html( );

            // Actualisation
            $title.html( MSG_LOADING );
            $plan.fadeTo( 200, 0.33, function( ) {

                $.ajax( {
                    type: "GET",
                    url: ABSOLUTE_URL + "/open_course_map_item_script",
                    data: {
                        id: $parentListItem.attr('id') ,
                        open: $parentListItem.hasClass( 'collapsed' ),
                    },
                    success: function( data ) {
                        $title.html( MSG_LOADING_OK );
                        setPlanChapterFold( $target );
                        $plan.fadeTo( 200, 1, function( ) {
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



/***************************************************************************************************

        Acces et preferences : acces etudiants

*/


/*
    Parametrage TokenInput
*/

var tokenParams = { };

function _setTokenParams( ) {

    tokenParams = {
        minChars: 4,
        hintText: MSG_TOKEN_HINT_TEXT,
        searchingText: MSG_TOKEN_SEARCH_TEXT,
        noResultsText: MSG_TOKEN_EMPTY_TEXT,
        preventDuplicates: true
    };
}



/*
    Etudiants : inscriptions individuelles
*/

function setLDAPSearch( ) {

    _setTokenParams( );

    Foundation.utils.S( '#input-groupe' ).tokenInput(
        ABSOLUTE_URL + '/rechercherUser',
        $.extend( {}, tokenParams, {
            queryParam: 'groupe'
        } )
    );
}



/*
    Enseignants : gestion des auteurs
*/

function setAuthorMod( ) {

    _setTokenParams( );

    Foundation.utils.S( '#input-auteurs' ).tokenInput(
        ABSOLUTE_URL + '/rechercherUser',
        $.extend( {}, tokenParams, {
            queryParam: 'coauteur',
            tokenLimit: 1
        } )
    );
}



/*
    Enseignants : gestion des co-auteurs / co-lecteurs
*/

function setCoAuthorReaderMod( ) {

    _setTokenParams( );

    Foundation.utils.S( '#input-coauteurs' ).tokenInput(
        ABSOLUTE_URL + '/rechercherUser',
        $.extend( {}, tokenParams, {
            queryParam: 'coauteur'
        } )
    );
}



/*
    Inscriptions listes scolarites
*/

function setApogeeSearch( ) {

    Foundation.utils.S( '#js-Apogee_search' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );
        var $reveal = Foundation.utils.S( '#reveal-main' );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
            $reveal.empty( ).html( data );
            revealInit( $reveal );
        } );
    } );
}


