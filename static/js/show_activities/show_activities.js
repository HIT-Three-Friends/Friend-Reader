function loadData(){
    var totalheight = parseFloat($(window).height()) + parseFloat($(window).scrollTop());
    if ($(document).height() <= totalheight) {  // 说明滚动条已达底部
        console.log("load more");
        /*这里使用Ajax加载更多内容*/
        var container = $("#container"); // 加载容器
        var data = {}; // 查询参数
        // 当前页
        var currentPage = parseInt(container.find('#currentPage').val());
        // 总页数
        var maxPage = parseInt(container.find('#maxPage').val());
        // 查询日期范围
        var startDate = container.find('#startDate').val();
        var endDate = container.find('#endDate').val();
        data.currentPage = currentPage;
        data.maxPage = maxPage;
        data.startDate =startDate;
        data.endDate = endDate;
        jQuery.ajax({
            type:"POST",
            url: "/servlet/query.do",
            data:data,
            dataType: "json",
            beforeSend: function(XMLHttpRequest){
                $("#loading").css('display','');
            }, success:function(response) {
                if(response.data){
                    for(var i=0, length = response.data.length; i<length; i++){
                        var html = response.data[i];
                        var test = $(html);
                        container.append(test);
                    }
                    container.find('#currentPage').val(parseInt(currentPage)+1);
                    $("#loading").css('display','none');
                }
            }, error:function(){
                alert("加载失败");
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