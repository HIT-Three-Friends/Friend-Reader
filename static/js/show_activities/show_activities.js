var last_activity = null;
var current_page = 0;
function add_activity(activity){
    var new_activity = $("#event-template").clone();
    new_activity.css("display", "block");
    $("#timeline").append(new_activity);
}
function add_time(time) {
    var new_time = $("#time-template").clone();
    new_time.css("display", "block");
    new_time.find("#time").html(time);
    $("#timeline").append(new_time);
}
function loadData(){
    var totalheight = parseFloat($(window).height()) + parseFloat($(window).scrollTop());
    console.log("load");
    console.log($(document).height());
    console.log(totalheight);
    if ($(document).height() - 101 <= totalheight) {  // 说明滚动条已达底部
        current_page++;
        console.log("load more");
        $(".footer").css("display", "block");
        $.ajax({
            url: "/activities/",
            type: "GET",
            data: {
                "page": current_page
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
                $(".footer").css("display", "none");
            }
        });
    }
}

$(function() {
    loadData();
    $(window).scroll( function() {
        loadData();
    });
});