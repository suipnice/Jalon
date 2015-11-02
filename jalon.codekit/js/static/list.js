/***************************************************************************************************

    Jalon v4.5 (static) : initialisation d'une liste triable

        id              = id CSS du conteneur global, lequel contient un .js-update_target contenant la liste
        criterias       = tableau des criteres de tri ( [ 'nom', 'date', 'etc' ] )
        initialCriteria = critere de tri par defaut
        initialOrder    = ordre de tri par defaut
*/


function setSortableList( id, criterias, initialCriteria, initialOrder ) {

    // Instanciation de la liste
    var sortableList = new List( id, {
        valueNames: criterias,
        //indexAsync: false,
        //listClass: 'list',
        //sortClass: 'sort',
        //searchClass: 'search',
        page: 500,
    } );

    sortableList.sort( initialCriteria, { order: initialOrder } );

}

/*
var sortableList = { };

function setSortableList( id, criterias, initialCriteria, initialOrder ) {

    sortableList[ id ] = { };

    // Init.
    if ( initialOrder === undefined ) {
         initialOrder = 'asc';
    }

    // Instanciation de la liste
    sortableList[ id ].list = new List( id, {
        valueNames: criterias,
        //indexAsync: false,
        //listClass: 'list',
        //sortClass: 'sort',
        //searchClass: 'search',
        page: 500,
    } );

    // Criteres de tri initiaux
    sortableList[ id ].list.sort( initialCriteria, { order: initialOrder } );
    sortableList[ id ].criteria = initialCriteria;
    sortableList[ id ].order = initialOrder;

    // Memorisation des criteres de tri utilisateur -> cookie ou stockage navigateur ?
    //Foundation.utils.S( '#' + id ).on( 'click', 'button[data-sort]', function( event ) {
    Foundation.utils.S( '#' + id ).on( 'click', '[data-sort]', function( event ) {
        //sortableList[ id ].criteria = $( event.target ).attr( 'data-sort' );
        sortableList[ id ].criteria = $( this ).attr( 'data-sort' );
        if ( $( this ).hasClass( 'desc' ) ) {
            sortableList[ id ].order = 'desc';
        } else {
            sortableList[ id ].order = 'asc';
        }
    } );

} //*/


