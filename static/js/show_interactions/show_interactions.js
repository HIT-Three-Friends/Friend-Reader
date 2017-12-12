function show_graph() {
    var i,
        s,
        N = 100,
        E = 500,
        g = {
          nodes: [],
          edges: []
        };
    // Generate a random graph:
    for (i = 0; i < N; i++)
      g.nodes.push({
        id: 'n' + i,
        label: 'Node \n' + i,
        x: Math.random(),
        y: Math.random(),
        size: Math.random(),
        color: '#666'
      });
    for (i = 0; i < E; i++)
      g.edges.push({
        id: 'e' + i,
        source: 'n' + (Math.random() * N | 0),
        target: 'n' + (Math.random() * N | 0),
        size: Math.random(),
        color: '#ccc'
      });
    // Instantiate sigma:
    s = new sigma({
      graph: g,
      container: 'graph-container'
    });
}
var table = null;
function show_table(data2) {
    console.log(data2);
    if (table != null)
        table.destroy();
    table = $("#table").DataTable({
        data: data2,
        columns: [
            { data: 'Name' },
            { data: 'InteractionNum' },
            { data: 'Tag1' },
            { data: 'Num1' },
            { data: 'Tag2' },
            { data: 'Num2' },
            { data: 'Tag3' },
            { data: 'Num3' },
            { data: 'NumN' }
        ],
        language : {
            'emptyTable' : '没有数据',
            'loadingRecords' : '加载中...',
            'processing' : '查询中...',
            'search' : '搜索:',
            'lengthMenu' : '每页 _MENU_ 项',
            'zeroRecords' : '没有数据',
            'paginate' : {
                'first' : '第一页',
                'last' : '最后一页',
                'next' : '下一页',
                'previous' : '上一页'
            },
            'info' : '第 _PAGE_ 页 / 总 _PAGES_ 页',
            'infoEmpty' : '没有数据',
            'infoFiltered' : '(过滤总件数 _MAX_ 条)'
        }
    });
}
function init() {
    $.ajax({
        url: "/friends/",
        type: "GET",
        success: function(data) {
            var friends = data["friends"];
            for (var i = 0; i < friends.length; i++) {
                var friend = friends[i];
                console.log(friend["friendid"]);
                $("#friendid").append($("<option></option>").val(friend["friendid"]).html(friend["name"]));
            }
            $("#friendid").selectpicker("refresh");
        }
    });

    $('#friendid').on('loaded.bs.select', function (e) {
        $(".footer").fadeIn();
        $.ajax({
            url: "/interaction/"+$("#friendid").val()+"/",
            type: "GET",
            success: function(data) {
                $(".footer").fadeOut();
                data = data["interactions"];
                show_table(data);
            }
        });
    });
    $('#friendid').on('changed.bs.select', function (e) {
        $(".footer").fadeIn();
       $.ajax({
            url: "/interaction/"+$("#friendid").val()+"/",
            type: "GET",
            success: function(data) {
                $(".footer").fadeOut();
                data = data["interactions"];
                show_table(data);
            }
       });
    });
}
$(function() {
    init();
});