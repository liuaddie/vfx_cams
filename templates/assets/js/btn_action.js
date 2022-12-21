var dir = 1;
$('#cam_btn_rotate').click(function(){
    cam_container = $(this).closest('.cam-container')
    if(dir){
        cam_container.find('.cam_feed_img').attr('src', 'cam_sample.jpg');
        cam_container.removeClass('cam-horizontal');
        cam_container.addClass('cam-vertical');
        dir = 0;
    } else{
        cam_container.find('.cam_feed_img').attr('src', 'cam_sample_H.jpg');
        cam_container.removeClass('cam-vertical');
        cam_container.addClass('cam-horizontal');
        dir = 1;
    }
    
})