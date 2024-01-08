from flask import Flask, render_template, request, redirect  ,url_for, flash, session ,Blueprint ,request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager , login_user
from flask_login import login_required, current_user, logout_user
from flask_socketio import SocketIO, join_room, leave_room ,emit,send
from io import BytesIO

from models_2 import *

# =================================== Configuration ===============================

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config["SESSION_PERMANENT"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///manymanydata.sqlite3"

login_manager = LoginManager()
login_manager.login_view = '/'
login_manager.init_app(app)
socketio = SocketIO(app)



@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return Username.query.get(int(user_id))


db.init_app(app)
app.app_context().push()


rooms = {}

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('psw')
        user = Username.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect('/')
        login_user(user)
        
        return redirect('/home')





@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('uname')
        email=request.form.get('email')
        password= request.form.get('psw')

        user=Username.query.filter_by(email=email).first()

        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists')
            return redirect('/register')
        new_user = Username(email=email, u_name=name, password=generate_password_hash(password))

        db.session.add(new_user)
        db.session.commit()

        return redirect('/')
    
@app.route('/home',methods=['GET','POST'])
@login_required
def home():
    
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room",methods=['GET','POST'])

def room():
    
    
    
     
    
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@app.route("/roomUser",methods=['GET','POST'])

def roomUser():
    if request.method == 'POST':
        room = session.get("room")
        file = request.files['file']

        upload = Upload(filename=file.filename, data=file.read())
        db.session.add(upload)
        db.session.commit()

        return render_template("room.html", code=room, messages=rooms[room]["messages"])
     
    
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])


@app.route('/UserHome',methods=['GET','POST'])

def UserHome():
    
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("homeUser.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("homeUser.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("homeUser.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("roomUser"))

    return render_template("homeUser.html")


@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")


    
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")







if __name__ == "__main__":
    app.run(debug = True)