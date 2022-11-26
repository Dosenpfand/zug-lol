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

// Select the node that will be observed for mutations
const targetNode = document.getElementById('output');

// Options for the observer (which mutations to observe)
const config = {attributes: true, childList: true};

// Callback function to execute when mutations are observed
const callback = (mutationList, observer) => {
    for (const mutation of mutationList) {
        if (mutation.type === 'attributes') {
            if (mutation.target.id === 'progress-output') {
                mutation.target.style.width = mutation.target.attributes['aria-valuenow'].nodeValue + '%';
            }
        } else if (mutation.type === 'childList') {
            if (mutation.addedNodes.length > 0) {
                if (mutation.addedNodes[0].id == 'progress') {
                    mutation.addedNodes[0].childNodes[0].style.width = mutation.addedNodes[0].childNodes[0].attributes['aria-valuenow'].nodeValue + '%';
                }
            }
        }
        console.log(mutation)
    }
};

// Create an observer instance linked to the callback function
const observer = new MutationObserver(callback);

// Start observing the target node for configured mutations
observer.observe(targetNode, config);
