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
        if (this.tagName.toLowerCase() == "select") {
            $(this).children().each(function() {
                if ($(this).val() == data[this.name]) {
                    $(this).attr("selected","selected");
                }
            });
        } else if(this.tagName.toLowerCase() == "input") {
            $(this).val(data[this.name]);
        }
    });
}
function add_friend(new_friend, friend) {
    new_friend.css("display", "block");
    new_friend.find("#avatar").attr("src",friend["avatar"]);
    //new_friend.find("#avatar").attr("src", "/media/upload/233.png");
    new_friend.find("#avatar").attr("data-friendid", friend["friendid"]);
    new_friend.find("#name").html(friend["name"]);
    new_friend.find("#name").attr("href", "/show/activities/"+friend["friendid"]+"/");
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
                        location.reload();
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
    var baseurl = new Array("//zhihu.com/people/", "//weibo.com/", "//github.com/");
    var social = friend["social"];
    for (var j = 0; j < social.length; j++) {
        if (social[j]["account"] != "") {
            new_friend.find("#id"+j).html(social[j]["account"]);
            new_friend.find("#url"+j).attr("href", baseurl[j] + social[j]["account"]);
            new_friend.find("#button-modify").attr("data-account"+j, social[j]["account"]);
        }
    }
    new_friend.find("#vitality").html(randomNum(10, 50));
    $("#body").append(new_friend);
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
        console.log(parseInt(modal.find("#sex").val()));
        if (friendid == "") { // new
            $.ajax({
                url: "/friends/",
                type: "POST",
                data: {
                    "name" : modal.find("#name").val(),
                    "sex" : parseInt(modal.find("#sex").val())
                },
                success: function(data) {
                    var friendid = data["id"];
                    var cnt = 0;
                    $("#cover").fadeIn();
                    $("#loading-img").fadeIn();
                    for (var i = 0; i < 3; i++) {
                        $.ajax({
                            url: "/friends/" + friendid + "/socials/" + i + "/",
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
                type: "POST",
                data: {
                    "name" : modal.find("#name").val(),
                    "sex" : parseInt(modal.find("#sex").val())
                },
                success: function(data) {
                    var friendid = modal.find("#friendid").val();
                    var cnt = 0;
                    $("#cover").fadeIn();
                    $("#loading-img").fadeIn();
                    console.log("OK");
                    for (var i = 0; i < 3; i++) {
                        $.ajax({
                            url: "/friends/" + friendid + "/socials/" + i + "/",
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


    $('#avatar-modal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); // Button that triggered the modal
        var friendid = button.data("friendid");
        var modal = $("#avatar-modal");
        modal.find("#friendid").val(friendid);
        modal.find("#avatar").val("");
        console.log(friendid);

    });
    $("#button-avatar").click(function() {
        var file = $("#avatar-modal #avatar").val();
        console.log(file);
        if (file == "") {
            alert("请选择文件！");
        } else {
            var iframe = document.getElementById("hidden-frame");
            var iwindow = iframe.contentWindow;
            var idoc = iwindow.document;
            $(idoc.body).empty();
            $(idoc.body).append($("#hidden-form").clone());
            var form =  $(idoc.body).find("#hidden-form");
            form.find("#avatar").remove();
            form.append($("#avatar-modal #avatar").clone());
            form.attr("action", "/friends/" + $("#avatar-modal #friendid").val() + "/");
            console.log(form.attr("action"));
            $("#hidden-frame").load(function() {
               location.reload();
            });
            form[0].submit();
            //location.reload();
        }
    });
});