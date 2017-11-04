$(function() {
    $.ajax({
        url: "/users",
        type: "GET",
        success: function(data){
            if (data["verdict"] == "success") {
                $("#username").html(data["username"]);
                $("#name").html(data["username"]);
                $("#email").html(data["email"]);
            } else {
                alert(data["message"]);
                window.location.href = "/login/";
            }
        },
        error: function() {
            window.location.href = "/login/";
        }
    });
    $("#button-logout").click(function(){
       $.ajax({
           url: "/users/logout",
           type: "GET",
           success: function(data) {
               window.location.href = "/login/";
           },
           error: function() {
               alert("注销失败");
           }
       });
    });
});