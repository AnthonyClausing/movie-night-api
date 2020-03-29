import jwt
import os
import datetime
from functools import wraps
from flask import json, Response, request, g, jsonify, make_response
from ..models.UserModel import UserModel


class Auth():
  """
  Auth Class
  """
  @staticmethod
  def generate_token(user_id):
    """
    Generate Token Method
    """
    try:
      payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
      }
      return jwt.encode(
        payload,
        os.getenv('JWT_SECRET_KEY'),
        'HS256'
      ).decode("utf-8")
    except Exception as e:
      return make_response(jsonify({'error': 'error in generating user token'}), 400)

  @staticmethod
  def decode_token(token):
    """
    Decode token method
    """
    re = {'data': {}, 'error': {}}
    try:
      payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
      re['data'] = {'user_id': payload['sub']}
      return re
    except jwt.ExpiredSignatureError as e1:
      re['error'] = {'message': 'token expired, please login again'}
      return re
    except jwt.InvalidTokenError:
      re['error'] = {'message': 'Invalid token, please try again with a new token'}
      return re

  @staticmethod
  def auth_required(func):
    """
    Auth decorator
    """
    @wraps(func)
    def decorated_auth(*args, **kwargs):
      if 'api-token' not in request.headers:
        return make_response(jsonify({'error': 'Authentication token is not available, please login to get one'}), 400)
      
      token = request.headers.get('api-token')
      data = Auth.decode_token(token)
      if data['error']:
        return make_response(jsonify({'error': 'whatthefuck'}), 400)
        
      user_id = data['data']['user_id']
      check_user = UserModel.get_one_user(user_id)
      if not check_user:
        return make_response(jsonify({'error': 'user does not exist, invalid token'}),400)
      g.user = {'id': user_id}
      return func(*args, **kwargs)
    return decorated_auth