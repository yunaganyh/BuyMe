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
            passwd2 = request.form['password2']
            if passwd1 != passwd2:
                flash('passwords do not match')
                return redirect(request.referrer)
            hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
            row = sqlFunctions.getUser(conn, username)
            if row is not None:
                flash('That username is taken')
                return redirect( url_for('register') )
        #     curs.execute('INSERT into userpass(username,hashed) VALUES(%s,%s)',
        #                  [username, hashed])
        #     session['username'] = username
        #     session['logged_in'] = True
        #     session['visits'] = 1
        #     return redirect( url_for('user', username=username) )
        except Exception as err:
            flash('form submission error '+str(err))
    return redirect(request.referrer)
    
    
@app.route('/login/', methods=['POST'])
def login():
    try:
        username = request.form['login_username']
        passwd = request.form['login_password']
        # print(username)
        conn = getConn()
        curs = conn.cursor(MySQLdb.cursors.DictCursor)
        curs.execute('SELECT hashed FROM userpass WHERE username = %s',
                     [username])
        row = curs.fetchone()
        # print passwd
        if row is None:
            # Same response as wrong password, so no information about what went wrong
            flash('login incorrect. Try again or join')
            return redirect( url_for('home'))
        hashed = row['hashed']
        if hashed == passwd:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['logged_in'] = True
            session['visits'] = 1
            print(username)
            return redirect( url_for('user', username=username) )
        else:
            flash('login incorrect. Try again or join')
            return redirect( url_for('home'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('home') )   
@app.route('/user/<username>')
def user(username):
    try:
        # don't trust the URL; it's only there for decoration
        conn = getConn()
        posts = sqlFunctions.getItemsAndUsers(conn)
        if 'username' in session:
            username = session['username']
            session['visits'] = 1+int(session['visits'])
            return render_template('main.html',posts=posts,
                                   username=username,
                                   visits=session['visits'])
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('home') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('home') )

@app.route('/logout/')
def logout():
    try:
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('logged_in')
            flash('You are logged out')
            return redirect(url_for('home'))
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('home') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('home') )

    
    
    

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)
