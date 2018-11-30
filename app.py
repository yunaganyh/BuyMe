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
    
    
@app.route('/login/')
def login():
    conn = getConn()
    
@app.route('/upload/', methods=['GET','POST'])
def uploadpost():
    conn = getConn()
    test = True
    if request.method == 'GET':
        return render_template('form.html')
    else:
        try:
            description = request.form.get('description')
            price = request.form.get('price')
            available = request.form.get('avail')
            urgency = request.form.get('urgency')
            category = request.form.get('category')
            other = request.form.get('other')
            role = request.form.get('role')
            item = description + "," + price + "," + available + "," + urgency + "," + category + "," + other + "," + role
            print item
            # if 'username' in session:
            #     username = session['username']
            itemDict = {'description': description, 'price': price,
            'available': available, 'urgency': urgency, 'category': category, 'other': other, 'role': role}
            sqlFunctions.insertNewItem(conn, itemDict)
            
        except Exception as err:
            flash('form submission error '+str(err))
    return redirect(request.referrer)

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)
