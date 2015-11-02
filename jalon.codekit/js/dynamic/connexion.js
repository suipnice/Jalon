/*

        Jalon v4.5 : Connexion


    À utiliser dans « connexion_form.cpt »

        <tal:comments replace="nothing"><!--
            <script charset="UTF-8"
                    tal:content="structure python:jsBuffer.getFile('connexion')" />
        --></tal:comments>


/***************************************************************************************************

        Envoi d'un formulaire de connexion


Foundation.utils.S( '#login_form' ).submit( function( event ) {

    event.preventDefault( );

    var $form = $( this );
    var url = $form.data( 'url' );
    var $reveal = Foundation.utils.S( '#reveal-connection' );

    $.post( $form.attr( 'action' ), $form.serialize( ) ).done( function( data ) {
        //console.log( data );
        console.log( jQuery( data ) );
        //var html = $.parseHTML( data );
        //console.log( $( html ).find( '#no_auth' ).length );
        //if ( $( html ).find( '#no_auth' ).length ) {
        if ( jQuery( data ).find( '#no_auth' ).length ) {
            $reveal.empty( ).html( data );
            revealInit( $reveal );
        } else {
            $reveal.foundation( 'reveal', 'close' );
            window.location.href = url;
        }
    } );
} );
*/

