var delayTimer;
var received_data;
var numberOfRows = 10;
var numberOfRowsDone = 0;
var datalistId;
var idStr;
var ingData = {};
var selectedOption;
var ingredientsIds;
var dataKeys;


var WEIGHT_MULTIPLIERS = {
    'kg':10,
    'gram':0.01,
    'oz':.2835,
    'lb':4.5359237,
    'piece':1,
}

function doMetricCalc(quantityString, wmultiplier) {
    var result = parseFloat(wmultiplier);
    var quantity = quantityString.replace(/[^\d\.]*/g, '');
    if (quantity.length > 0) {
        quantity = parseFloat(quantity);
        if (isNaN(quantity)){
            return result
        } else {
            result = wmultiplier * quantity;
            return result
        };
    } else {
        return result
    };
}

function stringTo100g(quantityString) {
    quantityString = quantityString.replace(/ /g,'').replace(/,/,'.');
    var found = 0;
    for (let key in WEIGHT_MULTIPLIERS) {
        if(WEIGHT_MULTIPLIERS.hasOwnProperty(key)){
            if ( quantityString.search(key) > 0) {
                found = 1;
                multiplier = doMetricCalc(quantityString, WEIGHT_MULTIPLIERS[key]);
                break
            };
      }
    };
    if (found == 0) {
        multiplier = doMetricCalc(quantityString, 1)
    };
    return multiplier
};

function roundToNearestDecimal(number) {
    return Math.round( 10 * number) / 10
};


function calculateTableQuantities() {
    //
    var kcals = 0;
    var protein = 0;
    var carbs = 0;
    var fats = 0;

    $('input[id*=original_quantity]:visible').each(function() {
        var elem = $(this);
        var oqId = elem.attr('id')
        var atId = oqId.replace('original_quantity','amount_type');
        var multiplier = WEIGHT_MULTIPLIERS[$('#'+atId).val()] * parseFloat(elem.val());
        if (isNaN(multiplier)) {
            multiplier = 1;
        };

        if ( ingData.hasOwnProperty(oqId) ) {
            protein = protein + multiplier * parseFloat(ingData[oqId]['protein']);
            carbs = carbs + multiplier * parseFloat(ingData[oqId]['carbs']);
            fats = fats + multiplier * parseFloat(ingData[oqId]['fats']);
            kcals = 4 * (protein + carbs) + 9 * fats;
        };
    });

    leanness = Math.round( 1000 * (protein * 4) / kcals) / 10;
    if (isNaN(leanness)) {
        leanness = 0;
    };
    leanness = String(leanness) + '%';
    $('#leanness').text(leanness);
    $('#kcals').text(roundToNearestDecimal(kcals));
    $('#protein').text(roundToNearestDecimal(protein));
    $('#carbs').text(roundToNearestDecimal(carbs));
    $('#fats').text(roundToNearestDecimal(fats));
};


function buildIngDatalist(data) {
    //
    var keys = Object.keys(data);
    var rows = ""
    var nothingFound = 0;
    for (const key of keys) {
        var keys2 = Object.keys(data[key]);
        row = '<option class="dl-option" data-id="' + data[key]['id'] + '" value="'+ data[key]['name'] + '">' + data[key]['name'] + '</option>';
        rows = rows + row;
        nothingFound += 1;
    };
    if (nothingFound == 0) {
        console.log("Didn't find anything.")
    };
    $('#'+datalistId).append(rows);
};


function getData(elem) {
    // 
    datalistId = $(elem).attr('list');
    idStr = $(elem).attr('id');
    contains = $('#'+idStr).val().trim();
    $('#'+datalistId).empty();
    $.ajax({
        url: getIngredientListUrl,
        data: {
            'intent': 'update',
            'contains': contains,
            'owner': '0',
            'number_of_rows': numberOfRowsDone + numberOfRows,
            'number_of_rows_done': numberOfRowsDone,
        },
        dataType: 'json',
        success: function (data) {
            return buildIngDatalist(data);
        },
        error: function(xhr, textStatus, error) {
            console.log(xhr.responseText);
            console.log(xhr.statusText);
            console.log(textStatus);
            console.log(error)
            $('#primaryAction').before("<div id='failureUpload' class='alert alert-danger text-center' role='alert'>Something went wrong. Try with different data.</div>");
        }
    });
};


function getIngVars() {
    // Gets ingredient's ids and id's of the quantity fields
    ingredientsIds = [];
    dataKeys = [];
    $('input[id*=ingredient]:hidden').each(function(){
        elem = $(this);
        if (elem.val() != '') {
            ingredientsIds.push( elem.val() );
            dataKeys.push(elem.attr('id').replace('ingredient','original_quantity') );
        };
    });
};


function getIngredientData() {
    // First fills ingredientsIds and dataKeys and calls ajax function to get data on the different ingredients. 
    // if successfull, then calls the calculateTableQuantities function to calculate the table values
    getIngVars();
    $.ajax({
        url: getIngredientDataUrl,
        data: {
            'ingredient_ids': ingredientsIds.join(),
            'data_keys':dataKeys.join()
        },
        dataType: 'json',
        success: function (data) {
            ingData = data;
            calculateTableQuantities();
        },
        error: function() {
        }
    });
};


function changeValueHiddenInput(elem) {
    // Changes the value of the hidden inputs for the different ingredients

    var datalstId = $(elem).attr('id').replace('ingredient_name','datalist');
    var ingredientPk = $('#'+datalstId+' option[value="' + $(elem).val() + '"]').attr('data-id');
    var hiddenInputId = $(elem).attr('id').replace('ingredient_name','ingredient');
    $('#'+hiddenInputId).val(ingredientPk);
    getIngredientData();
};


var delayTimer;
function delayedFunction(func, elem=0, waitTime=500) {
    // Function that calls another function <func> with a delay of <waitTime>
    clearTimeout(delayTimer);
    delayTimer = setTimeout(function() {
        if (elem == 0) {
            return func();
        } else {
            return func(elem)
        }
    }, waitTime);
};

function findChoice(elem) {
    var optionFound = false;
    var dlId = elem.attr('list');
    var datalistOptions = $('#'+dlId+' option');

    // Determine whether an option exists with the current value of the input.
    elVal = elem.val();
    for (var j = 0; j < datalistOptions.length; j++) {
        if (elVal == datalistOptions[j].value) {
            optionFound = true;
            break;
        }
    };
    return optionFound;
}

function validateChoice(elem) {
    optionFound = findChoice(elem);
    // use the setCustomValidity function of the Validation API
    // to provide an user feedback if the value does not exist in the datalist
    if (optionFound) {
        elem[0].setCustomValidity('');
        elem.removeClass('is-invalid');
        return true
    } else {
        elem[0].setCustomValidity('Please select a value from list.');
        elem.addClass('is-invalid');
        elem[0].reportValidity();
        return false
    };
};

function validateIngredientRow(elem){
    validation = validateChoice($(elem));
    qElemId = $(elem).attr('id').replace('ingredient_name','original_quantity');
    aElemId = $(elem).attr('id').replace('ingredient_name','amount_type');
    if (validation) {
        changeValueHiddenInput($(elem));
        $('#'+qElemId).prop('disabled',false);
        $('#'+aElemId).prop('disabled',false);
        
    } else {
        $('#'+qElemId).prop('disabled',true);
        $('#'+aElemId).prop('disabled',true);
    };
};

function addToRemoveRow(elem) {
    ingId = elem.parent().prev().attr('id').replace('ingredient','original_quantity');
    delete ingData[ingId];
    var ingDataKeys = Object.keys(ingData);
    for (var i = 0; i < ingDataKeys.length; i++) {
        ingData[i] = ingData[ingDataKeys[i]];
        delete ingData[ingDataKeys[i]];
    };
    for (var i = 0; i < ingDataKeys.length; i++) {
        ingData['id_form-'+String(i)+'-original_quantity'] = ingData[i];
        delete ingData[i];
    };
    calculateTableQuantities();
}

function addToDeleteClick() {
    $('.delete-row').off('click.addtoremoverow');
    $('.delete-row').on('click.addtoremoverow', function() {
        addToRemoveRow($(this));
    });
};

function addBindingsToIngredientSearch(selectorString) {
    $(selectorString).prop('disabled',false);
    $(selectorString).on('input', function() {
        optionFound = findChoice($(this));
        if (!optionFound) {
            delayedFunction(getData, elem=$(this));
        };
    });
    $(selectorString).on('change').blur();
}

$(document).ready(function(){
    addBindingsToIngredientSearch('.ingredient-search');

    if ($('#id_name').val() != '') {
        $(getIngredientData())
        $('.quantity-input').prop('disabled',false);
        $('input[id*=original_quantity]:visible').prop('disabled',false);
    };

    $(document).on('input','input[id*=original_quantity]:visible', function() {
        calculateTableQuantities();
    });

    $(document).on('change', '.quantity-input', function() {
        calculateTableQuantities();
    });

    $(document).on('change','.ingredient-search', function() {
        validateIngredientRow(this);
    });
    
    addToDeleteClick();
    $('.add-row').on('click', function() {
        addBindingsToIngredientSearch('.ingredient-search:last');
        addToDeleteClick();
    });

});