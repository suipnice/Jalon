/*

        Jalon v4.5 (static) : Mes etudiants


/***************************************************************************************************

        Envoi d'un courriel a un diplome, une UE, un groupe etc.

*/

function setUESendMail( ) {

    Foundation.utils.S( '#js-UESendMail' ).submit( function( event ) {

        event.preventDefault( );

        var $form = $( this );
        var $reveal = Foundation.utils.S( '#reveal-etudiants' );

        $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
            var html = $.parseHTML( data );
            if ( $( html ).find( '.fieldErrorBox' ).text( ) ) {
                $reveal.empty( ).html( data );
                revealInit( $reveal );
            } else {
                $reveal.foundation( 'reveal', 'close' );
                setAlertBox( 'success', $form.data( 'success_msg' ) );
            }
        } );
    } );
}

