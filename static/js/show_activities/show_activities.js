var last_activity = null;
var current_page = 0;
function loadData(){
    var totalheight = parseFloat($(window).height()) + parseFloat($(window).scrollTop());
    if ($(document).height() <= totalheight) {  // 说明滚动条已达底部
        current_page++;
        console.log("load more");
        $.ajax({

        });
    }
}

$(function() {
    loadData();
    $(window).scroll( function() {
        loadData();
    });
});