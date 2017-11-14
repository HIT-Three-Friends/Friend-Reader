function randomNum(minNum,maxNum){
    switch(arguments.length){
        case 1:
            return parseInt(Math.random()*minNum+1,10);
        break;
        case 2:
            return parseInt(Math.random()*(maxNum-minNum+1)+minNum,10);
        break;
            default:
                return 0;
            break;
    }
}
function putFormJson(node, data) {
    node.find("input,select").each(function() {
        console.log(this.tagName + " " + this.name);
        if (this.tagName.toLowerCase() == "select") {
            $(this).children().each(function() {
                if ($(this).val() == data[this.name]) {
                    $(this).attr("selected","selected");
                }
            });
        } else if(this.tagName.toLowerCase() == "input") {
            console.log(data[this.name] + " " + this.name);
            $(this).val(data[this.name]);
        }
    });
}
function add_friend(new_friend, friend) {
    new_friend.css("display", "block");
    new_friend.find("#avatar").attr("src","/media/"+friend["avatar"]);
    new_friend.find("#name").html(friend["name"]);
    if (friend["sex"] == 0) {
        new_friend.find("#sex").attr("src", "/static/images/male.png");
    } else {
        new_friend.find("#sex").attr("src", "/static/images/female.png");
    }
    console.log("before:"  + " " + friend["friendid"]);
    new_friend.find("#button-modify").attr("data-friendid", friend["friendid"]);
    new_friend.find("#button-modify").attr("data-name", friend["name"]);
    new_friend.find("#button-modify").attr("data-sex", friend["sex"]);
    new_friend.find("#button-delete").click(function(){
        if (confirm("确认删除该朋友？QAQ")) {
            $.ajax({
                url: "/friends/" + friend["friendid"] + "/",
                type: "DELETE",
                success: function(data) {
                    if (data["verdict"] == "success") {
                        alert("删除成功");
                    } else {
                        alert(data["message"]);
                    }
                },
                error: function(data) {
                    alert("删除失败，请联系管理员");
                }
            });
        }
    });
    $.ajax({
        url: "/socials/" + friend["friendid"] + "/",
        type: "GET",
        success: function(data) {
            console.log(friend["friendid"]);
            var baseurl = new Array("//zhihu.com/people/", "//weibo.com/", "//github.com/");
            for (var j = 0; j < data["socials"].length; j++) {
                if (data["socials"][j]["account"] != "") {
                    new_friend.find("#id"+j).html(data["socials"][j]["account"]);
                    new_friend.find("#url"+j).attr("href", baseurl[j] + data["socials"][j]["account"]);
                    new_friend.find("#button-modify").attr("data-account"+j, data["socials"][j]["account"]);
                }
            }
            new_friend.find("#vitality").html(randomNum(10, 50));
            $("#body").append(new_friend);
        }
    });
}
$(function() {
    $.ajax({
        url: "/friends/",
        type: "GET",
        success: function(data) {
            var friends = data["friends"];
            for (var i in friends) {
                var friend = friends[i];
                var new_friend = $("#friend-template").clone();
                add_friend(new_friend, friend);
            }
        }
    });
    $('#friend-modal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var recipient = button.data('whatever'); // Extract info from data-* attributes
        var data = new Array();
        data["friendid"] = button.data("friendid");
        data["name"] = button.data("name");
        data["sex"] = button.data("sex");
        data["account0"] = button.data("account0");
        data["account1"] = button.data("account1");
        data["account2"] = button.data("account2");
        console.log(data);
        var modal = $(this);
        putFormJson(modal, data);
    });
    $("#button-friend").click(function() {
        var friendid = $("#friend-modal #friendid").val();
        var modal = $("#friend-modal");
        if (friendid == "") { // new
            $.ajax({
                url: "/friends/",
                type: "POST",
                data: {
                    "name" : modal.find("#name").val(),
                    "sex" : parseInt(modal.find("id").val())
                },
                success: function(data) {
                    var friendid = data["id"];
                    var cnt = 0;
                    for (var i = 0; i < 3; i++) {
                        $.ajax({
                            url: "/friends/" + friendid + "/social/",
                            type: "POST",
                            data: {
                                "platform": i,
                                "account": modal.find("#account"+i).val()
                            },
                            success: function () {
                                cnt++;
                                if (cnt == 3) {
                                    alert("新建好友成功");
                                    location.reload();
                                }
                            }
                        });
                    }
                }
            });
        } else { // modify
            $.ajax({
                url: "/friends/" + friendid + "/",
                type: "PUT",
                data: {
                    "name" : modal.find("#name").val(),
                    "sex" : parseInt(modal.find("id").val())
                },
                success: function(data) {
                    var friendid = data["id"];
                    var cnt = 0;
                    for (var i = 0; i < 3; i++) {
                        $.ajax({
                            url: "/friends/" + friendid + "/social/",
                            type: "POST",
                            data: {
                                "platform": i,
                                "account": modal.find("#account"+i).val()
                            },
                            success: function () {
                                cnt++;
                                if (cnt == 3) {
                                    alert("修改好友成功");
                                    location.reload();
                                }
                            }
                        });
                    }
                }
            });
        }
    });
});