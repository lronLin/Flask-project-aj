
from flask_script import Manager

from utils.app import create_app

app = create_app()

manage = Manager(app)


if __name__ == '__main__':

    # app.run(debug=True, port=8000, host='127.0.0.1')
    # manage.py 主要功能是run, 其他功能封装到utils下面的app.py中去实现
    manage.run()
