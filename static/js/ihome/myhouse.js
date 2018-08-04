$(document).ready(function(){
    $(".auth-warn").show();

    $.get('/house/house_info/', function (data) {
        // 用户已经实名认证
        if(data.code == '200'){
            // 影藏警告
            $('.auth-warn').hide();
            for(var i=0; i<data.house_list.length; i++){

                var house_li = '';
                house_li += '<li><a href="/house/detail/?house_id=' + data.house_list[i].id + '"><div class="house-title">';
                house_li += '<h3>房屋ID:'+ data.house_list[i].id + '---' + data.house_list[i].title + '</h3></div>';
                house_li += '<div class="house-content">';
                house_li += '<img src="/static/media/' + data.house_list[i].image + '" alt="">';
                house_li += '<div class="house-text"><ul>';
                house_li += '<li>位于：' + data.house_list[i].area + '</li>';
                house_li += '<li>价格：' + data.house_list[i].price + '/晚</li>';
                house_li += '<li>发布时间：' + data.house_list[i].create_time + '</li>';
                house_li += '</ul></div></div></a></li>';

                $('#houses-list').append(house_li)

            }

        }else{
            // 影藏添加房屋的url
            $('#houses-list').hide()
        }
    });

});