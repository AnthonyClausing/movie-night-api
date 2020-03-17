from marshmallow import fields, Schema
from . import db
import datetime

class ReviewModel(db.Model):
  """
  Review Model
  """

  __tablename__ = 'reviews'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(128), nullable=False)
  score = db.Column(db.Numeric, nullable=False)
  text = db.Column(db.String, nullable=False)
  user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  created_at = db.Column(db.DateTime)
  modified_at = db.Column(db.DateTime)

  def __init__(self, data):
    self.title = data.get('title')
    self.score = data.get('score')
    self.text = data.get('text')
    self.user = data.get('user') 
    self.created_at = datetime.datetime.utcnow()
    self.modified_at = datetime.datetime.utcnow()

  def save(self):
    db.session.add(self)
    db.session.commit()

  def update(self, data):
    for key, item in data.items():
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  @staticmethod
  def get_all_reviews():
    return ReviewModel.query.all()
  
  @staticmethod
  def get_one_review(id):
    return ReviewModel.query.get(id)

  def __repr__(self):
    return '<id {}>'.format(self.id)

class ReviewSchema(Schema):
  """
  Review Schema
  """
  id = fields.Int(dump_only=True)
  title = fields.Str(required=True)
  score = fields.Number(required=True)
  text = fields.Str(required=True)
  user = fields.Int(required=True)
  created_at = fields.DateTime(dump_only=True)
  modified_at = fields.DateTime(dump_only=True)
