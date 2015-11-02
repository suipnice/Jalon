/*

        Jalon v4.5 (static) : selection d'elements de liste en vue d'action par lot
                              ou de sélection multiple.

*/


function setBatchSelect( target, noBatch ) {

    var $target = Foundation.utils.S( '#' + target );
    var $tableHead = $target.find( 'thead' );
    var $tableBody = $target.find( 'tbody' );
    var $batchButton = $target.find( 'tfoot a.dropdown' );
    var checkBoxName = $target.find( 'thead .checkall input[type=checkbox]' ).attr( 'role' );
    var $cbAll = $tableHead.find( '.checkall input[role="' + checkBoxName + '"]' );
    var $cbItems = $tableBody.find( 'input[name="' + checkBoxName + '"]' );

    var $mailAnnounce = ( ( target === "js-createAnnounce" ) || ( target === "js-mod-annonce" ) ) ? Foundation.utils.S( '#mailAnnounce' ) : false;
    var isBatch = ( typeof noBatch === "undefined" ) ? true : !noBatch;

    // Bascule d'etat des controles d'actions par lot / submit
    function setBatchButtonActive( state ) {

        if ( state ) {
            $batchButton.removeClass( 'inactive' );
            switchButtonEnabledState( $target.find( '.formControls > [type="submit"]' ), true );
        } else {
            $batchButton.addClass( 'inactive' );
            switchButtonEnabledState( $target.find( '.formControls > [type="submit"]' ), false );
        }

    }


    /*
        Initialisation
    */

    if ( isBatch ) {

        $cbItems.prop( 'checked', false );
        $cbAll.prop( 'checked', false );

        $batchButton.on( 'click', function( event ) {

            if ( $( this ).hasClass( 'inactive' ) ) {
                event.preventDefault( );
                event.stopPropagation( );
            }

        } );

    } else if ( $mailAnnounce ) {

        var cbCheckedItemsNumber = $tableBody.find( 'input[type=checkbox]:checked' ).length;

        if ( $cbItems.length === cbCheckedItemsNumber ) {
            $cbAll.prop( 'indeterminate', false ).prop( 'checked', true );
            $mailAnnounce.prop( 'disabled', false );
        } else if ( !cbCheckedItemsNumber ) {
            $cbAll.prop( 'indeterminate', false ).prop( 'checked', false );
            $mailAnnounce.prop( 'disabled', true );
        } else {
            $cbAll.prop( 'indeterminate', true ).prop( 'checked', false );
            $mailAnnounce.prop( 'disabled', false );
        }

    } else {

        if ( $cbItems.length === $tableBody.find( 'input[type=checkbox]:checked' ).length ) {
            $cbAll.prop( 'indeterminate', false ).prop( 'checked', true );
        } else {
            $cbAll.prop( 'indeterminate', true ).prop( 'checked', false );
        }

    }


    /*
        Selection / deselection de l'ensemble
    */

    if ( $cbItems.length > 0 ) {

        $cbAll.on( 'click', function( e ) {

            e.stopPropagation( );
            var allChecked = $cbAll.prop( 'checked' );

            $cbItems.prop( 'checked', allChecked );

            if ( isBatch ) {

                if ( allChecked ) {
                    setBatchButtonActive( true );
                } else {
                    setBatchButtonActive( false );
                }

            } else if ( $mailAnnounce ) {

                var cbCheckedItemsNumber = $tableBody.find( 'input[type=checkbox]:checked' ).length;

                if ( allChecked ) {
                    $mailAnnounce.prop( 'disabled', false );
                } else {
                    $mailAnnounce.prop( 'disabled', true );
                }

            }

        } );

    } else {
        $cbAll.prop( 'disabled', true );
    }


    /*
        Selection / deselection d'un element
    */

    $tableBody.on( 'click', 'input[type=checkbox]', function( event ) {

        event.stopPropagation( );
        var checkedNbr = $tableBody.find( 'input[type=checkbox]:checked' ).length;

        if ( $cbItems.length === checkedNbr ) {

            $cbItems.prop( 'checked', true );
            $cbAll.prop( 'indeterminate', false ).prop( 'checked', true );
            if ( isBatch ) {
                setBatchButtonActive( true );
            } else if ( $mailAnnounce ) {
                $mailAnnounce.prop( 'disabled', false );
            }

        } else if ( checkedNbr === 0 ) {

            $cbItems.prop( 'checked', false );
            $cbAll.prop( 'indeterminate', false ).prop( 'checked', false );
            if ( isBatch ) {
                setBatchButtonActive( false );
            } else if ( $mailAnnounce ) {
                $mailAnnounce.prop( 'disabled', true );
            }

        } else {

            $cbAll.prop( 'indeterminate', true ).prop( 'checked', false );
            if ( isBatch ) {
                setBatchButtonActive( true );
            } else if ( $mailAnnounce ) {
                $mailAnnounce.prop( 'disabled', false );
            }

        }

    } );

}

