from functools import wraps

from flask import session, redirect, url_for


def get_sqlalchemy_uri(DATABASE):

    return '%s+%s://%s:%s@%s:%s/%s' % (DATABASE['ENGINE'],
                                       DATABASE['DRIVER'],
                                       DATABASE['USER'],
                                       DATABASE['PASSWORD'],
                                       DATABASE['HOST'],
                                       DATABASE['PORT'],
                                       DATABASE['DB']
                                       )


# 装饰器 - 就是闭包 - 函数里套函数 - 外套函数返回内层函数 - 内层函数返回传的函数
def is_login(func):

    # 用functools装饰函数 - 防止属性变化
    @wraps(func)
    def check_login(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            # 跳转到用户登录页面
            return redirect(url_for('user.login'))

    return check_login




