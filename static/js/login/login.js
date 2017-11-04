$(function(){
   $("#button-login").click(function(){
       console.log("test");
       var json = getFormJson($("form"));
       console.log(json["username"]);
       $.ajax({
           url: "/users/login/",
           type: "post",
           data : json,
           success : function(data){
               if(data["verdict"] == "success") {
                   window.location.href = "/show/activities";
               } else {
                   alert(data["message"]);
               }
           },
           error : function(data) {
               alert("登录失败，请联系管理员");
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
