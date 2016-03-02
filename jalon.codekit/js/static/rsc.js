/*

        Jalon v4.5 (static) : Mes ressources


/***************************************************************************************************

        Modulation Foundation
*/

/*
    Anti plantage Firefox : pas de switches dans les listes si trop d'elements…
*/

function setSwitchMarkup( ) {

    //console.log( NB_LISTED_ELEMENTS );
    if ( NB_LISTED_ELEMENTS <= 250 ) {

        Foundation.utils.S( '#js-update_target .noSwitch' ).each( function( ) {
            $( this).removeClass( 'noSwitch' ).addClass( 'switch tiny round' );
            //$( this).removeClass( 'noSwitch' ).addClass( 'switch tiny round has-tip' ).attr( 'data-tooltip', true );
        } );
        Foundation.utils.S( '#js-update_target .list' ).foundation( 'switch', 'reflow' );
        //Foundation.utils.S( '#js-update_target .list' ).foundation( 'switch', 'reflow' ).foundation( 'tooltip', 'reflow' );
    }
}



/***************************************************************************************************

        Fichiers
*/

/*
    Edition
*/

//function setFileEditor( formID, revealID ) {
function setFileEditor( ) {

    //var $form = Foundation.utils.S( '#' + formID );
    var $form = Foundation.utils.S( '#js-fileEditor' );

    $form.find( '#title' ).attr( 'required', "required" ).attr( 'placeholder', $form.data( 'placeholder' ) );
    $form.find( '#archetypes-fieldname-file > span > span > img' ).remove( );
    $form.find( '#archetypes-fieldname-file > span > span > span.discreet > span' ).remove( );

    /* Casse l'upload de fichier...
    setRevealForm( formID, revealID ); //*/

    /*

        Upload de fichier en AJAX : http://malsup.com/jquery/form/#file-upload


    Foundation.utils.S( '#js-fileEditor' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );
        var param = $form.serialize( );

        //console.log( param );
        $.post( $form.attr( 'action' ), param ).done( function( data ) {
            $( '#js-update_target' ).empty( ).html( data );
            Foundation.utils.S( '#reveal-main ).foundation( 'reveal', 'close' );
            setAlertBox( 'success', $form.data( 'success_msg_pre' ) + " « " + $form.data( 'res_name' ) + " » " + $form.data( 'success_msg_post' ) );
        } );
    } ); //*/
}



/***************************************************************************************************

        Liens vers des ressources externes
*/

/*
    Creation d'un lien : choix du type
*/

function setLinkCreator( ) {

    Foundation.utils.S( '#js-linkCreator' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
            var $reveal = $( '#reveal-main' );
            $reveal.empty( ).html( data );
            revealInit( $reveal );
        } );
    } );
}


/*
    Creation d'un lien a partir du catalogue de la BU
*/

function setBULinkSearch( ) {

    Foundation.utils.S( '.js-BULinkSearch' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );
        var $reveal = Foundation.utils.S( '#reveal-main' );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
            $reveal.empty( ).html( data );
            revealInit( $reveal );
        } );
    } );
}


/*
    Creation d'un lien a partir du catalogue de la BU -> Affichage & selection
*/

function setBULinkCreator( ) {

    Foundation.utils.S( '#js-BULinkCreator' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
            $( '#js-update_target' ).empty( ).html( data );
            Foundation.utils.S( '#reveal-main' ).foundation( 'reveal', 'close' );
            setAlertBox( 'success', $form.data( 'success_msg' ) );
        } );
    } );
}


/*
    Edition d'un lien
*/

function setLinkEditor( ) {

    var $form = Foundation.utils.S( '#js-linkEditor' );

    $form.find( '#title, #lecteur' ).attr( 'required', "required" ).attr( 'placeholder', $form.data( 'placeholder' ) );
    //$form.find( '#lecteur_text_format' ).parent( 'div' ).removeAttr( 'style' );
    $form.find( '#lecteur_text_format' ).parent( 'div' ).remove( );

    Foundation.utils.S( '#js-linkEditor' ).submit( function( event ) {

        event.preventDefault( );

        var $reveal = Foundation.utils.S( '#reveal-main' );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
            var html = $.parseHTML( data );
            if ( $( html ).find( '.error' ).length ) {
                $reveal.empty( ).html( data );
                revealInit( $reveal );
            } else {
                $( '#js-update_target' ).empty( ).html( data );
                $reveal.foundation( 'reveal', 'close' );
                if ( $form.find( '#title' ).length ) {
                    setAlertBox( 'success', $form.data( 'success_msg_pre' ) + " « " + $form.find( '#title' ).attr( 'value' ) + " » " + $form.data( 'success_msg_post' ) );
                } else {
                    setAlertBox( 'success', $form.data( 'success_msg_pre' ) + " « " + $form.find( 'h3' ).text( ) + " » " + $form.data( 'success_msg_post' ) );
                }
            }
        } );
    } );
}



/***************************************************************************************************

        Termes de glossaire
*/

/*
    Edition
*/

function setGlossaryEditor( ) {

    var $form = Foundation.utils.S( '#js-glossaryEditor' );

    $form.find( '#title, #description' ).attr( 'required', "required" ).attr( 'placeholder', $form.data( 'placeholder' ) );

    setRevealForm( 'js-glossaryEditor', 'reveal-main' );
    /*
    var $form = Foundation.utils.S( '#js-glossaryEditor' );

    $form.find( '#title, #description' ).attr( 'required', "required" ).attr( 'placeholder', $form.data( 'placeholder' ) );

    $form.submit( function( event ) {

        event.preventDefault( );

        //var $reveal = $form.parent( '.reveal-modal' );
        var $reveal = Foundation.utils.S( '#reveal-main' );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
            var html = $.parseHTML( data );
            if ( $( html ).find( '.fieldErrorBox' ).text( ) ) {
                $reveal.empty( ).html( data );
                revealInit( $reveal );
            } else {
                $( '#js-update_target' ).empty( ).html( data );
                $reveal.foundation( 'reveal', 'close' );
                setAlertBox( 'success', $form.data( 'success_msg_pre' ) + " « " + $form.find( '#title' ).attr( 'value' ) + " » " + $form.data( 'success_msg_post' ) );
            }
        } );
    } ); //*/
}



/***************************************************************************************************

        Operations en relation avec les ressources et les cours
*/

/*
    Supprimer une ressource / un cours
*/

function setItemSuppressor( ) {

    Foundation.utils.S( '#js-itemSuppressor' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {

            $( '#js-update_target' ).empty( ).html( data );
            $form.parent( '.reveal-modal' ).foundation( 'reveal', 'close' );
            setAlertBox( 'success', " « " + $form.data( 'item_name' ) + " » " + $form.data( 'success_msg' ) );
        } );
    } );
}



/*
    Detacher une ressource d'un ensemble de cours
*/

function setResDetacher( ) {

    var $form = Foundation.utils.S( '#js-resDetacher' );
    var $formSubmit = $form.find( '[type="submit"]' );

    //$formSubmit.attr( 'disabled', "disabled" );
    $formSubmit.prop( 'disabled', true );

    // Bascule de selection des etiquettes
    _setTagSelector( $form );

    // Activation du submit
    $form.on( 'click', 'a.filter-button', function( ) {

        if ( $form.find( 'a.filter-button.selected' ).length ) {
            //$formSubmit.removeAttr( 'disabled' );
            $formSubmit.prop( 'disabled', false );
        } else {
            //$formSubmit.attr( 'disabled', "disabled" );
            $formSubmit.prop( 'disabled', true );
        }

    } );

    $form.submit( function( event ) {

        event.preventDefault( );

        var courseNames = [ ];
        var param = $form.serialize( );

        $form.find( 'a.selected' ).each( function( index ) {
            param += '&listeCours:list=' + $( this ).attr( 'id' );
            courseNames.push( "« " + $( this ).data( 'course_name' ) + " »" );
        } );

        $.post( $form.attr( 'action' ), param ).done( function( data ) {
            $( '#js-update_target' ).empty( ).html( data );
            $form.parent( '.reveal-modal' ).foundation( 'reveal', 'close' );
            setAlertBox( 'success', $form.data( 'success_msg_pre' ) + " « " + $form.data( 'res_name' ) + " » " + $form.data( 'success_msg_post' ) + " : " + courseNames.join( ', ' ) + "." );
        } );
    } );
}

