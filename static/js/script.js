var show_num = 5;
var fetch_num = 10;

function link_obj(json) {
    var p = $("<div></div>").attr("id", json.id).attr("class", 'btn-group');

    var a = $("<button></button>").attr("type", "button").attr("class", "btn btn-primary link-btn").attr("onclick", "location.href = '"+json.link+"'");
    p.append(a);

    var t = $("<span>").attr("class", "d-inline-block text-truncate").attr("style","max-width: 250px;");
    t.append($("<img>").attr("src", json.favicon).attr("class","link-icon"));
    t.append(' ');
    t.append(json.title);
    a.append(t);

    var x = $("<button></button>").attr("type", "button").attr("class", "btn btn-primary remove-btn").click(function() {remove(json.id);});
    x.append('x');
    p.append(x);

    return p;
}

function error_msg(data) {
    e = $("<div></div>").attr("role", "alert").html(data['message']);

    if(data['status'] == 500)
        e = e.attr("class", "alert alert-dark width-full text-center").html("INTERNAL ERROR");
    else if(data['status'] == 400)
        e = e.attr("class", "alert alert-danger width-full text-center").html("BAD REQUEST");
    else
        return;

    $('#errorbox').append(e);
    setTimeout(function(){e.remove();}, 3000);
}

function fetch(args) {
    $("#things").html('');

    return $.post("/fetch", args, function(data) {
        var n = data.length;
        var i = 0;
        for(i=0;i<n;i++) {
            var o = link_obj(data[n-1-i]);
            $("#things").append(o);

            if(i>=show_num)
                o.hide();
        }
        return data;
    }).fail(function(data){error_msg(data)});
};

function onEnter(t) {
    // triggered when text inside the box is changed
    
    if (t=='') {
        fetch({});  
        return;
    }

    // check if the text is url
    // copy-pasted from 
    // https://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url

    var ex = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
    var regex = new RegExp(ex);
    if (t.match(regex)) {
        $("#box").val('');
        save(t);
        return;
    }


    // check if the text is tag; if so, search by tag

    // if neither, search
    fetch({title: t});
}


function save(t) {
    //send bookmark link to server
    //TODO: add tagging

    var link = t;
    return $.post("/save", {link: link}, function(data) {
        //add data

        $("#things div:nth-child("+show_num+")").hide();
        $("#things").prepend(link_obj(data));
        
        return data;
    }).fail(function(data){error_msg(data)});
};

function remove(id) {
    return $.post("/remove", {id: id}, function(data) {

        $('#'+id).remove();
        $("#things div:nth-child("+show_num+")").show();

        return data;
    }).fail(function(data){error_msg(data)});
}

$(document).ready(function() {
    $("#box").change(function() {
        onEnter($("#box").val());
    });

    fetch({num: fetch_num});
});
