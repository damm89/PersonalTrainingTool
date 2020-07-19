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
}

