var last_activity = null;
var current_page = 0;
var loading = false;
function add_activity(activity){
    var new_activity = $("#event-template").clone();
    new_activity.attr("class", new_activity.attr("class")+" event");
    new_activity.css("display", "block");
    new_activity.find("#avatar").attr("src", activity["avatar"]);
    new_activity.find("#event-time").html(activity["time"]);
    new_activity.find("#title").html(activity["title"]);
    new_activity.find("#name").html(activity["name"]);
    new_activity.find("#name").attr("href", "/show/activities/"+activity["friendid"]+"/");
    new_activity.find("#url").attr("href", activity["url"]);
    new_activity.find("#word").html(activity["word"]);
    if (activity["weibo_id"] != -1) {
        new_activity.find("#comment").css("display", "");
        new_activity.find("#comment").click(function() {
            $.ajax({
                url: "/token/",
                type: "GET",
                success: function(data) {
                    if (data["verdict"] == "error") {
                        window.open('https://api.weibo.com/oauth2/authorize?client_id=610259729&response_type=code&redirect_uri=http://127.0.0.1:8000/code/','_blank','width=300,height=200,menubar=no,toolbar=no, status=no,scrollbars=yes');
                    } else {
                        $("#comment-modal").find("#comment").val("");
                        $("#comment-modal").find("#weibo_id").val(activity["weibo_id"]);
                        $('#comment-modal').modal('show');
                    }
                }
            })
        })
    }
    new_activity.find("#word").click(function(e) {
        new_activity.find("#word").css("max-height", "");
        new_activity.find("#word").css("cursor", "");
        new_activity.find("#word").css("color", "");
        $(document).one("click", function () {
            new_activity.find("#word").css("max-height", "200px");
            new_activity.find("#word").css("cursor", "pointer");
        });
        e.stopPropagation();
    });
    new_activity.find("#word").mouseover(function(e) {
        if ($(this).css("max-height") == "200px")
            new_activity.find("#word").css("color", "#989ba2");
        $(document).one("mouseover", function () {
            new_activity.find("#word").css("color", "");
        });
        e.stopPropagation();
    });
    $("#timeline").append(new_activity);
}
function add_time(time) {
    var new_time = $("#time-template").clone();
    new_time.attr("class", new_time.attr("class") + " time-milestone");
    new_time.css("display", "block");
    new_time.find("#time").html(time);
    $("#timeline").append(new_time);
}
function loadData(){
    var totalheight = parseFloat($(window).height()) + parseFloat($(window).scrollTop());
    console.log("load");
    console.log($(document).height());
    console.log(totalheight);
    if ($(document).height() - 101 <= totalheight && loading == false) {  // 说明滚动条已达底部
        console.log("loading="+loading);
        loading = true;
        current_page++;
        console.log("load more");
        $(".footer").fadeIn();
        console.log(location.pathname.replace("/show",""));
        $.ajax({
            url: location.pathname.replace("/show", ""),
            type: "GET",
            data: {
                "page": current_page,
                "platform": $("#platform").val()
            },
            success: function(data) {
                var activities = data["activity"];
                for (var i in activities) {
                    var activity = activities[i];
                    if (last_activity == null || activity["date"] != last_activity["date"]) {
                        add_time(activity["date"]);
                    }
                    last_activity = activity;
                    add_activity(activity);
                }
                $(".footer").fadeOut();
                loading = false;
            }
        });
    }
}
function refresh() {
    $(".event").remove();
    $(".time-milestone").remove();
    current_page = 0;
    $(".footer").fadeIn();
    loadData();
}

$(function() {
    $('#platform').on('loaded.bs.select', function (e) {
        refresh();
    });
    $('#platform').on('changed.bs.select', function (e) {
        refresh();
    });
    loadData();
    $(window).scroll( function() {
        loadData();
    });
    $("#button-refresh").click(function() {
        refresh();
    });
    $("#comment-submit").click(function() {
        $.ajax({
            url: "/comment/" + $("#comment-modal").find("#weibo_id").val() + "/",
            type: "POST",
            data: {
                "content": $("#comment-modal").find("#comment").val()
            },
            success: function(data) {
                if (data["verdict"] == "ok") {
                    alert("评论成功!");
                    $("#comment-modal").modal("hide");
                } else {
                    alert(data["message"]);
                }
            },
            error: function() {
                alert("评论失败，请联系管理员");
            }
        });
    });
});