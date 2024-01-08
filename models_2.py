from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin

db = SQLAlchemy()

class Username(UserMixin,db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    email= db.Column(db.String(50),nullable = False)
    u_name = db.Column(db.String(50),nullable = False)
    password = db.Column(db.String(50),nullable = False)
    #passw = db.relationship('Pass', backref = "creator", secondary = "association")

    def __repr__(self):
        return f"<director {self.name}>"
    
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)


    def __repr__(self):
        return f"<director {self.name}>"

'''class Pass(db.Model):
    p_id = db.Column(db.Integer(), primary_key = True)
    password = db.Column(db.String(50),nullable = False)
    # creator = db.relationship('Director', backref = "films")

    def __repr__(self):
        return f"<movie {self.name}>"

class Association(db.Model):
    user_id = db.Column(db.Integer(), db.ForeignKey("username.u_id"), primary_key = True)
    password_id = db.Column(db.Integer(), db.ForeignKey("pass.p_id"), primary_key = True)
   ''' 