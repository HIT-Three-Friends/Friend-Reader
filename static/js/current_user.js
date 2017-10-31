$(function() {
    $.ajax({
        url: "/users",
        type: "GET",
        success: function(data){
            $("#username").html(data["username"]);
            $("#email").html(data["email"]);
        }
    });
    $("#button-logout").click(function(){
       $.ajax({
           url: "/users/logout",
           type: "GET",
           success: function() {
               window.location.href = "/login/";
           },
           error: function() {
               alert("注销失败");
           }
       });
    });
});