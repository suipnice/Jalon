/***************************************************************************************************

    Jalon v4.5 : fonctionnalites specifiques aux roles "Manager" et "Secretaire"

*/


/*
    Inclusions CodeKit specifiques
*/

//@codekit-prepend "static/vanilladualselect/vanilladualselect.js";



/***************************************************************************************************

    Gestion pedagogique (portal_jalon_bdd)

*/


/*
    Offre de formation : responsable
*/

function setFormOfferResp( ) {

    _setTokenParams( );

    Foundation.utils.S( '#input-auteurs' ).tokenInput(
        ABSOLUTE_URL + '/recherchUtilisateurs',
        $.extend( { }, tokenParams, {
            queryParam: 'rechercheEns',
            tokenLimit: 1
        } )
    );
}



/*
    Offre de formation : enseignant
*/

function setFormOfferTeacher( ) {

    _setTokenParams( );

    Foundation.utils.S( '#input-coauteurs' ).tokenInput(
        ABSOLUTE_URL + '/recherchUtilisateurs',
        $.extend( { }, tokenParams, {
            queryParam: 'rechercheEns',
        } )
    );
}



/*
    Offre de formation : etudiant
*/

function setFormOfferStudent( ) {

    _setTokenParams( );

    Foundation.utils.S( '#input-coauteurs' ).tokenInput(
        ABSOLUTE_URL + '/recherchUtilisateurs',
        $.extend( { }, tokenParams, {
            queryParam: 'rechercheEtu',
        } )
    );
}



/*
    Utilisateurs : creation / edition
*/

function setFormUserEdition( ) {

    var $createForm = Foundation.utils.S( '#admin-user_edit-form' );
    var $studentInfoBlock = Foundation.utils.S( '#js-studentInfo' );

    $createForm.on( 'click', 'input[name="TYPE_IND"]', function( event ) {

        if ( $( this ).val( ) === 'Etudiant' ) {
            if ( $studentInfoBlock.is( ':hidden' ) ) {
                $studentInfoBlock.slideDown( );
            }
        } else {
            if ( $studentInfoBlock.is( ':visible' ) ) {
                $studentInfoBlock.slideUp( 400, function( ) {
                    $( this ).find( 'input[type="text"]' ).val( '' );
                } );
            }
        }

    } );

}

