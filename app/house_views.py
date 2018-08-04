
import os

from flask import Blueprint, render_template, jsonify, session, request

from app.models import User, Area, House, Facility, HouseImage, Order
from utils import status_code

from utils.functions import is_login
from utils.settings import upload_folder

house_blueprint = Blueprint('house', __name__)


@house_blueprint.route('/myhouse/', methods=['GET'])
def myhouse():
    return render_template('myhouse.html')


# 房源信息
@house_blueprint.route('/house_info/', methods=['GET'])
@is_login
def house_info():
    # 获取用户信息
    user = User.query.get(session['user_id'])
    if user.id_card:
        # 实名认证成功
        houses = House.query.filter(House.user_id == session['user_id']).order_by('-id')
        house_list = [house.to_dict() for house in houses]
        return jsonify(code=status_code.OK, house_list=house_list)
    else:
        return jsonify(status_code.HOUSE_USER_INFO_ID_CARD_INVALID)


# 发布新房源
@house_blueprint.route('/newhouse/', methods=['GET'])
def newhouse():
    return render_template('newhouse.html')


# 获取区域信息
@house_blueprint.route('/area_facility/', methods=['GET'])
def area_facility():
    areas = Area.query.all()
    facilitys = Facility.query.all()

    # 返回所有的区域与房屋信息
    areas_json = [area.to_dict() for area in areas]
    facilitys_json = [facility.to_dict() for facility in facilitys]

    return jsonify(code=status_code.OK, areas=areas_json, facilitys=facilitys_json)


# 后端获取房屋信息
@house_blueprint.route('/newhouse/', methods=['POST'])
def my_newhouse():
    # 保存房屋信息, 设施信息 - request.form : 内字典
    house_dict = request.form

    # 验证参数是否传完
    # 获取房屋基本信息 - 价格, 主题,等
    house = House()
    house.user_id = session['user_id']
    house.price = house_dict.get('price')
    house.title = house_dict.get('title')
    house.area_id = house_dict.get('area_id')
    house.address = house_dict.get('address')
    house.room_count = house_dict.get('room_count')
    house.acreage = house_dict.get('acreage')
    house.unit = house_dict.get('unit')
    house.capacity = house_dict.get('capacity')
    house.beds = house_dict.get('beds')
    house.deposit = house_dict.get('deposit')
    house.min_days = house_dict.get('min_days')
    house.max_days = house_dict.get('max_days')

    # 获取房屋的基础设施信息 - 多对多关系
    facilitys = house_dict.getlist('facility')
    for facility_id in facilitys:
        facility = Facility.query.get(facility_id)
        # 多对多关联
        house.facilities.append(facility)
    house.add_update()

    # 返回房屋的id
    return jsonify(code=status_code.OK, house_id=house.id)


# 房屋图片
@house_blueprint.route('/house_images/', methods=['POST'])
def house_images():
    # 创建房屋图片
    house_id = request.form.get('house_id')
    image = request.files.get('house_image')

    # 保存图片  /static/media/upload/xxx/jpg
    save_url = os.path.join(upload_folder, image.filename)
    image.save(save_url)

    # 保存房屋和图片信息
    house_image = HouseImage()
    house_image.house_id = house_id
    image_url = os.path.join('upload', image.filename)
    house_image.url = image_url
    house_image.add_update()
    # 创建房屋首图
    house = House.query.get(house_id)
    if not house.index_image_url:
        house.index_image_url = image_url
        house.add_update()
    return jsonify(code=status_code.OK, image_url=image_url)


# 详情页面
@house_blueprint.route('/detail/', methods=['GET'])
def detail():
    return render_template('detail.html')


# 获取房屋详情id
@house_blueprint.route('/house_detail/<int:id>/', methods=['GET'])
def house_detail(id):
    # 房屋详情信息 - get获取对象
    house = House.query.get(id)
    return jsonify(code=status_code.OK, house=house.to_full_dict())


# 返回首页
@house_blueprint.route('/index/', methods=['GET'])
def index():
    return render_template('index.html')


@house_blueprint.route('/hindex/', methods=['GET'])
def my_index():
    user_id = session.get('user_id')
    # 验证用户的登录情况
    if user_id:
        user = User.query.get(user_id)
        username = user.name
    else:
        username = ''
        # 返回轮播图
    houses = House.query.filter(House.index_image_url != '')[:3]
    houses_image = [house.to_dict() for house in houses]

    return jsonify(code=status_code.OK, username=username, houses_image=houses_image)


# 返回页面
@house_blueprint.route('/search/', methods=['GET'])
def searh():
    return render_template('search.html')


# 搜索
@house_blueprint.route('/my_search/', methods=['GET'])
def search_house():

    # 区域信息
    aid = request.args.get('aid')
    # 开始时间
    sd = request.args.get('sd')
    # 结束时间
    ed = request.args.get('ed')
    sk = request.args.get('sk')
    # 过滤下区域信息
    house = House.query.filter(House.area_id == aid)
    # 过滤登录用户发布的房屋信息
    if 'user_id' in session:
        hlist = house.filter(House.user_id != session['user_id'])
    # 查询不满足条件的房屋id - 通过订单的开始时间与结束时间满足的条件 - 不能再次下单
    order1 = Order.query.filter(Order.begin_date <= sd, Order.end_date >= ed)

    # 订单开始时间<输入开始时间,订单的结束时间>开始时间
    order2 = Order.query.filter(Order.begin_date <= sd, Order.end_date >= sd)

    # 订单开始时间>入住开始时间, 订单的开始时间<入住结束时间
    order3 = Order.query.filter(Order.begin_date >= sd, Order.begin_date <= ed)

    order4 = Order.query.filter(Order.begin_date >= sd, Order.end_date <= ed)

    # 拿到四种情况房屋id
    house_ids1 = [order.house_id for order in order1]
    house_ids2 = [order.house_id for order in order2]
    house_ids3 = [order.house_id for order in order3]
    house_ids4 = [order.house_id for order in order4]

    house_ids = list(set(house_ids1 + house_ids2 + house_ids3 + house_ids4))

    # 过滤出最终能展示的房屋信息
    houses = hlist.filter(House.id.notin_(house_ids))

    if sk == 'booking':
        houses =houses.order_by('order_count')
    elif sk == 'price-inc':
        houses = houses.order_by('price')
    elif sk == 'price-des':
        houses = houses.order_by('-price')
    else:
        houses = houses.order_by('-id')

    houses_dict = [house.to_dict() for house in houses]
    # 序列化后返给页面
    return jsonify(code=status_code.OK, house_dict=houses_dict)
