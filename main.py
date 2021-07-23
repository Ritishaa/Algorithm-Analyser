from flask import Flask, request, redirect, render_template, jsonify
from threading import Thread
import sqlite3 as lite

app = Flask(__name__)
con = lite.connect('site.db')

with con:
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT , password TEXT)"
    )


@app.route("/", methods=['GET'])
def home():
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

            cur.execute("INSERT INTO users(username,password) VALUES (?,?)",
                        (username, password))

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
        if row[1] == username and row[2]!=password:
          return jsonify(message = "Incorrect Password.", success='no')
        if row[1]== username and row[2] == password:
          return jsonify(username = username, success='yes')

      return jsonify(message="Usename Does not Exists.", success='no')

    return render_template('login.html')


@app.route("/main", methods=['GET'])
def main():
    return render_template('main.html')


# #The server is ran through local host on server via 8080 port
def run():
    app.run(host='0.0.0.0', port=7000)


t = Thread(target=run)
t.start()
