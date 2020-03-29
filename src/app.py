
from flask import Flask

from .config import app_config
from .models import db, bcrypt

from .views.UserView import user_api as user_blueprint
from .views.ReviewView import review_api as review_blueprint

def create_app(env_name):
  """
  Create app
  """
  
  # app initialization
  app = Flask(__name__)
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config.from_object(app_config[env_name])
  bcrypt.init_app(app)
  db.init_app(app)

  app.register_blueprint(user_blueprint, url_prefix='/v1/users')
  app.register_blueprint(review_blueprint, url_prefix="/v1/reviews")
  @app.route('/', methods=['GET'])
  def index():
    """
    example endpoint
    """
    return 'Congratulations! Your first endpoint is workin'

  return app