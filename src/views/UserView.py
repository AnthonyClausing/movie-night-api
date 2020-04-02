from flask import request, json, Response, Blueprint, g, jsonify, make_response
from ..models.UserModel import UserModel, UserSchema
from ..shared.Authentication import Auth
from marshmallow import ValidationError

user_api = Blueprint('users', __name__)
user_schema = UserSchema()

@user_api.after_request # blueprint can also be app~~
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, PATCH, DELETE'
    header['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, x-auth'
    return response

@user_api.route('/', methods=['POST'])
def create():
  """
  Create User Function
  """
 
  req_data = request.get_json()
  try:
    data = user_schema.load(req_data)
  except ValidationError as error:
    return custom_response(error.messages, 400)
  # check if user already exist in the db
  user_in_db = UserModel.get_user_by_email(data.get('email'))
  if user_in_db:
    message = {'error': 'User already exist, please supply another email address'}
    return custom_response(message, 400)
  
  user = UserModel(data)
  user.save()
  ser_data = user_schema.dump(user)

  token = Auth.generate_token(ser_data.get('id'))
  return custom_response({'jwt_token': token}, 201)

# @user_api.route('/', methods=['GET'])
# @Auth.auth_required
# def get_all():
#   users = UserModel.get_all_users()
#   ser_users = user_schema.dump(users, many=True)
#   return custom_response(ser_users, 200)


@user_api.route('/login', methods=['POST'])
def login():
  req_data = request.get_json()
  
  try:
    data = user_schema.load(req_data, partial=True)
  except ValidationError as error:
    return custom_response(error.messages, 400)
  
  if not data.get('email') or not data.get('password'):
    return custom_response({'error': 'you need email and password to sign in'}, 400)
  
  user = UserModel.get_user_by_email(data.get('email'))

  if not user:
    return custom_response({'error': 'invalid credentials'}, 400)
  
  if not user.check_hash(data.get('password')):
    return custom_response({'error': 'invalid credentials'}, 400)
  
  ser_data = user_schema.dump(user)
  
  token = Auth.generate_token(ser_data.get('id'))

  return custom_response({'jwt_token': token}, 200)  

# @user_api.route('/<int:user_id>', methods=['GET'])
# @Auth.auth_required
# def get_a_user(user_id):
#   """
#   Get a single user
#   """
#   user = UserModel.get_one_user(user_id)
#   if not user:
#     return custom_response({'error': 'user not found'}, 404)
  
#   ser_user = user_schema.dump(user)
#   return custom_response(ser_user, 200)

@user_api.route('/me', methods=['PUT'])
@Auth.auth_required
def update():
  """
  Update me
  """
  req_data = request.get_json()
  try:
    data = user_schema.load(req_data, partial=True)
  except ValidationError as error:
    return custom_response(error.messages, 400)
  
  user = UserModel.get_one_user(g.user.get('id'))
  user.update(data)
  ser_user = user_schema.dump(user)
  return custom_response(ser_user, 200)

@user_api.route('/me', methods=['GET'])
@Auth.auth_required
def get_me():
  """
  Get me
  """
  user = UserModel.get_one_user(g.user.get('id'))
  ser_user = user_schema.dump(user)
  return custom_response(ser_user, 200)


def custom_response(res, status_code):
  """
  Custom Response Function
  """
  resp = Response(
    mimetype="application/json",
    response=json.dumps(res),
    status=status_code
  )
  resp.headers['Access-Control-Allow-Origin'] = '*'
  resp.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
  resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
  return resp
