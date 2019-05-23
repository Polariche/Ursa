var box;
var things;

function link_html(json) {
    //TODO: DOM 스타일로 바꾸기
    
    return "<p id="+json.id+"> <a class='link' href="+ json.link + ">" + json.title + "</a> x </p>";
}

function fetch() {
    things.html('');
    $.post("/fetch", {}, function(data) {
        var n = data.length;
        var i = 0;
        for(i=n-1;i>=0;i--) {
            //latest link first
            things.append(link_html(data[i]));
        }
    });
};

function onEnter(t) {
    // triggered when text inside the box is changed

    // check if the text is url
    // copy-pasted from 
    // https://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url
    var ex = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
    var regex = new RegExp(ex);
    if (t.match(regex)) {
        box.val('');
        save(t);
        return;
    }

    // check if the text is tag; if so, search by tag

    // if neither, search

    $('#things').html(t);
}

function search_title(t) {
    
}

function search_tag(t) {

}

function render(indices) {
    //render stuff
}

function save(t) {
    //send bookmark link to server
    //TODO: add tagging

    var link = t;
    $.post("/save", {link: link}, function(data) {
        //add data

        things.html(link_html(data)+things.html());
    });
};

function remove(id) {
    $.post("/remove", {id: id}, function(data) {
        $('#'+id).hide();
    });
}

$(document).ready(function() {
    box = $("#box");
    things = $("#things");

    box.change(function() {
        onEnter(box.val());
    });

    fetch();
});
