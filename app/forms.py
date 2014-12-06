from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, Required, Email
from app.models import User

class LoginForm(Form):
    nickname = StringField('nickname',[DataRequired()])
    password = PasswordField('password', [DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

    def __init__(self, *args, **kwargs):
	Form.__init__(self,*args,**kwargs)
	self.user= None
    def validate(self):
	rv= Form.validate(self)
	if not rv:
		return False
	user= User.query.filter_by(nickname=self.nickname.data).first()
	if user is None:
		self.nickname.errors.append("Unknows nickname")
		return False
	if not user.check_password(self.password.data):
		self.password.errors.append("Invalid password")
		return False
	self.user = user
	return True

class RegisterForm(Form):
	nickname= StringField('nickname', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])
	email = StringField('email', validators=[DataRequired(), Email()])
	age = StringField('age', validators=[DataRequired()])

	def __init__ (self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
	def validate(self):
		
		
		if not Form.validate(self):
			return False
		user = User.query.filter_by(nickname=self.nickname.data.lower()).first()
		if user:
			self.nickname.errors.append("nickname is taken")
			return False
		email = User.query.filter_by(email=self.email.data.lower()).first()
		if email:
			self.email.errors.append("Email is taken")
			return False


		return True



class EditForm(Form):
	nickname = StringField("nickname", validators=[DataRequired()])
	age = StringField("age", validators=[DataRequired()])
	about_me = TextAreaField("about_me", validators=[Length(min=0, max=120)])

	def __init__ (self, original_nickname, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.original_nickname=original_nickname

	def validate(self):
		if not Form.validate(self):
			return False
		if self.nickname.data == self.original_nickname:
			return True
		user = User.query.filter_by(nickname=self.nickname.data).first()
		if user!= None:
			self.nickname.errors.append("This nickname is unavaliable. Please choose another one!")
			return False
		return True

class PostForm(Form):
	post = TextAreaField("post", validators=[Length(min=0, max=160)])
