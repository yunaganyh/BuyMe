from flask import (Flask, url_for, render_template, request, session, redirect, flash, jsonify, send_from_directory)
import random, math
import MySQLdb
import sys,os
from werkzeug import secure_filename
import bcrypt
import sqlFunctions
app = Flask(__name__)

app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

def getConn():
    return sqlFunctions.getConn('c9')
    
@app.route('/')
def home():
    conn = getConn()
    posts = sqlFunctions.getItemsAndUsers(conn)
    return render_template('main.html', posts = posts)

@app.route('/register/', methods=['GET','POST'])
def register():
    conn = getConn()
    if request.method == 'GET':
        return render_template('registration.html')
    else:
        try:
            username = request.form['username']
            passwd1 = request.form['password1']
            print passwd1
            passwd2 = request.form['password2']
            print passwd2
            if passwd1 != passwd2:
                flash('passwords do not match')
                return redirect(request.referrer)
            hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
            print hashed
            row = sqlFunctions.getUser(conn, username)
            if row is not None:
                flash('That username is taken')
                return redirect( url_for('register') )
            name = request.form['name']
            gradYear = request.form['gradYear']
            email = request.form['email']
            dorm = request.form['dorm']
            sqlFunctions.insertUser(conn,username,name,gradYear,dorm,email)
            sqlFunctions.insertUserpass(conn,username,hashed)
            session['username'] = username
            session['logged_in'] = True
            session['visits'] = 1
            return redirect( url_for('account', username=username) )
        except Exception as err:
            flash('form submission error '+str(err))
    return redirect(request.referrer)
    
@app.route('/account/<username>')
def account(username):
    conn = getConn()
    person = sqlFunctions.getUserByUsername(conn,username)
    if person is None:
        flash('User does not exists.')
        return redirect(url_for('login'))
    return render_template('account.html', person = person)

@app.route('/login/')
def login():
    conn = getConn()

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)
