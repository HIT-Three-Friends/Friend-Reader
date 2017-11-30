window.chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)'
};
function init_date() {
    for (var i = 2010; i <= 2017; i++) {
        $("#year").append($("<option></option>").val(i).html(i));
    }
    for (var i = 1; i <= 12; i++) {
        $("#month").append($("<option></option>").val(i).html(i+"月"));
    }
    $("#day").append($("<option></option>").val("0").html("日活跃度分析"));
    $("#day").append($("<option></option>").val("1").html("该月分析"));

    $('#day').on('loaded.bs.select', function (e) {
        var val = $("#day").val();
        console.log(val);
        if (val == "0") {
            $("#month").selectpicker("hide");
            $("#year").selectpicker("hide");
        } else {
            $("#year").selectpicker("show");
            $("#month").selectpicker("show");
        }
    });

    $('#day').on('changed.bs.select', function (e) {
        var val = $("#day").val();
        if (val == "0") {
            $("#month").selectpicker("hide");
            $("#year").selectpicker("hide");
        } else {
            $("#year").selectpicker("show");
            $("#month").selectpicker("show");
        }
    });
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
}
function render_day(data) {
    var xz = new Array();
    for (var i = 0; i < 24; i++)
        xz.push(i.toString());
    var config = {
        type: 'line',
        data: {
            labels: xz,
            datasets: [{
                label: "活跃度",
                backgroundColor: window.chartColors.red,
                borderColor: window.chartColors.red,
                data: data,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: '好友日活跃度分析'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: '时间(小时)'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: '活跃度'
                    }
                }]
            }
        }
    };
    if (window.myLine != null)
        window.myLine.destroy();
    var ctx = document.getElementById("canvas").getContext("2d");
    window.myLine = new Chart(ctx, config);
}
function render_month(data) {

    var xz = new Array();
    for (var i = 1; i <= data.length; i++)
        xz.push(i.toString());
    var config = {
        type: 'line',
        data: {
            labels: xz,
            datasets: [{
                label: "活跃度",
                backgroundColor: window.chartColors.red,
                borderColor: window.chartColors.red,
                data: data,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: '好友月活跃度分析'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: '日'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: '活跃度'
                    }
                }]
            }
        }
    };
    if (window.myLine != null)
        window.myLine.destroy();
    var ctx = document.getElementById("canvas").getContext("2d");
    window.myLine = new Chart(ctx, config);
}
$(function() {
    init_date();
    $("#button-query").click(function(){
        $(".footer").fadeIn();
        if ($("#day").val() == "0") {
            $.ajax({
                url: "/vitality/" + $("#friendid").val() + "/days/",
                type: "GET",
                success: function (data) {
                    $(".footer").fadeOut();
                    render_day(data["vitality"]);
                }
            });
        } else {
            $.ajax({
                url: "/vitality/" + $("#friendid").val() + "/months/",
                type: "GET",
                data: {
                    "year": parseInt($("#year").val()),
                    "month": parseInt($("#month").val())
                },
                success: function(data) {
                    $(".footer").fadeOut();
                    render_month(data["vitality"]);
                }
            });
        }
    });
});