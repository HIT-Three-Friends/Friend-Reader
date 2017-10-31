$(function(){
    $("#button-register").click(function() {
        var json = getFormJson($("form"));
        $.ajax({
            url: "/users/",
            type: "POST",
            data: json,
            success: function (data) {
                if (data["verdict"] == "success") {
                    alert("注册成功");
                    window.location.href = "/login/";
                } else {
                    alert(data["message"]);
                }
            },
            error: function() {
               alert("注册失败，请联系管理员");
            }
        });
    });
});
function getFormJson(node) {
    var o = {};
    node.find("input,select").each(function(){
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
}
