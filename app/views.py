from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from app import app, db, lm
from .forms import LoginForm, EditForm, PostForm, RegisterForm
from .models import User, Post
from datetime import datetime
from config import POSTS_PER_PAGE


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
	g.user.last_seen = datetime.utcnow()
	db.session.add(g.user)
	db.session.commit()


@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
@app.route('/index/<int:page>', methods=["GET", "POST"])
@login_required
def index(page=1):
    form=PostForm()
    if form.validate_on_submit():
	post= Post(body=form.post.data, timestamp=datetime.utcnow(),author=g.user)
	db.session.add(post)
	db.session.commit()
	flash("Your post was published!")
	return redirect(url_for("index"))
   
    posts=g.user.friends_posts().paginate(page,POSTS_PER_PAGE,False)
  
    return render_template("index.html", form=form, posts=posts, user=g.user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate():
	user = User.query.filter_by(nickname=form.nickname.data).first()
	login_user(user, remember= form.remember_me.data)
        if 'remember_me' in session:
           remember_me = session['remember_me']
           session.pop('remember_me', None)
        session["email"]=user.email
	flash(u"Successfully logged in as %s" % form.nickname.data)
        session['remember_me'] = form.remember_me.data
        return redirect(url_for('index'))
    return render_template('login.html', form=form)




@app.route('/register', methods=['GET', 'POST'])
def register(): 
    form = RegisterForm()
    if form.validate_on_submit():	
	newuser= User(nickname=form.nickname.data, password=form.password.data, email=form.email.data, age=form.age.data)
	
	db.session.add(newuser)
	db.session.commit()
	login_user(newuser)
	session["email"]=newuser.email
        return redirect(url_for("index"))
    return render_template('register.html',form=form)




@app.route('/logout')
def logout():
	logout_user()
	session.pop("email",None)   
    	return redirect(url_for('login'))

@app.route('/delete')
def delete():
	db.session.delete(g.user)
	db.session.commit()
	logout_user()
	session.pop("email",None) 	
    	return redirect(url_for('login'))

@app.route("/user/<nickname>")
@app.route("/user/<nickname>/<int:page>")
@login_required
def user(nickname, page=1):
	user= User.query.filter_by(nickname=nickname).first()
	if user == None:
		flash("User %s not found." % nickname)
		return redirect(url_for("index"))
	posts=user.posts.paginate(page,POSTS_PER_PAGE,False)
  	friends=g.user.friended_users().paginate(page,POSTS_PER_PAGE,False)
	allusers=User.query.paginate(page,POSTS_PER_PAGE,False)	
	return render_template("user.html", user=user, posts=posts,friends=friends, users=allusers)

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
	form = EditForm(g.user.nickname)
	if form.validate_on_submit():
		g.user.nickname=form.nickname.data
		g.user.about_me=form.about_me.data		
		g.user.age=form.age.data
		db.session.add(g.user)
		db.session.commit()
		flash("Your changes were saved!")
		return redirect(url_for("edit"))
	else:
		form.nickname.data=g.user.nickname
		form.age.data=g.user.age
		form.about_me.data=g.user.about_me
	return render_template("edit.html", form=form)
@app.errorhandler(401)
def not_found_error(error):
	return render_template("401.html"), 401

@app.errorhandler(404)
def not_found_error(error):
	return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template("500.heml"), 500

@app.route("/friend/<nickname>")
@login_required
def friend(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash("User %s not found!" % nickname)
		return redirect(url_for("index"))
	if user == g.user:
		flash("Impossible to make friends with yourself!")
		return redirect(url_for("user", nickname=nickname))
	u1=g.user.friended(user)
	u2=user.friended(g.user)
	if u1 is None or u2 is None:
		flash("Cannot be friends with :"+nickname+"!")
		return redirect(url_for("user",nickname=nickname))
	db.session.add(u1)
	db.session.add(u2)
	db.session.commit()
	flash("You are frieds with user:"+nickname+".")
	return redirect(url_for("user",nickname=nickname))

@app.route("/unfriend/<nickname>")
@login_required
def unfriend(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash("User %s not found!" % nickname)
		return redirect(url_for("index"))
	if user == g.user:
		flash("Impossible to delete yourself!")
		return redirect(url_for("user", nickname=nickname))
	u1=g.user.unfriend(user)
	u2=user.unfriend(g.user)
	if u1 is None or u2 is None:
		flash("Cannot delete friend: "+nickname+"!")
		return redirect(url_for("user",nickname=nickname))
	db.session.add(u1)
	db.session.add(u2)
	db.session.commit()
	flash("You deleted user: "+nickname+" from your friends.")
	return redirect(url_for("user",nickname=nickname))

@app.route("/bff/<nickname>")
@login_required
def bff(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash("User %s not found!" % nickname)
		return redirect(url_for("index"))
	if user == g.user:
		flash("Impossible to make best friends with yourself!")
		return redirect(url_for("user", nickname=nickname))
	u=g.user.add_bff(user)	
	if u is None :
		flash("Cannot be best friends with :"+nickname+"!")
		return redirect(url_for("user",nickname=nickname))
	db.session.add(u)	
	db.session.commit()
	flash("You added best friend: "+nickname+".")
	return redirect(url_for("user",nickname=nickname))

@app.route("/unbff/<nickname>")
@login_required
def unbff(nickname):
	user = User.query.filter_by(nickname=nickname).first()
	if user is None:
		flash("User %s not found!" % nickname)
		return redirect(url_for("index"))
	if user == g.user:
		flash("Impossible to delete yourself as best friend!")
		return redirect(url_for("user", nickname=nickname))
	u=g.user.remove_bff(user)
	if u is None:
		flash("Cannot delete best friend: "+nickname+"!")
		return redirect(url_for("user",nickname=nickname))
	db.session.add(u)
	db.session.commit()
	flash("You deleted best fiend: "+nickname+".")
	return redirect(url_for("user",nickname=nickname))



@app.route("/all_users")
@app.route("/all_users/<int:page>")
@login_required
def all_users(page=1):	
	allusers=User.query.paginate(page,POSTS_PER_PAGE,False)

	return render_template("all_users.html", user=g.user, users=allusers)



	 


