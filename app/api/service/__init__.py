from flask_restful import Api
from api import create_app
from flasgger import Swagger

app = create_app('production')
app.config['SWAGGER'] = {
    'title': '监测预警',
    'uiversion': 3,  # 数字必须为 3
    'description': 'Python Flask相关接口'
}
swagger = Swagger(app)
api = Api(app)

from api.service import views

# 接口注册
api.add_resource(views.ImageView, '/comparison')
api.add_resource(views.Picture, '/base')
