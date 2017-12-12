window.chartColors = ['rgb(255, 99, 132)',
    'rgb(255, 159, 64)',
    'rgb(75, 192, 192)',
    'rgb(255, 205, 86)',
    'rgb(54, 162, 235)',
    'rgb(201, 203, 207)',
    'rgb(153, 102, 255)'];
function render_year(data) {
    console.log(data);
    var xz = new Array();
    for (var i = 0; i < 12; i++)
        xz.push((i+1).toString());
    var set = new Array();
    for (var i = 0; i < data["num"]; i++) {
        var new_set = new Array();
        new_set.label = data["topic"][i];
        new_set.backgroundColor = window.chartColors[i];
        new_set.borderColor = window.chartColors[i];
        new_set.data = data["percent"+(i+1)];
        new_set.fill = false;
        set.push(new_set);
    }
    var config = {
        type: 'line',
        data: {
            labels: xz,
            datasets: set
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: '好友兴趣随时间变化分析'
            },
            tooltips: {
                mode: 'index',
                intersect: false
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
    for (var i = 1; i <= data["day"]; i++)
        xz.push(i.toString());
    var set = new Array();
    for (var i = 0; i < data["num"]; i++) {
        var new_set = new Array();
        new_set.label = data["topic"][i];
        new_set.backgroundColor = window.chartColors[i];
        new_set.borderColor = window.chartColors[i];
        new_set.data = data["percent"+(i+1)];
        new_set.fill = false;
        set.push(new_set);
    }
    var config = {
        type: 'line',
        data: {
            labels: xz,
            datasets: set
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: '好友兴趣随时间变化分析'
            },
            tooltips: {
                mode: 'index',
                intersect: false
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

    for (var i = 2010; i <= 2017; i++) {
        $("#year").append($("<option></option>").val(i).html(i));
    }
    for (var i = 1; i <= 12; i++) {
        $("#month").append($("<option></option>").val(i).html(i+"月"));
    }

    $('#query-type').on('loaded.bs.select', function (e) {
        var val = $("#query-type").val();
        if (val == "year") {
            $("#month").selectpicker("hide");
            $("#year").selectpicker("show");
        } else {
            $("#year").selectpicker("show");
            $("#month").selectpicker("show");
        }
    });
    $('#query-type').on('changed.bs.select', function (e) {
        var val = $("#query-type").val();
        if (val == "year") {
            $("#month").selectpicker("hide");
            $("#year").selectpicker("show");
        } else {
            $("#year").selectpicker("show");
            $("#month").selectpicker("show");
        }
    });
    $("#button-query").click(function() {
        $(".footer").fadeIn();
        $.ajax({
            url: "/interest/" + $("#friendid").val() + "/" + $("#query-type").val() + "s/",
            type: "GET",
            data: {
                "year": $("#year").val(),
                "month": $("#month").val()
            },
            success: function(data) {
                $(".footer").fadeOut();
                if ($("#query-type").val() == "year") {
                    render_year(data);
                } else {
                    render_month(data);
                }
            }
        })
    });
}
$(function() {
    init();
});