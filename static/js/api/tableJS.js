    var retrievedAll = 0;
    var numberOfRowsDone = 0;
    var numberOfRows = 20;
    var next = 0;
    var delayTimer;
    var back = 1;
    var dataList = [];

    function colVis(elem) {
        var el = $(elem);
        var classVis = el.attr('data-item')
        if (el.hasClass('active')) {
            el.removeClass('active');
            $('.'+classVis).hide(); 
            hiddenCols.push(classVis);
        } else {
            el.addClass('active');
            $('.'+classVis).show();
            var idx = hiddenCols.indexOf(classVis);
            if (idx !== -1) hiddenCols.splice(idx, 1);
        };
    };

    function buildDataList(data) {
        var options = "";
        if (data['status_code'] == '200') {
            dataList = data['results'];
            dataList.sort();
            for (dl of dataList) {
                options += "<option value='" + dl + "'>";
            };
            $('#acSe').empty();
            $('#acSe').append(options);
        } else {
            dataList = [];
        };
    };

    function getDataList() {
        setVars();
        return $.ajax({
            url: searchUrl,
            data: {
                'contains': contains,
            }
        })
    };

    function getData(inStr) {
        setVars();
        $.ajax({
            url: listUrl,
            data: {
                'intent': inStr,
                'contains': contains,
                'owner': owner,
                'number_of_rows': numberOfRowsDone + numberOfRows,
                'number_of_rows_done': numberOfRowsDone,
            },
            dataType: 'json',
            success: function (data) {
                return buildTable(data);
            },
            error: function() {
            }
        });
    };

    function continueOrBackDown(data) {
        var warning = data['data'];
        var cont = confirm(warning);
        if (cont) {
            return true;
        } else {
            return false;
        };
    };

    var contDel;
    function deleteItem(elem) {
        if (typeof(getWarning) == "function") {
            contDel = getWarning(elem);
            contDel.done(function(data) {
                var cont = continueOrBackDown(data);
                if (cont) {
                    return deleteItemDef(elem);
                };
            });
        } else {
            return deleteItemDef(elem);
        }
    };


    function deleteItemDef(elem) {
        var itemUrl = $(elem).attr('data-url');
        $.ajax({
            type: "POST",
            url: itemUrl,
            dataType: "JSON",
            data: {
                csrfmiddlewaretoken: csrfToken
            },
            success: function(data) {
                $('#successUpload').remove();
                $('#failureUpload').remove();
                if (data['status_code'] == 200) {
                    $('#tableContainer').after("<div id='successUpload' class='alert alert-success text-center' role='alert'>" + data['message'] + "</div>");
                    var ingId = $(elem).attr("data-id");
                    $(".item"+ingId).remove();

                } else {
                    $('#tableContainer').after("<div id='failureUpload' class='alert alert-danger text-center' role='alert'>" + data['message'] + "</div>");
                };
            },
            error: function(xhr, textStatus, error) {
                $('#successUpload').remove();
                $('#submitButton').before("<div id='failureUpload' class='alert alert-danger text-center' role='alert'>Something went wrong. Try with different data.</div>");
            }
        });
    };

    function buildTable(data) {
        var keys = Object.keys(data);
        var rows = ""
        var nothingFound = 0;
        const hiddenStyle = 'style="display:none;" '
        for (const key of keys) {
            var keys2 = Object.keys(data[key]);
            var row = '<tr class="unoriginal item' + data[key]["id"]+ '">';
            for (const key2 of cols) {
                var startRow =  "<th scope='col' ";
                if (hiddenCols.includes(key2)) {
                    startRow += hiddenStyle;
                };
                
                if (key2 != 'id' ) {
                    if (!['name'].includes(key2)) {
                        row = row + startRow + 'class="text-center ' + key2 + '">' + data[key][key2] + '</th>';
                    } else {
                        row = row + startRow + 'class="'+ key2 + '">'
                        if (key2 != 'name') {
                            row += data[key][key2] + '</th>';
                        } else {
                            row += '<a href="' + editUrl.replace("0", data[key]["id"]) + '">' + data[key][key2] + '</a>' + '</th>';
                        };
                    };
                };
            };

            if (deletable) {
                row = row + '<td><button onclick="deleteItem(this)" data-url="' + delUrl.replace("0", data[key]["id"]) + '" data-id="'+ data[key]["id"] +'" class="btn btn-primary btn-sm"><span class="fa fa-trash"></span></button></td>';
            };

            rows = rows + row;
            nothingFound += 1;
        };

        if (nothingFound == 0) {
            if ( next == 0 ) {
                rows = '<tr class="unoriginal"><th scope="row" colspan="100">' + 
                    "Couldn't find anything for " + '"' + $('#searchInput').val().trim() + '". Try something different.' + '</th></tr>'
            } else {
                rows = '<tr class="unoriginal"><th scope="row" colspan="100">' + 
                    "No more results.</th></tr>";
                $('#nextButton').hide();
            };
        };

        $('#tableContent').append(rows);
        showNextButtonOrNot(keys.length);
        showBackButtonOrNot();
    };


    function showNextButtonOrNot(count) {
        if ( count < numberOfRows ) {
            $('#nextButton').hide();

        } else {
            $('#nextButton').show();
        };
    };


    function showBackButtonOrNot() {
        if ( next == 0 ) {
            $('#backButton').hide();

        } else {
            $('#backButton').show();
        };
    };

    function searchOnInput() {
        clearTimeout(delayTimer);
        delayTimer = setTimeout(function() {
            search = getDataList();
            search.done(function(data) {
                buildDataList(data);
            })
        }, 250);
    };

    function searchOnChange() {
        next = 0;
        $('tr.original').hide();
        $('tr.unoriginal').remove();
        var elem = $('#searchInput')
        contains = elem.val().trim().toLowerCase();

        if (dataList.includes(contains)) {
            clearTimeout(delayTimer);
            delayTimer = setTimeout(function() {
                return getData('update');
            }, 100);
        } else {
            clearTimeout(delayTimer);
            delayTimer = setTimeout(function() {
                return getData('update');
            }, 100);
            
        };
    };


    function setVars() {
        if ($('#ownData').prop('checked')) {
            owner = 1;

        } else {
            owner = 0;
        }
        contains = $('#searchInput').val().trim().toLowerCase();
        if (next == 0) {
            numberOfRows = parseInt($('#numberOfRowsSelected').val());
            numberOfRowsDone = 0;

        } else {
            numberOfRowsDone += back * numberOfRows;
        };
    };
    
    var search;
    $(document).ready(function(){
        $('#searchInput').prop('disabled',false);
        $('#numberOfRowsSelected').prop('disabled',false);
        $('#ownData').prop('disabled',false);

        $('input.oninput').on('input', function() {
            searchOnInput();
        });

        $('select.oninput').on('change', function() {
            searchOnChange();
        });
        
        showNextButtonOrNot($('tr.original').length);

        $('#nextButton').on('click', function() {
            next += 1;
            back = 1;
            $('tr.original').hide();
            $('tr.unoriginal').remove();
            $('#nextButton').hide();
            $('#backButton').hide();
            getData('update');
        });

        $('#backButton').on('click', function() {
            next -= 1;
            back = -1;
            $('tr.unoriginal').remove();
            $('#nextButton').hide();
            $('#backButton').hide();
            getData('update');
        });

        $('#colvisdd').on({"click":function(e){
              e.stopPropagation();}
        });

        $(document).keyup(function(event) {
            if ($("#searchInput").is(":focus") && event.key == "Enter") {
                searchOnChange();
            };
        });

        $('#seB').on('click', function(){
            searchOnChange();
        });

    });
