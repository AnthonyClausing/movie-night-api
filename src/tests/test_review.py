import unittest
import os
import json
from ..app import create_app, db


class ReviewsTest(unittest.TestCase):
  def setUp(self):
    """
    Test Setup
    """
    self.app = create_app("testing")
    self.client = self.app.test_client
    self.user = {
      'name': 'olawale',
      'email': 'olawale@mail.com',
      'password': 'passw0rd!'
    }
    self.review = {
      'title': 'Nice Guys',
      'score': 6,
      'text': 'Was okay I guess, could have been better'
    }
    self.headers= {
      'Content-Type': 'application/json'
    }

    with self.app.app_context():
      # create all tables
      db.create_all()

  def test_review_creation(self):
    created_user = self.client().post('/v1/users/', headers=self.headers, data=json.dumps(self.user))
    token = json.loads(created_user.data).get('jwt_token')
    self.headers['api-token'] = token
    res = self.client().post('/v1/reviews/', headers=self.headers, data=json.dumps(self.review))
    json_data = json.loads(res.data)

    self.assertTrue(json_data.get('score'))
    self.assertEqual(res.status_code, 201)
  
  def test_review_creation_with_empty_request(self):
    created_user = self.client().post('/v1/users/', headers=self.headers, data=json.dumps(self.user))
    token = json.loads(created_user.data).get('jwt_token')
    self.headers['api-token'] = token
    review1 = {}
    res = self.client().post('/v1/reviews/', headers=self.headers, data=json.dumps(review1))
    
    self.assertEqual(res.status_code, 400)
  
  def test_get_all_reviews(self):
    created_user = self.client().post('/v1/users/', headers=self.headers, data=json.dumps(self.user))
    token = json.loads(created_user.data).get('jwt_token')
    self.headers['api-token'] = token
    self.client().post('/v1/reviews/', headers=self.headers, data=json.dumps(self.review))
    res = self.client().get('/v1/reviews/', headers=self.headers)
    json_data = json.loads(res.data)

    self.assertEqual(len(json_data), 1)
    self.assertEqual(res.status_code, 200)
  
  def test_get_one_review(self):
    created_user = self.client().post('/v1/users/', headers=self.headers, data=json.dumps(self.user))
    token = json.loads(created_user.data).get('jwt_token')
    self.headers['api-token'] = token
    self.client().post('/v1/reviews/', headers=self.headers, data=json.dumps(self.review))
    res = self.client().get('/v1/reviews/1', headers=self.headers)
    json_data = json.loads(res.data)

    self.assertEqual(json_data.get('id'), 1)
    self.assertEqual(res.status_code, 200)
  
  def test_get_one_review_where_review_does_not_exist(self):
    res = self.client().get('/v1/reviews/1', headers=self.headers)
    json_data = json.loads(res.data)
    self.assertEqual(json_data['error'], 'post not found')
    self.assertEqual(res.status_code, 404)

  def test_delete_review(self):
    created_user = self.client().post('/v1/users/', headers=self.headers, data=json.dumps(self.user))
    token = json.loads(created_user.data).get('jwt_token')
    self.headers['api-token'] = token
    self.client().post('/v1/reviews/', headers=self.headers, data=json.dumps(self.review))
    res = self.client().delete('/v1/reviews/1', headers=self.headers)
    self.assertEqual(res.status_code, 204)
  
  def test_delete_review_where_review_does_not_exist(self):
    created_user = self.client().post('/v1/users/', headers=self.headers, data=json.dumps(self.user))
    token = json.loads(created_user.data).get('jwt_token')
    self.headers['api-token'] = token
    res = self.client().delete('/v1/reviews/1', headers=self.headers)
    json_data = json.loads(res.data)
    self.assertEqual(json_data['error'], 'post not found')
    self.assertEqual(res.status_code, 404)
  
  def test_delete_review_where_user_does_not_match(self):
    created_user1 = self.client().post('/v1/users/', headers=self.headers, data=json.dumps(self.user))
    token = json.loads(created_user1.data).get('jwt_token')
    self.headers['api-token'] = token
    self.client().post('/v1/reviews/', headers=self.headers, data=json.dumps(self.review))
    self.user['email'] = "newTest@email.com"
    self.user['name'] = 'Tester'
    created_user2 = self.client().post('/v1/users/', headers=self.headers, data=json.dumps(self.user))
    token = json.loads(created_user2.data).get('jwt_token')
    self.headers['api-token'] = token
    res = self.client().delete('/v1/reviews/1', headers=self.headers)
    json_data = json.loads(res.data)
    self.assertEqual(json_data['error'], 'permission denied')
    self.assertEqual(res.status_code, 400)

  def tearDown(self):
    """
    Tear Down
    """
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

if __name__ == "__main__":
  unittest.main() 