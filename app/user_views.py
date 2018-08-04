import os
import random
import re

from flask import Blueprint, render_template, jsonify, \
    session, request

from app.models import db, User
from utils import status_code
from utils.functions import is_login
from utils.settings import upload_folder

user_blueprint = Blueprint('user', __name__)


# 视图函数返回页面
@user_blueprint.route('/register/', methods=['GET'])
def register():
    return render_template('register.html')


@user_blueprint.route('/create_db/', methods=['GET'])
def create_db():
    db.create_all()
    return '创建数据库成功'


# 获取验证码
@user_blueprint.route('/get_code/', methods=['GET'])
def get_code():
    # 自定义
    code = ''
    s = '1234567890qwertyuiopasdfghjklzxcvbnm'
    for i in range(4):
        # 随机生成
        code += random.choice(s)
        # 不能直接返回一个字典
    # return {'code': 200, 'msg': '请求成功', 'data': code}
    session['code'] = code
    return jsonify(code=200, msg='请求成功', data=code)


# 验证手机号
@user_blueprint.route('/register/', methods=['POST'])
def my_register():

    # 获取用户信息
    mobile = request.form.get('mobile')
    imagecode = request.form.get('imagecode')
    passwd = request.form.get('passwd')
    passwd2 = request.form.get('passwd2')

    # 验证参数是否完整
    if not all([mobile, imagecode, passwd, passwd2]):
        return jsonify(status_code.USER_REGISTER_PARAMS_VALID)
    # 验证图片验证码是否正确
    if session.get('code') != imagecode:
        return jsonify(status_code.USER_REGISTER_CODE_ERROR)
    # 验证手机号, ^1[3456789]\d{9}$
    if not re.match(r'^1[3456789]\d{9}$', mobile):
        return jsonify(status_code.USER_REGISTER_MOBILE_INVALID)
    # 验证密码
    if passwd != passwd2:
        return jsonify(status_code.USER_REGISTER_PASSWORD_ERROR)
    # 验证手机号是否存在
    if User.query.filter(User.phone == mobile).count():
        # 如果有值, 说明数据库中已存在
        return jsonify(status_code.USER_REGISTER_MOBILE_EXSIST)
    # 数据库中不存在该手机号
    user = User()
    user.phone = mobile
    user.password = passwd
    # 手机号也可以是用户名
    user.name = mobile

    try:
        user.add_update()
        return jsonify(status_code.SUCCESS)
    except:
        return jsonify(status_code.DATABASE_ERROR)


@user_blueprint.route('/login/', methods=['GET'])  # GET请求返回页面 - 前端需要做的
def login():
    return render_template('login.html')


@user_blueprint.route('/login/', methods=['POST'])
def my_login():
    # 获取mobile, password
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    # 校验完整参数
    if not all([mobile, password]):
        return jsonify(status_code.USER_LOGIN_PARAMS_VALID)
        # 验证手机号, ^1[3456789]\d{9}$
    if not re.match(r'^1[3456789]\d{9}$', mobile):
        return jsonify(status_code.USER_REGISTER_MOBILE_INVALID)

    user = User.query.filter(User.phone == mobile).first()
    # 校验用户, 查看用户是否存在
    if user:
        if user.check_pwd(password):
            # 密码校验成功
            session['user_id'] = user.id
            return jsonify(status_code.SUCCESS)
        else:
            return jsonify(status_code.USER_LOGIN_PASSWORD_INVALID)
    else:
        return jsonify(status_code.USER_LOGIN_PHONE_INVALID)


# 退出 - 注销
@user_blueprint.route('/logout/', methods=['GET'])
def logout():
    # 清空session值
    session.clear()
    return jsonify(status_code.SUCCESS)


# 个人中心
@user_blueprint.route('/my/', methods=['GET'])
@is_login
def my():
    return render_template('my.html')


# 获取用户信息
@user_blueprint.route('/user_info/', methods=['GET'])
@is_login
def user_info():
    user_id = session['user_id']
    # 获取user信息
    user = User.query.get(user_id)
    user_info = user.to_basic_dict()
    # 返回数据与状态码
    return jsonify(user_info=user_info, code=status_code.OK)


# 个人信息 - 前端返回页面 - 开发直接调接口
@user_blueprint.route('/profile/', methods=['GET'])
@is_login
def profile():
    return render_template('profile.html')


@user_blueprint.route('/profile/', methods=['PATCH'])
@is_login
def my_profile():
    # 修改头像 - 并保存
    avatar = request.files.get('avatar')
    name = request.form.get('name')
    if avatar:
        # 验证图片 'mimetype = image/jpeg' 'image/png'
        if not re.match(r'image/*', avatar.mimetype):
            return jsonify(status_code.USER_USERINFO_PROFILE_AVATAR_INVALID)
        # 图片保存 static/media/upload/xxx.jpg --> 图片路径
        avatar.save(os.path.join(upload_folder, avatar.filename))
        # 修改用户的avatar字段
        user = User.query.get(session['user_id'])
        avatar_addr = os.path.join('upload', avatar.filename)
        user.avatar = avatar_addr
        try:
            user.add_update()
            return jsonify(code=status_code.OK, avatar=avatar_addr)
        except:
            return jsonify(status_code.DATABASE_ERROR)

    if name:
        # 修改用户名
        if User.query.filter(User.name == name).count():
            return jsonify(status_code.USER_USERINFO_NAME_EXSITS)
        user = User.query.get(session['user_id'])
        # 修改时需判断 用户名是否是惟一的
        user.name = name
        try:
            user.add_update()
            return jsonify(code=status_code.OK)
        except:
            return jsonify(status_code.DATABASE_ERROR)


# 实名认证
@user_blueprint.route('/auth/', methods=['GET'])
def auth():
    return render_template('auth.html')


# 验证字段real_name/id_card
@user_blueprint.route('/auth/', methods=['PATCH'])
def my_auth():
    real_name = request.form.get('real_name')
    id_card = request.form.get('id_card')

    if not all([real_name, id_card]):
        return jsonify(status_code.USER_USERINFO_ID__NAME_CARD_INVALID)

    # 验证身份证号
    if not re.match(r'[1-9]\d{16}[0-9X]', id_card):
        return jsonify(status_code.USER_USERINFO_ID_CARD_INVALID)

    user = User.query.get(session['user_id'])
    user.id_name = real_name
    user.id_card = id_card
    try:
        user.add_update()
        return jsonify(code=status_code.OK)
    except:
        return jsonify(status_code.DATABASE_ERROR)


# 获取实名认证信息
@user_blueprint.route('/read_user_info/', methods=['GET'])
def read_user_info():
    user = User.query.get(session['user_id'])
    user = user.to_auth_dict()
    return jsonify(code=status_code.OK, user=user)
