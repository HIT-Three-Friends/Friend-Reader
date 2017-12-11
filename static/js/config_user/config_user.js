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
function add_attention(new_attention, attention) {
    new_attention.css("display", "block");
    new_attention.find("#name").html(attention["tag"]);
    console.log("before:"  + " " + attention["id"]);
    new_attention.find("#button-delete").click(function(){
        if (confirm("确认删除该话题？QAQ")) {
            $.ajax({
                url: "/attentions/" + attention["id"] + "/",
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
    $("#body").append(new_attention);
}
$(function() {

    $.ajax({
        url: "/attentions/",
        type: "GET",
        success: function(data) {
            var attentions = data["tags"];
            for (var i in attentions) {
                var attention = attentions[i];
                var new_attention = $("#attention-template").clone();
                add_attention(new_attention, attention);
            }
        }
    });

    $("#button-attention").click(function() {
        var modal = $("#attention-modal");
        $.ajax({
            url: "/attentions/",
            type: "POST",
            data: {
                "tag" : modal.find("#tag").val()
            },
            success: function(data) {
                location.reload();
            }
        });
    });

    $('#friend-modal').on('show.bs.modal', function (event) {
        $("#friend-modal #tag").val("");
    });
});