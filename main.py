from flask import Flask, request, redirect, render_template, jsonify,abort,url_for
from threading import Thread
import sqlite3 as lite
from flask_bcrypt import Bcrypt
import jwt
from functools import wraps

app = Flask(__name__)
bcrypt = Bcrypt(app)
con = lite.connect('site.db')

with con:
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT , password TEXT, token TEXT)"
    )


app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba652'

def token_authorization(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    token_cookie = request.cookies.get('token')
    
    if not token_cookie:
      abort(403)

    con = lite.connect('site.db')
    with con:
      cur = con.cursor()
      cur.execute("select * from users")
      while True:
        row = cur.fetchone()
        if row == None:
          abort(403)
        if row[3] == token_cookie:
          return f(*args, **kwargs)

  return decorator

@app.route("/", methods=['GET'])
def home():
  token_cookie = request.cookies.get('token')
  if token_cookie:
    return redirect(url_for('main'))
  return render_template('index.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']

        con = lite.connect('site.db')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM users")
            while True:
                row = cur.fetchone()
                if row == None:
                    break
                if row[1] == username:
                    return jsonify(
                        message=
                        'Username already exists! Please enter another username',
                        result='No')

            token = jwt.encode({'user' : username} , 
            app.config['SECRET_KEY'])
            hashed_pass = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute("INSERT INTO users(username,password,token) VALUES (?,?,?)",
                        (username, hashed_pass,token))

        return jsonify(username=username, result='Yes')

    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
      # write code for login here
      username = request.form['username']
      password = request.form['pass']
      
      conn= lite.connect('site.db')
      cursor= conn.cursor()
      cursor.execute("select * from users")
      while True:
        row= cursor.fetchone()
        if row==None :
          break
        if row[1] == username and not bcrypt.check_password_hash(row[2],password):
          return jsonify(message = "Incorrect Password.", success='no')
        if row[1]== username and bcrypt.check_password_hash(row[2],password):
          token = row[3]
          return jsonify(username = username, success='yes', token = token)

      return jsonify(message="Usename Does not Exists.", success='no')

    return render_template('login.html')


@app.route("/main", methods=['GET'])
@token_authorization
def main():
    return render_template('main.html')


# #The server is ran through local host on server via 8080 port
def run():
    app.run(host='0.0.0.0', port=7000)


t = Thread(target=run)
t.start()
