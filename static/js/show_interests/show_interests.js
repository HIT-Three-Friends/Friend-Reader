window.chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};
function render_bar(data) {
    var labels = new Array();
    var rate = new Array();
    for (var i in data) {
        labels.push(data[i][0]);
        rate.push(data[i][1]);
    }
    var color = Chart.helpers.color;
    var barChartData = {
        labels: labels,
        datasets: [{
            label: '兴趣',
            backgroundColor: color(window.chartColors.red).alpha(0.5).rgbString(),
            borderColor: window.chartColors.red,
            borderWidth: 1,
            data: rate
        }]
    };
    if (window.myBar != null)
        window.myBar.destroy();
    var ctx = document.getElementById("canvas").getContext("2d");
    window.myBar = new Chart(ctx, {
                type: 'bar',
                data: barChartData,
                options: {
                    responsive: true,
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: '好友兴趣分析'
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0
                            }
                        }]
                    }
                }
            });
}
var byear, bmonth, bday, eyear, emonth, eday;
function get_data() {
    var data = {};
    data["byear"] = byear;
    data["bmonth"] = bmonth;
    data["bday"] = bday;
    data["eyear"] = eyear;
    data["emonth"] = emonth;
    data["eday"] = eday;
    return data;
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
    $("#button-query").click(function() {
        $(".footer").fadeIn();
        console.log(get_data());
        $.ajax({
            url: "/interest/" + $("#friendid").val() + "/",
            type: "GET",
            data: get_data(),
            success: function(data) {
                $(".footer").fadeOut();
                var data = data["ans"];
                render_bar(data);
            }
        })
    });
}
function init_range_picker() {
    var start = moment().subtract(29, 'days');
    var end = moment();

    function cb(start, end) {
        $('#range-picker span').html(start.format('YYYY/MM/DD') + ' - ' + end.format('YYYY/MM/DD'));
        start = start._d;
        end = end._d;
        byear = start.getFullYear();
        bmonth = start.getMonth()+1;
        bday = start.getDate();
        eyear = end.getFullYear();
        emonth = end.getMonth()+1;
        eday = end.getDate();
    }
    $('#range-picker')
        .daterangepicker(
            {
                "showDropdowns" : true,
                "locale" : {
                    "format": "YYYY/MM/DD",
                    applyLabel : '确认',
                    cancelLabel : '取消',
                    fromLabel : '从',
                    toLabel : '到',
                    weekLabel : 'W',
                    customRangeLabel : '自定义时间',
                    daysOfWeek : [ "日", "一", "二", "三", "四", "五", "六" ],
                    monthNames : [ "一月", "二月", "三月", "四月", "五月", "六月",
                            "七月", "八月", "九月", "十月", "十一月", "十二月" ],
                },
                "startDate" : start,
                "endDate" : end,
                ranges: {
                   '今天': [moment(), moment()],
                   '昨天': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                   '前7天': [moment().subtract(6, 'days'), moment()],
                   '前30天': [moment().subtract(29, 'days'), moment()],
                   '这个月': [moment().startOf('month'), moment().endOf('month')],
                   '上个月': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
                }
            },
            cb
        );
    cb(start, end);
}
$(function() {
    init();
    init_range_picker();
});