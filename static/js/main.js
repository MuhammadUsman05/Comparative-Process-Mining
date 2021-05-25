$(document).ready(function() {

$("#menu-toggle").click(function() {
        $("#wrapper").toggleClass("toggled");
    });


    function handler1() {

    $("#microwrapper").addClass("microtoggled");
    $(".items2").fadeIn(3000);

    $(this).one("click", handler2);
    }
    function handler2() {


    $(".items2").hide();
    $("#microwrapper").removeClass("microtoggled");
        $(this).one("click", handler1);
    }
    $("#project").one("click", handler1);


});