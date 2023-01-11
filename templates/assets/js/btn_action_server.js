//
// Button Actinos for Server Only
//
$('#multiview').gridstrap({
    draggable: false // toggle mouse dragging.
});
$("#drag_btn").change(function() {
    if ($(this).is(':checked')) {
        $('.drag-handle').css('visibility', 'visible');
        $('#multiview').data('gridstrap').updateOptions({
            draggable: true
        });
    } else {
        $('.drag-handle').css('visibility', 'hidden');
        $('#multiview').data('gridstrap').updateOptions({
            draggable: false
        });
    }
});
$("#Z000").hide();
$(".toggle_cam").click(function(){
    cam_id = $(this).attr('cam_id');
    elm_id = "#"+cam_id;
    // console.log(cam_id, "is clicked")
    if ($(this).hasClass("btn_on")){
        $('#multiview').data('gridstrap').detachCell($(elm_id));
        $("[id="+cam_id+"]").remove();
    } else {
        elm_clone = $("#Z000").clone(true).show().prop('id', cam_id);
        elm_clone.find('[cam_id="Z000"]').attr('cam_id', cam_id);
        elm_clone.find('.header_name').text(elm_clone.find('.header_name').text().replace("Z000", cam_id));
        $('#multiview').data('gridstrap').insertCell(elm_clone,0);  
    };
    $(this).toggleClass("btn_on");
});