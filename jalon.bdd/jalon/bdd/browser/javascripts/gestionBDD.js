/****************************************************************************/
/*** CONFIG *****************************************************************/
/****************************************************************************/

var common_content_filter = '#content>*';
var common_jqt_config = {fixed:false,speed:'fast',mask:{color:'#fff',opacity: 0.4,loadSpeed:0,closeSpeed:0}};
var common_close_filter = '';
jQuery.extend(jQuery.tools.overlay.conf, common_jqt_config);

jQuery(function($) {
    updateJavascriptsBDD($('body'));
});

function updateJavascriptsBDD(context) {
    /****************************************************************************/
    /*** OVERLAYS ***************************************************************/
    /****************************************************************************/

    search('a.showmore', context, function(el) {
        el.bind('click', function() {
            $(document).trigger('hideOpenPopover.popover');
        }).prepOverlay({
            subtype:'ajax',
            filter:common_content_filter,
            closeselector:common_close_filter,
            config:{
                closeOnClick:false,
                onLoad:function() {
                    updateJavascripts(this.getOverlay());
                    updateJavascriptsBDD(this.getOverlay());
                }
            }
        });
    });

    search('a.showmore-inform', context, function(el) {
        el.bind('click', function() {
            $(document).trigger('hideOpenPopover.popover');
        }).prepOverlay({
            subtype:"ajax",
            filter:common_content_filter,
            closeselector:common_close_filter,
            formselector: 'form#inform, form#in-form',
            noform: 'reload',
            config:{
                closeOnClick:false,
                onLoad:function() {
                    updateJavascripts(this.getOverlay());
                    updateJavascriptsBDD(this.getOverlay());
                }
            }
        });
    });

    context.find('#typeUtilisateur input#typeEnseignant').bind('click', function() {
        context.find('#archetypes-fieldname-COD_ETU').hide().find('input').val("");
        context.find('#archetypes-fieldname-PROMO_IND').hide().find('input').val("");
        updateJavascriptsBDD($(this));
    });

    context.find('#typeUtilisateur input#typeEtudiant').bind('click', function() {
        context.find('#archetypes-fieldname-COD_ETU').show();
        context.find('#archetypes-fieldname-PROMO_IND').show();
        updateJavascriptsBDD($(this));
    });

    // /****************************************************************************/
    // /*** ONGLETS ****************************************************************/
    // /****************************************************************************/

    context.find('#connecteur_bdd .onglets li a').bind('click', function(e) {
        e.preventDefault();
        context.find('#connecteur_bdd .onglets li').removeClass('selected').addClass('unselected');
        $(this).parent('li').toggleClass('selected');
        context.find('#tableauAjout').html('<div class="loading"></div>').load(this.href + ' div#tableau', function() {
            updateJavascripts($(this));
            updateJavascriptsBDD($(this));
        });
    });

    context.find('#variables_connecteur input[type="submit"]').bind('click', function(e) {
        e.preventDefault();
        form = $(this).parents('form:first');
        var formData = form.serialize();
        url = form.attr("action");
        context.find('#tableau').html('<div class="loading"></div>').load(url + ' div#tableau', formData, function() {
            updateJavascriptsBDD($(this));
        });
    });

    search('#connecteur_bdd .onglets', context, function(el) {
        setTimeout(function() {
            el.find('li a').first().trigger('click');
        }, 0); // overlay animation
    });
    // To Do : recharger résultat recherche dans même popup

    // /****************************************************************************/
    // /*** BOUTONS PAGES **********************************************************/
    // /****************************************************************************/

    context.find('#boutonPage a#pageSuiv').bind('click', function(e) {
        e.preventDefault();
        context.html('<div class="loading"></div>').load(this.href + ' div#tableau', function() {
            updateJavascriptsBDD($(this));
        });
    });

    context.find('#boutonPage a#pagePrec').bind('click', function(e) {
        e.preventDefault();
        context.html('<div class="loading"></div>').load(this.href + ' div#tableau', function() {
            updateJavascriptsBDD($(this));
        });
    });

    context.find('#numberPage').bind('keypress', function(e) {
        if (e.keyCode == 13) {
            var url_load = $(this).parent('form').attr('action') + '?page=' + this.value;
            context.html('<div class="loading"></div>').load(url_load + ' div#tableau', function() {
                updateJavascriptsBDD($(this));
            });
        }
    });
    /****************************************************************************/
    /*** TOKEN INPUT ************************************************************/
    /****************************************************************************/

    var tokenParams = {
        searchDelay: 20,
        minChars: 4,
        hintText:'Commencez à taper...',
        searchingText:'Recherche...',
        noResultsText:'Pas de résultat'
    };

    search('#input-etudiant', context, function(el) {
        el.tokenInput('./portal_jalon_bdd/recherchUtilisateurs', $.extend({}, tokenParams, {queryParam: 'rechercheEtu'}));
    });

    search('#input-enseignant', context, function(el) {
        el.tokenInput('./portal_jalon_bdd/recherchUtilisateurs', $.extend({}, tokenParams, {tokenLimit: 1, queryParam: 'rechercheEns'}));
    });


    /****************************************************************************/
    /*** LISTE DOUBLE ***********************************************************/
    /****************************************************************************/

    var of = 'sur';

    (function ($) {
        var settings = new Array();
        var group1 = new Array();
        var group2 = new Array();
        var onSort = new Array();
        $.configureBoxes = function (options) {
            var index = settings.push({
                    box1View: 'box1View',
                    box1Storage: 'box1Storage',
                    box1Filter: 'box1Filter',
                    box1Clear: 'box1Clear',
                    box1Counter: 'box1Counter',
                    box2View: 'box2View',
                    box2Storage: 'box2Storage',
                    box2Filter: 'box2Filter',
                    box2Clear: 'box2Clear',
                    box2Counter: 'box2Counter',
                    to1: 'to1',
                    allTo1: 'allTo1',
                    to2: 'to2',
                    allTo2: 'allTo2',
                    transferMode: 'move',
                    sortBy: 'text',
                    useFilters: true,
                    useCounters: true,
                    useSorting: true,
                    selectOnSubmit: true
                });
            index--;
            $.extend(settings[index], options);
            group1.push({
                    view: settings[index].box1View,
                    storage: settings[index].box1Storage,
                    filter: settings[index].box1Filter,
                    clear: settings[index].box1Clear,
                    counter: settings[index].box1Counter,
                    index: index
                });
            group2.push({
                    view: settings[index].box2View,
                    storage: settings[index].box2Storage,
                    filter: settings[index].box2Filter,
                    clear: settings[index].box2Clear,
                    counter: settings[index].box2Counter,
                    index: index
                });
            if (settings[index].sortBy == 'text') {
                onSort.push(function (a, b) {
                    var aVal = a.text.toLowerCase();
                    var bVal = b.text.toLowerCase();
                    if (aVal < bVal) {
                        return -1;
                    }
                    if (aVal > bVal) {
                        return 1;
                    }
                    return 0;
                });
            } else {
                onSort.push(function (a, b) {
                    var aVal = a.value.toLowerCase();
                    var bVal = b.value.toLowerCase();
                    if (aVal < bVal) {
                        return -1;
                    }
                    if (aVal > bVal) {
                        return 1;
                    }
                    return 0;
                });
            } if (settings[index].useFilters) {
                $('#' + group1[index].filter).keyup(function (e) {
                    var code = (e.keyCode ? e.keyCode : e.which);
                    if(code == 13) {
                        Filter(group1[index]);
                    }
                });
                $('#' + group2[index].filter).keyup(function () {
                    Filter(group2[index]);
                });
                $('#' + group1[index].clear).click(function () {
                    ClearFilter(group1[index]);
                });
                $('#' + group2[index].clear).click(function () {
                    ClearFilter(group2[index]);
                });
            }
            if (IsMoveMode(settings[index])) {
                $('#' + group2[index].view).dblclick(function () {
                    MoveSelected(group2[index], group1[index]);
                });
                $('#' + settings[index].to1).click(function () {
                    MoveSelected(group2[index], group1[index]);
                });
                $('#' + settings[index].allTo1).click(function () {
                    MoveAll(group2[index], group1[index]);
                });
            } else {
                $('#' + group2[index].view).dblclick(function () {
                    RemoveSelected(group2[index], group1[index]);
                });
                $('#' + settings[index].to1).click(function () {
                    RemoveSelected(group2[index], group1[index]);
                });
                $('#' + settings[index].allTo1).click(function () {
                    RemoveAll(group2[index], group1[index]);
                });
            }
            $('#' + group1[index].view).dblclick(function () {
                MoveSelected(group1[index], group2[index]);
            });
            $('#' + settings[index].to2).click(function () {
                MoveSelected(group1[index], group2[index]);
            });
            $('#' + settings[index].allTo2).click(function () {
                MoveAll(group1[index], group2[index]);
            });
            if (settings[index].useCounters) {
                UpdateLabel(group1[index]);
                UpdateLabel(group2[index]);
            }
            if (settings[index].useSorting) {
                SortOptions(group1[index]);
                SortOptions(group2[index]);
            }
            $('#' + group1[index].storage + ',#' + group2[index].storage).css('display', 'none');
            if (settings[index].selectOnSubmit) {
                $('#' + settings[index].box2View).closest('form').submit(function () {
                    $('#' + settings[index].box2View).children('option').attr('selected', 'selected');
                });
            }
        };

        function UpdateLabel(group) {
            var showingCount = $("#" + group.view + " option").size();
            var hiddenCount = $("#" + group.storage + " option").size();
            $("#" + group.counter).text(showingCount + ' ' + of + ' ' + (showingCount + hiddenCount));
        }

        function Filter(group) {
            var index = group.index;
            var filterLower;
            if (settings[index].useFilters) {
                filterLower = $('#' + group.filter).val().toString().toLowerCase();
            } else {
                filterLower = '';
            }
            $('#' + group.view + ' option').filter(function (i) {
                var toMatch = $(this).text().toString().toLowerCase();
                return toMatch.indexOf(filterLower) == -1;
            }).appendTo('#' + group.storage);
            $('#' + group.storage + ' option').filter(function (i) {
                var toMatch = $(this).text().toString().toLowerCase();
                return toMatch.indexOf(filterLower) != -1;
            }).appendTo('#' + group.view);
            try {
                $('#' + group.view + ' option').removeAttr('selected');
            } catch (ex) {}
            if (settings[index].useSorting) {
                SortOptions(group);
            }
            if (settings[index].useCounters) {
                UpdateLabel(group);
            }
        }

        function SortOptions(group) {
            var $toSortOptions = $('#' + group.view + ' option');
            $toSortOptions.sort(onSort[group.index]);
            $('#' + group.view).empty().append($toSortOptions);
        }

        function MoveSelected(fromGroup, toGroup) {
           var ajax = true;
           if (ajax) {
               var from = $('#'+fromGroup.view);
               var to = $('#'+toGroup.view);
               var form = from.parents('form');
               var action = form.attr('action');
               var method = form.attr('method');
               /*var COD_ELP = form.children('input#COD_ELP');
               var TYP_ELP = form.children('input#TYP_ELP');
               var TYP_ELP_SELECT = form.children('input#TYP_ELP_SELECT');*/
               var formulaire = form.serializeObject();
               delete formulaire[from.attr('name')];
               delete formulaire[to.attr('name')];

               if (action && method) {
                    formulaire['from'] = from.attr('name');
                    formulaire['to'] = to.attr('name');
                    formulaire['selected'] = from.val();

                   //var ajaxData = {from: from.attr('name'), to: to.attr('name'), selected: from.val()};
                   var evenData = {from: from, to: to, selected: from.val() };

                   $(document).trigger('listesDoublesAjaxStart', evenData);

                   $.ajax({
                       type: method, url: action,
                       data: formulaire,
                       success: function() {
                           $(document).trigger('listesDoublesAjaxSuccess', evenData);
                           MoveSelectedAjax(fromGroup, toGroup);
                       },
                       error: function() {
                           $(document).trigger('listesDoublesAjaxError', evenData);
                       },
                       complete: function() {
                           $(document).trigger('listesDoublesAjaxComplete', evenData);
                       }
                   });
               }
           } else {
               MoveSelectedAjax(fromGroup, toGroup);
           }
        }

        function MoveSelectedAjax(fromGroup, toGroup) {

            if (IsMoveMode(settings[fromGroup.index])) {
                $('#' + fromGroup.view + ' option:selected').appendTo('#' + toGroup.view);
            } else {
                $('#' + fromGroup.view + ' option:selected:not([class*=copiedOption])').clone().appendTo('#' + toGroup.view).end().end().addClass('copiedOption');
            }
            try {
                $('#' + fromGroup.view + ' option,#' + toGroup.view + ' option').removeAttr('selected');
            } catch (ex) {}
            Filter(toGroup);
            if (settings[fromGroup.index].useCounters) {
                UpdateLabel(fromGroup);
            }
        }

        function MoveAll(fromGroup, toGroup) {
            if (IsMoveMode(settings[fromGroup.index])) {
                $('#' + fromGroup.view + ' option').appendTo('#' + toGroup.view);
            } else {
                $('#' + fromGroup.view + ' option:not([class*=copiedOption])').clone().appendTo('#' + toGroup.view).end().end().addClass('copiedOption');
            }
            try {
                $('#' + fromGroup.view + ' option,#' + toGroup.view + ' option').removeAttr('selected');
            } catch (ex) {}
            Filter(toGroup);
            if (settings[fromGroup.index].useCounters) {
                UpdateLabel(fromGroup);
            }
        }

        function RemoveSelected(removeGroup, otherGroup) {
            $('#' + otherGroup.view + ' option.copiedOption').add('#' + otherGroup.storage + ' option.copiedOption').remove();
            try {
                $('#' + removeGroup.view + ' option:selected').appendTo('#' + otherGroup.view).removeAttr('selected');
            } catch (ex) {}
            $('#' + removeGroup.view + ' option').add('#' + removeGroup.storage + ' option').clone().addClass('copiedOption').appendTo('#' + otherGroup.view);
            Filter(otherGroup);
            if (settings[removeGroup.index].useCounters) {
                UpdateLabel(removeGroup);
            }
        }

        function RemoveAll(removeGroup, otherGroup) {
            $('#' + otherGroup.view + ' option.copiedOption').add('#' + otherGroup.storage + ' option.copiedOption').remove();
            try {
                $('#' + removeGroup.storage + ' option').clone().addClass('copiedOption').add('#' + removeGroup.view + ' option').appendTo('#' + otherGroup.view).removeAttr('selected');
            } catch (ex) {}
            Filter(otherGroup);
            if (settings[removeGroup.index].useCounters) {
                UpdateLabel(removeGroup);
            }
        }

        function ClearFilter(group) {
            $('#' + group.filter).val('');
            $('#' + group.storage + ' option').appendTo('#' + group.view);
            try {
                $('#' + group.view + ' option').removeAttr('selected');
            } catch (ex) {}
            if (settings[group.index].useSorting) {
                SortOptions(group);
            }
            if (settings[group.index].useCounters) {
                UpdateLabel(group);
            }
        }

        function IsMoveMode(currSettings) {
            return currSettings.transferMode == 'move';
        }
    })(jQuery);

        $(function() {
            $.configureBoxes({
                box1View : 'listeDouble1',
                box1Storage : 'stockageListeDouble1',
                box1Filter : 'champFiltreListeDouble1',
                box1Clear : 'clearFiltreListeDouble1',
                box1Counter : 'compteListeDouble1',
                to1 : 'versListeDouble1',

                box2View : 'listeDouble2',
                box2Storage : 'stockageListeDouble2',
                box2Filter : 'champFiltreListeDouble2',
                box2Clear : 'clearFiltreListeDouble2',
                box2Counter : 'compteListeDouble2',
                to2 : 'versListeDouble2',
                useSorting : false
            });

            $(document).bind('listesDoublesAjaxStart', function(e, data){
            //console.log('listesDoublesAjaxStart');
            });
            $(document).bind('listesDoublesAjaxSuccess', function(e, data){
                //console.log('listesDoublesAjaxSuccess');
            });
            $(document).bind('listesDoublesAjaxError', function(e, data){
                //console.log('listesDoublesAjaxError');
            });
            $(document).bind('listesDoublesAjaxComplete', function(e, data){
                //console.log('listesDoublesAjaxComplete');
            });
        });

    /****************************************************************************/
    /*** TAGS *******************************************************************/
    /****************************************************************************/

    context.find('#typeELP li.tag a').bind('click', function(e) {
        e.preventDefault();
        console.log("typeELP");
        context.find('#tag li').removeClass('selected').addClass('unselected');
        $(this).parent('li').toggleClass('selected');

        var vars = getUrlVars(this.href);
        var url_load = this.href.split('?')[0];

        context.find('#contenantLoadAjax').html('<div class="loading"></div>').load(url_load + ' div#contenuLoadAjax', serializeVars(vars), function() {
            context.find('#TYP_ELP_SELECT').val(vars['TYP_ELP_SELECT']);
            updateJavascriptsBDD($(this));
        });
    });

    /****************************************************************************/
    /*** BOUTON RELOAD **********************************************************/
    /****************************************************************************/

    context.find('.bouton_actualiser').bind('click', function(e) {
    location.reload(true);
    });

    /****************************************************************************/
    /*** TABLE SORTER ***********************************************************/
    /****************************************************************************/

/*
    (function($) {

        function sortabledataclass(cell){
            var re, matches;
            
            re = new RegExp("sortabledata-([^ ]*)","g");
            matches = re.exec(cell.attr('class'));
            if (matches) { return matches[1]; }
            return null;
        }

        function sortable(cell) {
            // convert a cell a to something sortable

            // use sortabledata-xxx cell class if it is defined
            var text = sortabledataclass(cell);
            if (text === null) { text = cell.text(); }

            // A number, but not a date?
            if (text.charAt(4) !== '-' && text.charAt(7) !== '-' && !isNaN(parseFloat(text))) {
                return parseFloat(text);
            }
            return text.toLowerCase();
        }

        function setoddeven() {
            var tbody = $(this);
            // jquery :odd and :even are 0 based
            tbody.find('tr').removeClass('odd').removeClass('even')
                .filter(':odd').addClass('even').end()
                .filter(':even').addClass('odd');
        }

        function sort() {
            var th, colnum, table, tbody, reverse, index, data, usenumbers, tsorted;

            th = $(this).closest('th');
            colnum = $('th', $(this).closest('thead')).index(th);
            table = $(this).parents('table:first');
            tbody = table.find('tbody:first');
            tsorted = parseInt(table.attr('sorted') || '-1', 10);
            reverse = tsorted === colnum;

            $(this).parent().find('th:not(.nosort) .sortdirection')
                .html('&#x2003;');
            $(this).children('.sortdirection').html(
                reverse ? '&#x25b2;' : '&#x25bc;');

            index = $(this).parent().children('th').index(this);
            data = [];
            usenumbers = true;
            tbody.find('tr').each(function() {
                var cells, sortableitem;

                cells = $(this).children('td');
                sortableitem = sortable(cells.slice(index,index+1));
                if (isNaN(sortableitem)) { usenumbers = false; }
                data.push([
                    sortableitem,
                    // crude way to sort by surname and name after first choice
                    sortable(cells.slice(1,2)), sortable(cells.slice(0,1)),
                    this]);
            });

            if (data.length) {
                if (usenumbers) {
                    data.sort(function(a,b) {return a[0]-b[0];});
                } else {
                    data.sort();
                }
                if (reverse) { data.reverse(); }
                table.attr('sorted', reverse ? '' : colnum);

                // appending the tr nodes in sorted order will remove them from their old ordering
                tbody.append($.map(data, function(a) { return a[3]; }));
                // jquery :odd and :even are 0 based
                tbody.each(setoddeven);
            }
        }

        $(function() {
            // set up blank spaceholder gif
            var blankarrow = $('<span>&#x2003;</span>').addClass('sortdirection');
            // all listing tables not explicitly nosort, all sortable th cells
            // give them a pointer cursor and  blank cell and click event handler
            // the first one of the cells gets a up arrow instead.
            $('table.listing:not(.nosort) thead th:not(.nosort)')
                .append(blankarrow.clone())
                .css('cursor', 'pointer')
                .click(sort);
            $('table.listing:not(.nosort) tbody').each(setoddeven);
        });

    })(jQuery);

*/

}

$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};
