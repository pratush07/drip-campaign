from app import db
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True)
    credentials = db.Column(db.Text, unique=True)

    def __init__(self, user_id, credentials):
	    self.credentials = credentials
	    self.user_id = user_id

class Campaign(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	camp_title = db.Column(db.Text, unique=True)
	thread_id = db.Column(db.Text)

	def __init__(self, camp_title, thread_id=None):
		self.camp_title = camp_title
		self.thread_id = thread_id

db.create_all()