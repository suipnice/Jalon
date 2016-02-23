/***************************************************************************************************

        Selection & filtrage d'elements « vanilla JS »

            rev 1 - P. Pomedio - 04/2015
*/


function setSelectionForm( ) {

    var selectionForm = document.getElementById( 'js-selection_form' );
    var selected = document.getElementById( 'js-selected_list' );
    var complete = document.getElementById( 'js-complete_list' );
    var submitButton = selectionForm.querySelector( 'button[type=submit]' );
    var selectedList = selected.querySelector( 'select' );
    var completeList = complete.querySelector( 'select' );
    var searchPanel = complete.getElementsByClassName( 'panel' )[ 0 ];
    var filterInput = searchPanel.querySelector( 'input:not(disabled)' );
    var filterDisplay = searchPanel.querySelector( 'input:disabled' );
    var filterLaunch = searchPanel.querySelector( 'ul > li:first-child > button' );
    var filterReset = searchPanel.querySelector( 'ul > li:last-child > button' );
    var filteredItemsCounter = 0;
    var filterData = '';
    var filterRE = '';


    /*
     *  Lancement d'une operation avec affichage / masquage du « spinner »
     */

    function _proceedWithSpinner( callback ) {

        filterInput.focus( );
        $( '#js-selection_form span.label' ).fadeIn( 300, callback ).fadeOut( 300 );

    }


    /*
     *  Affichage du nombre d'« option » selectionees
     */

    function _updateSelectedCount( ) {

        selected.getElementsByTagName( 'p' )[ 0 ].querySelector( 'span' ).textContent = selectedList.length;

    }


    /*
     *  Affichage du nombre d'« option » affichees par le « select » global
     */

    function _updateCompleteCount( ) {

        complete.getElementsByTagName( 'p' )[ 0 ].querySelector( 'span' ).textContent = filteredItemsCounter;

    }


    /*
     *  Masquage des « option » du « select » global selon le filtre
     */

    function _hideMatchingOptions( ) {

        var options = completeList.options;

        filteredItemsCounter = 0;

        for ( i = 0; i < completeList.length; i++ ) {

            if ( options[ i ].text.match( filterRE ) === null ) {
                options[ i ].className = 'hide';
            } else {
                options[ i ].className = '';
                filteredItemsCounter++;
           }
        }

        _updateCompleteCount( );

    }


    /*
     *  Filtrage des « option » du « select » global
     */

    function _filterOptions( ) {

        if ( filterData ) {

            filterRE = new RegExp( filterData, 'gi' );
            _hideMatchingOptions( );
            filterDisplay.value = "Filtrage : " + filterData;
            filterReset.removeAttribute( 'disabled' );
        }

    }


    /*
     *  Tri des « option » d'un « select » selon leur « text »
     */

    function _sortOptions( list ) {

        var listData = [ ];
        var listLength = list.length;

        if ( listLength !== 0 ) {

            for ( i = 0; i < listLength; i++ ) {

                var data = [ ];

                data.optSort = list.options[ i ].text.toUpperCase( );
                data.optText = list.options[ i ].text;
                data.optValue = list.options[ i ].value;

                listData[ i ] = data;
            }

            listData.sort( function ( a, b ) {

                if ( a.optSort > b.optSort ) { return 1; }
                if ( a.optSort < b.optSort ) { return -1; }
                return 0;
            });

            for ( i = 0; i < listLength; i++ ) {

                list.options[ i ].value = listData[ i ].optValue;
                list.options[ i ].text = listData[ i ].optText;
            }
        }

    }


    /*
     *  Transfert de l'element selectionne du « select » source vers le « select » cible
     */

    function _swapItem( sourceList, targetList) {

        if ( sourceList.selectedIndex !== -1 ) {

            var option = new Option( sourceList.options[ sourceList.options.selectedIndex ].text, sourceList.options[ sourceList.options.selectedIndex ].value );

            sourceList.removeChild( sourceList.options[ sourceList.options.selectedIndex ] );
            targetList.options[ ( targetList.length ) ] = option;

            /*
            if ( selectedList.length < 1 ) {
                submitButton.setAttribute( 'disabled', "disabled" );
            } else {
                submitButton.removeAttribute( 'disabled' );
            } //*/

            _sortOptions( targetList );

            if ( targetList === completeList ) {
                _hideMatchingOptions( );
            } else {
                filteredItemsCounter = completeList.length - completeList.getElementsByClassName( 'hide' ).length;
                _updateCompleteCount( );
            }

            _updateSelectedCount( );
        }

    }


    /*
        Initialisation
    */

    _proceedWithSpinner( function( ) {
        filterInput.focus( );
        filterInput.value = '';
        filterDisplay.value = '';
        for ( i = 0; i < selectedList.length; i++ ) {
            $( '#js-complete_list select option[value="' + selectedList.options[ i ].value + '"]' ).remove( );
        }
        filteredItemsCounter = completeList.length;
        _updateSelectedCount( );
        _updateCompleteCount( );
        _sortOptions( selectedList );
        _sortOptions( completeList );
    } );

    if ( filteredItemsCounter >= 10000 ) {
        $( '#js-highNumberWarning' ).slideDown( 'slow' );
    }


    /*
        Selection
    */

    completeList.addEventListener( 'click', function( ) {

        filterInput.focus( );
        _swapItem( completeList, selectedList );

    }, false );


    /*
        Deselection
    */

    selectedList.addEventListener( 'click', function( ) {

        _proceedWithSpinner( function( ) {
            _swapItem( selectedList, completeList );
        } );

    }, false );


    /*
        Saisie d'un critere de filtrage
    */

    filterInput.addEventListener( 'keyup', function( event ) {

        filterData = filterInput.value.trim( );

        if ( filterData ) {
            filterLaunch.removeAttribute( 'disabled' );
        } else {
            filterLaunch.setAttribute( 'disabled', "disabled" );
        }

        if ( filterRE ) {
            filterReset.removeAttribute( 'disabled' );
        } else {
            filterReset.setAttribute( 'disabled', "disabled" );
        }

    }, false );


    /*
        Declenchement du filtrage : touche « Entree »
    */

    filterInput.addEventListener( 'keypress', function( event ) {

        if ( event.keyCode === 13 ) {

            event.preventDefault( );
            event.stopPropagation( );

            _proceedWithSpinner( _filterOptions );
        }

    }, false );


    /*
        Declenchement du filtrage : bouton « Filtrer »
    */

    filterLaunch.addEventListener( 'click', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        _proceedWithSpinner( _filterOptions );

    }, false );


    /*
        RAZ filtrage
    */

    filterReset.addEventListener( 'click', function( event ) {

        event.preventDefault( );
        event.stopPropagation( );

        filterRE = '';
        filterInput.value = '';
        filterDisplay.value = '';

        filterReset.setAttribute( 'disabled', "disabled" );
        filterLaunch.setAttribute( 'disabled', "disabled" );

        _proceedWithSpinner( function( ) {

            for ( i = 0; i < completeList.length; i++ ) {
                completeList.options[ i ].className = '';
            }

            filteredItemsCounter = completeList.length;
            _updateCompleteCount( );

        } );

    }, false );


    /*
        « submit » du « form »
    */

    selectionForm.addEventListener( 'submit', function( event ) {

        submitButton.setAttribute( 'disabled', "disabled" );

        var selectedItems = selectedList.length;

        if ( selectedItems > 0 ) {

            for ( var i = 0; i < selectedItems; i++ ) {
                selectedList.options[ i ].selected = true;
            }

            return true;

        } else {

            return false;
        }

    }, false );


}

