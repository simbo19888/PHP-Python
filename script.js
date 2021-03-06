(function() {
    var blob, domain, ref, ref1, ref2, upload_id, url;
    url = window.location !== window.parent.location ? location.ancestorOrigins != null ? location.ancestorOrigins[0] : document.referrer : document.location.href;
    domain = url != null ? (ref = url.match(/\/\/([^\/]+)/)) != null ? ref[1] : void 0 : void 0;
    if (navigator.sendBeacon == null) {
        return
    }
    blob = new FormData;
    blob.append("domain", domain || "unknown-domain");
    if (upload_id = (ref1 = window.location.href) != null ? (ref2 = ref1.match(/\/html\/(\d+)/)) != null ? ref2[1] : void 0 : void 0) {
        blob.append("upload_id", upload_id)
    }
    navigator.sendBeacon("https://itch.io/html-callback", blob)
}).call(this);