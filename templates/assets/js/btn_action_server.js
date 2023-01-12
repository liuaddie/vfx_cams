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

// Additional Function for All Camera Action Buttons before and after
function all_cam_action_before(element){
    // console.log('before: ' + element.attr('cam_id'));
    // cam_container = element.closest('.cam-container');
    // console.log('id: ' + cam_container.attr('id'));
    // cam_container_id = cam_container.attr('id');
    // cam_container_selector = "[id="+cam_container_id+"]";// find cam_container outside the gridstrap
    // console.log(cam_container_selector);
    $('.cam_btn_focus.btn_on').removeClass("btn_on");
    $('.cam_feed_img.img_on').removeClass("img_on");
    // cancelFocus(cam_container);
    
    // Lock
    if (element.attr('action') == 'actHalfPressShutter'){
        console.log('before all:' + element.attr('action'));
        $('.cam_action[action="actHalfPressShutter"]').toggleClass("btn_on");
        element.toggleClass("btn_on");
        $('.cam_action, .all_cam_action').not('.dont_lock').prop('disabled', (i, v) => !v);
        $('.cam_btn_focus').prop('disabled', (i, v) => !v);
        $('.cam_setting, .all_cam_setting').prop('disabled', (i, v) => !v);
    };
    
};

// Function for All Camera Action Buttons
// Share function with all_cam_action buttons and all_cam_setting dropdowns
function all_cam_action(element){
    // cam_id = element.attr('cam_id');
    action = element.attr('action');
    if (element.hasClass('all_cam_setting')){
        param = element.val();
    } else {
        param = element.attr('param') !== undefined ? element.attr('param') : '';
    };
    all_cam_action_before(element);
    console.log("All Cam: ", action, param);
    // data = {'cam_id':cam_id, 'action':action, 'param':param};
    // $.ajax({
    //     type : 'POST',
    //     url : '/cam_control',
    //     contentType: 'application/json;charset=UTF-8',
    //     data : JSON.stringify(data)
    // });
};


$('.all_cam_action').click(function(){all_cam_action($(this));});
$('.all_cam_setting').change(function(){all_cam_action($(this));});