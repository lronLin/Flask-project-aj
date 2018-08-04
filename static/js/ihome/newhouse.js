function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $.get('/house/area_facility/', function (data) {
        if(data.code == '200'){
            for(var i=0; i<data.areas.length; i++){
                area_str = '<option value="' + data.areas[i].id + '">' + data.areas[i].name + '</option>';
                $('#area-id').append(area_str)
                // $('#area-id').append($('<option>').val(data.areas[i].id).text(data.area[i].name));
            }

            // 动态加载设备信息 - 动态刷新页面
            for(var j=0; j<data.facilitys.length; j++){
                facility_str = '<li><div class="checkbox"><label>';
                facility_str += '<input type="checkbox" name="facility" value="'+ data.facilitys[j].id + '">'+ data.facilitys[j].name;
                facility_str += '</lable></div></li>';

                $('.house-facility-list').append(facility_str)
                // $('.house-facility-list').append($('<li>').class('checkbox').append($('<lable>').add($('<input>').attr({'type':'checkbox','name':'facility','value':1}))))

            }
        }
    });

    // form提交表单 - 发布新房源
    $('#form-house-info').submit(function (e) {
        e.preventDefault();
        // 全部提交表单 - 房屋标题等
        $(this).ajaxSubmit({
            url:'/house/newhouse/',
            type: 'POST',
            dataType: 'json',
            success:function(data){
                if(data.code == '200'){
                    $('#form-house-image').show();
                    $('#form-house-info').hide();
                    // 添加房屋信息
                    $('#house-id').val(data.house_id)
                }
            },
            error:function(data){
                alert('请求失败')
            }
        });
    });

    // 创建房屋图片信息
    $('#form-house-image').submit(function (e) {
        e.preventDefault();
        $(this).ajaxSubmit({
            url: '/house/house_images/',
            dataType: 'json',
            type: 'POST',
            success: function (data) {
                if(data.code == '200'){
                    var img_src = '<img src="/static/media/' + data.image_url + '">';
                    $('.house-image-cons').append(img_src)
                }
            },
            error: function (data) {
                alert('请求失败')
            }

        });
    });

});