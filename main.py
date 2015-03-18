from flask import Flask,render_template,request
from flask.ext.login import LoginManager,login_required,login_user
import pickledb
import uuid
from passlib.hash import sha512_crypt

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"
app.secret_key = "hallo"
db = pickledb.load('users.db', True)
if not db.get('users'):
    db.dcreate('users')

#self.app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=2)
#@app.route("/")
#def login(name=None):
#    return render_template('login.html', name=name)

@app.route('/', methods=['POST', 'GET'])
def root():
    return render_template('login.html')

@app.route('/hello')
@login_required
def hello():
    return render_template('hello.html')

@app.route('/create', methods=['POST', 'GET'])
def create():
    e_message = None
    error = False
    if request.method == 'POST':
        name = request.form['login']
        passw = request.form['password']
        if name.strip() == "":
            error = True
            e_message = "Username cannot be blank."
            return render_template('create.html', error=error,e_message = e_message)
        if ' ' in name or '"' in name or '{' in name or '}' in name or '[' in name or ']' in name or ':' in name or ',' in name:
            error = True
            e_message = "Username cannot contain the following characters: \"\'{}[]:,"
            return render_template('create.html', error=error,e_message = e_message)
        if create_user(name,passw):
            return render_template('hello.html', name=name)
        else:
            error = True
            e_message = 'User already exists or other error!'
    return render_template('create.html', error=error,e_message = e_message)

def create_user(name,passw):
    if not user_exists(name):
        print "Users does not exist. Creating."
        hash = sha512_crypt.encrypt(passw)
        db.dadd('users',(name,[str(uuid.uuid4()),hash]))
        return True
    else:
        return False

def user_exists(name):
    try:
        if db.dexists('users',name) == 1:
            return True
        else:
            return False
    except KeyError:
        return False
    

@app.route('/submit', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        name = request.form['username']
        print name
        passw = request.form['password']
        print name,' ',passw
        if valid_login(name,passw):
            return log_the_user_in(name)
        else:
            error = 'Invalid username/password'
    return render_template('login.html',error=error)

def log_the_user_in(name=None):
    print name
    return render_template('hello.html', name=name)

def valid_login(name=None, password=None):
    try:
        creds = db.dget('users',name)

        if sha512_crypt.verify(password, creds[1]):
            return True
        else:
            return False
    except KeyError: 
        return False

if __name__ == "__main__":
    app.debug = True
    app.run()