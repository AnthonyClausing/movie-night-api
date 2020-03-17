
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
#######
# existing code remains #
#######
bcrypt = Bcrypt()
# initialize our db
db = SQLAlchemy()