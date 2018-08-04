function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

// ready()待执行的回调函数
$(document).ready(function () {
    // 通过id获取表单提交执行的方法
    $('#form-auth').submit(function () {
        real_name = $('#real-name').val();
        id_card = $('#id-card').val();
        // 原生ajax, 不支持文件上传
        $.ajax({
            url: '/user/auth/',
            data: {'real_name': real_name, 'id_card': id_card},
            dataType: 'json',
            type: 'PATCH',
            success:function (data) {
                auth();
            },
            error:function (data) {
                alert('请求失败')
            }
        });
    });

function auth() {
    // 获取用户信息
    $.get('/user/read_user_info/', function (data) {
        if(data.code == '200'){
            // 展示实名认证信息
            $('#real-name').val(data.user.id_name);
            $('#id-card').val(data.user.id_card);
            if(data.user.id_name){
                // 影藏保存按钮
                // $('#real-name').attr('readonly',true)
                $('.btn-success').hide()
            }
        }
    });
}
auth();
});



