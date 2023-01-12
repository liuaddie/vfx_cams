//
// Button Actinos for both Controller & Server
//

// Initizal Variables
var res = $("#cam_set_res").val();
var img_w = 0;
var img_h = 0;
var rot = 0; // rot flag will not be work in server, pending

// Hide the handle at the beginning
$('.drag-handle').css('visibility', 'hidden');

// Function for Change Resolution
function changeResolution(res){
    // sm = 200x300, md = 300x450, lg = 400x600
    switch (res) {
        case 'md':
            img_w = 450;
            img_h = 300;
        break;
        case 'sm':
            img_w = 300;
            img_h = 200;
        break;
        case 'lg':
            img_w = 600;
            img_h = 400;
        break;
    };
    console.log(res, img_w, img_h);
}
changeResolution(res);

// Function for Change Orientation
function changeOrientation() {
    img_temp = img_w;
    img_w = img_h;
    img_h = img_temp;
    console.log(img_w+'x'+img_h);
}

// Deactive cam_btn_focus if other button is clicked
function cancelFocus(cam_container) {
    cam_container.find(".cam_btn_focus").removeClass("btn_on");
    cam_container.find(".cam_feed_img").removeClass("img_on");
}

// Change Resolution
$('select[id="cam_set_res"]').change(function(){
    all_cam_container = $('.cam-container');
    res_old = "cam-"+res;
    if ($(this).val() != res){
        res = $(this).val();
        res_new = "cam-"+res;
        all_cam_container.removeClass(res_old);
        all_cam_container.addClass(res_new);
        console.log(res_new);
        changeResolution(res);
    };
});

// Disable dragging the images
$('img').on('dragstart', function(event) { event.preventDefault(); });

// Additional Function for Camera Action Buttons before and after
function cam_action_before(element){
    console.log('before: ' + element.attr('cam_id'));
    cam_container = element.closest('.cam-container');
    console.log('id: ' + cam_container.attr('id'));
    cam_container_id = cam_container.attr('id');
    cam_container_selector = "[id="+cam_container_id+"]";// find cam_container outside the gridstrap
    console.log(cam_container_selector);
    cancelFocus(cam_container);
    
    // Rotate the camera view
    if (element.attr('action') == 'rotate'){
        console.log('before:' + element.attr('action'));
        img_elm = $(cam_container_selector).find('.cam_feed_img');
        rot = (rot+1) % 4;
        if(rot % 2 == 1){
            sample_img = 'cam_sample.jpg';
            $(cam_container_selector).removeClass('cam-horizontal');
            $(cam_container_selector).addClass('cam-vertical');
            changeOrientation();
        } else{
            sample_img = 'cam_sample_H.jpg';
            $(cam_container_selector).removeClass('cam-vertical');
            $(cam_container_selector).addClass('cam-horizontal');
            changeOrientation();
        };
        if (img_elm.attr("src").toLowerCase().indexOf(".jpg") >= 0){
            img_elm.attr('src', sample_img);
        };
    };
    
    // Lock
    if (element.attr('action') == 'actHalfPressShutter'){
        console.log('before:' + element.attr('action'));
        element.toggleClass("btn_on");
        cam_container.find('.cam_action').not('.dont_lock').prop('disabled', (i, v) => !v);
        cam_container.find('.cam_btn_focus').prop('disabled', (i, v) => !v);
        cam_container.find('.cam_setting').prop('disabled', (i, v) => !v);
    };
    
};

// Function for Camera Action Buttons
// Share function with cam_action buttons and cam_setting dropdowns
function cam_action(element){
    cam_id = element.attr('cam_id');
    action = element.attr('action');
    if (element.hasClass('cam_setting')){
        param = element.val();
    } else {
        param = element.attr('param') !== undefined ? element.attr('param') : '';
    };
    cam_action_before(element);
    console.log(cam_id, action, param);
    data = {'cam_id':cam_id, 'action':action, 'param':param};
    $.ajax({
        type : 'POST',
        url : '/cam_control',
        contentType: 'application/json;charset=UTF-8',
        data : JSON.stringify(data)
    });
};


$('.cam_action').click(function(){cam_action($(this));});
$('.cam_setting').change(function(){cam_action($(this));});

// Toogle Focus Button
$('.cam_btn_focus').click(function(){
    $(this).toggleClass("btn_on");
    cam_container = $(this).closest('.cam-container')
    img_elm = cam_container.find('.cam_feed_img');
    img_elm.toggleClass("img_on");
});

// POST touchAF
$(".cam_feed_img").click(function(event){
    if ($(this).hasClass("img_on")){
        var touchAF = {x: event.pageX - $(this).offset().left, y: event.pageY - $(this).offset().top};
        
        touchAF.x = Math.round(touchAF.x/img_w*100);
        touchAF.y = Math.round(touchAF.y/img_h*100);
        
        touchAF.x = touchAF.x<=0 ? 1 : touchAF.x>100 ? 100 : touchAF.x;
        touchAF.y = touchAF.y<=0 ? 1 : touchAF.y>100 ? 100 : touchAF.y;
        console.log(touchAF);
        
        switch(rot){
            case 1:
                temp = touchAF.y;
                touchAF.y = 100-touchAF.x;
                touchAF.x = temp;
            break
            case 2:
                touchAF.y = 100-touchAF.y;
                touchAF.x = 100-touchAF.x;
            break
            case 3:
                temp = touchAF.x;
                touchAF.y = temp;
                touchAF.x = 100-touchAF.y;
            break
        } 
        
        
        data = {'cam_id': '', 'action': 'setTouchAFPosition', 'param':touchAF.x+","+touchAF.y};
        $.ajax({
            type : 'POST',
            url : '/cam_control',
            contentType: 'application/json;charset=UTF-8',
            data : JSON.stringify(data),
            context: this
        }).always(cancelFocus($(this).closest('.cam-container')));
    };
});
