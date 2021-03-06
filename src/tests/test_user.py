import unittest
import os
import json
from ..app import create_app, db

class UsersTest(unittest.TestCase):
  """
  Users Test Case
  """
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

    with self.app.app_context():
      # create all tables
      db.create_all()
  def test_response_headers(self):
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertTrue(res.headers['Access-Control-Allow-Origin'])
    self.assertTrue(res.headers['Access-Control-Allow-Methods'])
    self.assertTrue(res.headers['Access-Control-Allow-Headers'])

  def test_user_creation(self):
    """ test user creation with valid credentials """
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data)
    self.assertTrue(json_data.get('jwt_token'))
    self.assertEqual(res.status_code, 201)

  def test_user_creation_with_existing_email(self):
    """ test user creation with already existing email"""
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 400)
    self.assertTrue(json_data.get('error'))

  def test_user_creation_with_no_password(self):
    """ test user creation with no password"""
    user1 = {
      'name': 'olawale',
      'email': 'olawale1@mail.com',
    }
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 400)
    self.assertTrue(json_data.get('password'))

  def test_user_creation_with_no_email(self):
    """ test user creation with no email """
    user1 = {
      'name': 'olawale',
      'pasword': 'olawale1@mail.com',
    }
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 400)
    self.assertTrue(json_data.get('email'))

  def test_user_creation_with_empty_request(self):
    """ test user creation with empty request """
    user1 = {}
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(user1))
    self.assertEqual(res.status_code, 400)
  
  def test_user_login(self):
    """ User Login Tests """
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/v1/users/login', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    json_data = json.loads(res.data)
    self.assertTrue(json_data.get('jwt_token'))
    self.assertEqual(res.status_code, 200)

  def test_user_login_with_invalid_password(self):
    """ User Login Tests with invalid credentials """
    user1 = {
      'password': 'olawale',
      'email': 'olawale@mail.com',
    }
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/v1/users/login', headers={'Content-Type': 'application/json'}, data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertFalse(json_data.get('jwt_token'))
    self.assertEqual(json_data.get('error'), 'invalid credentials')
    self.assertEqual(res.status_code, 400)
  
  def test_user_login_with_invalid_user_data(self):
    user1 = {
      'broken': 'broken',
      'email': 'olawale@mail.com',
    }
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/v1/users/login', headers={'Content-Type': 'application/json'}, data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertFalse(json_data.get('jwt_token'))
    self.assertEqual(json_data.get('broken')[0], 'Unknown field.')
    self.assertEqual(res.status_code, 400)

  def test_user_login_with_missing_password(self):
    user1 = {
      'email': 'olawale@mail.com',
    }
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/v1/users/login', headers={'Content-Type': 'application/json'}, data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertFalse(json_data.get('jwt_token'))
    self.assertEqual(json_data.get('error'),'you need email and password to sign in')
    self.assertEqual(res.status_code, 400)

  def test_user_login_with_invalid_email(self):
    """ User Login Tests with invalid credentials """
    user1 = {
      'password': 'passw0rd!',
      'email': 'olawale1111@mail.com',
    }
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/v1/users/login', headers={'Content-Type': 'application/json'}, data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertFalse(json_data.get('jwt_token'))
    self.assertEqual(json_data.get('error'), 'invalid credentials')
    self.assertEqual(res.status_code, 400)

  def test_user_get_me(self):
    """ Test User Get Me """
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    api_token = json.loads(res.data).get('jwt_token')
    res = self.client().get('/v1/users/me', headers={'Content-Type': 'application/json', 'api-token': api_token})
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 200)
    self.assertEqual(json_data.get('email'), 'olawale@mail.com')
    self.assertEqual(json_data.get('name'), 'olawale')

  def test_user_update_me(self):
    """ Test User Update Me """
    user1 = {
      'name': 'new name'
    }
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    api_token = json.loads(res.data).get('jwt_token')
    res = self.client().put('/v1/users/me', headers={'Content-Type': 'application/json', 'api-token': api_token}, data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 200)
    self.assertEqual(json_data.get('name'), 'new name')
    
  def test_user_update_me_with_wrong_credentials(self):
    """ Test User Update Me """
    user1 = {
      'wrong_key': 'this is so broken'
    }
    res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    api_token = json.loads(res.data).get('jwt_token')
    res = self.client().put('/v1/users/me', headers={'Content-Type': 'application/json', 'api-token': api_token}, data=json.dumps(user1))
    json_data = json.loads(res.data)
    print(res)
    self.assertTrue(json_data['wrong_key'])
    self.assertEqual(res.status_code, 400)
  # def test_delete_user(self):
  #   """ Test User Delete """
  #   res = self.client().post('/v1/users/', headers={'Content-Type': 'application/json'}, data=json.dumps(self.user))
  #   self.assertEqual(res.status_code, 201)
  #   api_token = json.loads(res.data).get('jwt_token')
  #   res = self.client().delete('/v1/users/me', headers={'Content-Type': 'application/json', 'api-token': api_token})
  #   self.assertEqual(res.status_code, 204)
    
  def tearDown(self):
    """
    Tear Down
    """
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

if __name__ == "__main__":
  unittest.main() 