// HTMX and SSE
function onHtmxLoaded() {
    htmx.on('htmx:sseError', function (evt) {
        if (htmx.find("#price")) {
            htmx.find("#price").value = htmx.find("#price-log").innerHTML
            htmx.remove(htmx.find("#sse-container-outer"));
        } else {
            htmx.find("#price-output").innerHTML = htmx.find("#price-log").innerHTML
            htmx.remove(htmx.find("#sse-container"));
        }
    });
}

if ('htmx' in window) {
    onHtmxLoaded();
} else {
    var script = document.getElementById('htmx-script');
    script.addEventListener('load', onHtmxLoaded);
}

// Auto-Complete
$('.basicAutoComplete').autoComplete({
    resolverSettings: {
        url: '/station_autocomplete'
    }
})

// Swap origin and destination
document.addEventListener('DOMContentLoaded', function () {
    let reverseDirection = document.getElementById('reverse-direction');
    if (reverseDirection) {
        reverseDirection.addEventListener('click', function swapValues() {
            const origin_temp = document.getElementById("origin").value;
            document.getElementById("origin").value = document.getElementById("destination").value;
            document.getElementById("destination").value = origin_temp;
        });
    }
});
