from flask import request, g, Blueprint, json, Response
from ..shared.Authentication import Auth
from ..models.ReviewModel import ReviewModel, ReviewSchema
from marshmallow import ValidationError

review_api = Blueprint('review_api', __name__)
review_schema = ReviewSchema()


@review_api.route('/', methods=['POST'])
@Auth.auth_required
def create():
  """
  Create Review Function
  """
  req_data = request.get_json()
  req_data['user'] = g.user.get('id')
  try:
    data = review_schema.load(req_data)
    post = ReviewModel(data)
    post.save()
    data = review_schema.dump(post)
    return custom_response(data, 201)
  except ValidationError as error:
    return custom_response(error.messages, 400)

@review_api.route('/', methods=['GET'])
def get_all():
  """
  Get All Reviews
  """
  posts = ReviewModel.get_all_reviews()
  data = review_schema.dump(posts, many=True)
  return custom_response(data, 200)

@review_api.route('/<int:review_id>', methods=['GET'])
def get_one(review_id):
  """
  Get A Review
  """
  post = ReviewModel.get_one_review(review_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = review_schema.dump(post)
  return custom_response(data, 200)

# @review_api.route('/<int:review_id>', methods=['PUT'])
# @Auth.auth_required
# def update(review_id):
#   """
#   Update A Review
#   """
#   req_data = request.get_json()
#   post = ReviewModel.get_one_review(review_id)
#   if not post:
#     return custom_response({'error': 'post not found'}, 404)
#   data = review_schema.dump(post)
#   if data.get('user') != g.user.get('id'):
#     return custom_response({'error': 'permission denied'}, 400)
#   try:
#     data = review_schema.load(req_data, partial=True)
#     post.update(data)
#     data = review_schema.dump(post)
#     return custom_response(data, 200)
#   except ValidationError as error:
#     return custom_response(error.messages, 400)

@review_api.route('/<int:review_id>', methods=['DELETE'])
@Auth.auth_required
def delete(review_id):
  """
  Delete A Review
  """
  post = ReviewModel.get_one_review(review_id)
  if not post:
    return custom_response({'error': 'post not found'}, 404)
  data = review_schema.dump(post)
  print(data)
  if data.get('user') != g.user.get('id'):
    return custom_response({'error': 'permission denied'}, 400)
  post.delete()
  return custom_response({'message': 'deleted'}, 204)

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
  resp.headers['Access-Control-Allow-Methods'] = '*'
  resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
  return resp