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

#get connection to c9 database
def getConn():
    return sqlFunctions.getConn('c9')

#homepage that renders all posts     
@app.route('/', methods=['GET','POST'])
def home():
    conn = getConn()
    posts = sqlFunctions.getItemsAndUsers(conn)
    return render_template('main.html', posts = posts)

#register user and add them into the user database
@app.route('/register/', methods=['GET','POST'])
def register():
    conn = getConn()
    if request.method == 'GET':
        return render_template('registration.html')
    else:
        try:
            #retrieve username and password
            username = request.form['username']
            passwd1 = request.form['password1']
            passwd2 = request.form['password2']
            #compare passwords and return error if they don't match
            if passwd1 != passwd2:
                flash('passwords do not match')
                return redirect(request.referrer)
            #hash the password
            hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
            #retrieve user from user table to see if user already exists 
            #return error if user exists
            row = sqlFunctions.getUserByUsername(conn, username)
            if row is not None:
                flash('That username is taken')
                return redirect( url_for('register') )
            #retrieve user input info
            name = request.form['name']
            gradYear = request.form['gradYear']
            email = request.form['email']
            dorm = request.form['dorm']
            #insert user into user table and password table
            sqlFunctions.insertUser(conn,username,name,gradYear,dorm,email)
            sqlFunctions.insertUserpass(conn,username,hashed)
            #create session for user
            session['username'] = username
            session['logged_in'] = True
            session['visits'] = 1
            session.permanent= True
            return redirect( url_for('account') )
        except Exception as err:
            flash('form submission error '+str(err))
    return redirect(request.referrer)

#account page for user    
@app.route('/account/', methods=['POST','GET'])
def account():
    conn = getConn()
    #check if user is in session
    try: 
        loggedIn = session['logged_in']
    except:
        loggedIn = None
    #show account page if user logged in, redirect to home otherwise
    if loggedIn:
        username = session['username']
        #retrieve posts by user
        user = sqlFunctions.getUserByUsername(conn,username)
        posts = sqlFunctions.getUserPosts(conn,user)
    else:
        flash('User not logged in')
        return redirect(url_for('home'))
    return render_template('account.html', person = user, posts = posts)

@app.route('/login/', methods=['POST'])
def login():
    conn = getConn()
    try:
        username = request.form['login_username']
        passwd = request.form['login_password']
        #retrieves the user's password from the database
        row = sqlFunctions.getUserPassword(conn,username)
        if row is None:
            # Same response as wrong password, so no information about what went wrong
            flash('No account for username. Try again with correct username')
            return redirect( url_for('home'))
        hashed = row['hashed']
        #compares the user's input to the hashed password
        if bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8')) == hashed:
            flash('successfully logged in as '+username)
            session['username'] = username
            session['logged_in'] = True
            session['visits'] = 1
            return redirect(request.referrer)
        else:
            flash('Wrong password. Please try again')
            return redirect( url_for('home'))
    except Exception as err:
        flash('form submission error '+str(err))
        return redirect( url_for('home') )   

@app.route('/logout/', methods=['POST'])
def logout():
    try:
        if 'username' in session:
            username = session['username']
            session.pop('username')
            session.pop('logged_in')
            flash('You are logged out')
            return redirect(request.referrer)
        else:
            flash('you are not logged in. Please login or join')
            return redirect(request.referrer)
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect(request.referrer)

# renders all the posts with items for sale to html template
@app.route('/sale/')
def getSalePosts():
    conn = getConn()
    # retrieves the posts from the database
    saleposts=sqlFunctions.getItemsForSale(conn, "seller")
    return render_template('forsale.html', saleposts=saleposts)

''' 
Handles the upload form submission
Retrieves inputs from the form and creates a dictionary that will be passed into
a function that extracts the different compenents to insert the item into the 
Items table
'''
@app.route('/upload/', methods=['GET','POST'])
def uploadPost():
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
            #below is for testing purposes
            item = description + "," + price + "," + available + "," + urgency + "," + category + "," + other + "," + role
            print item
            #below is to assign an item to a specific user -- not yet implemented
            # if 'username' in session:
            #     username = session['username']
            itemDict = {'description': description, 'price': price,
            'available': available, 'urgency': urgency, 'category': category, 'other': other, 'role': role}
            sqlFunctions.insertNewItem(conn, itemDict) #add item to the database
        except Exception as err:
            flash('form submission error '+str(err))
    posts = sqlFunctions.getItemsAndUsers(conn) #return to main page and pass in updated item list
    return render_template('main.html', posts = posts)

@app.route('/retrievePost/', methods=['POST'])
def retrievePost():
    conn = getConn()
    iid = request.form['iid']
    item = sqlFunctions.getItemByID(conn, iid)
    return jsonify(item)
    
#to be fleshed out
@app.route('/updatePost/', methods=['POST'])
def updatePost():
    conn = getConn()
    try:
        iid = request.form['iid']
        print request.form
        if 'description' in request.form:
            sqlFunctions.updatePostDescription(conn, request.form['description'],iid)
        if 'price' in request.form:
            sqlFunctions.updatePostPrice(conn, request.form['price'],iid)
        if 'avail' in request.form:
            sqlFunctions.updatePostAvailability(conn, request.form['availability'], iid)
        if 'urgency' in request.form:
            sqlFunctions.updatePostUrgency(conn, request.form['urgency'], iid)
        if 'category' in request.form:
            sqlFunctions.updatePostCategory(conn, request.form['category'].replace('-','/'), iid)
        if 'other' in request.form:
            sqlFunctions.updatePostOther(conn, request.form['other'], iid)
    except:
        flash('Invalid item')
    return redirect(request.referrer)
  
@app.route('/deletePost/', methods=['POST'])
def deletePost():  
    print request.form['id']
    return "hello"

@app.route('/sale/',methods=['GET','POST'])
def search():
    if request.method=="GET":
        return render_template('forsale.html')
    else:
        category=request.form.get('menu-category')
        print category
        return redirect(url_for('searchCategory',category=category))

@app.route('/sale/<category>', methods=['GET','POST'])
def searchCategory(category):
    conn = getConn()
    if request.method=="GET":
        cat=sqlFunctions.getItembyCategory(conn,category)
        if cat:
            return render_template('search.html',cat=cat,category=category)
        else:
            flash("There are no posts in this category")
            return redirect(request.referrer)
    
@app.route('/stringSearch/', methods=['POST'])
def stringSearch():
    conn=getConn()
    if request.method=="POST":
        searchWord = request.form.get('searchterm')
        # print searchWord
        keyword=sqlFunctions.partialDescription(conn,searchWord)
        if not keyword:
            flash("There is no post that matches this keyword.")
            return redirect(request.referrer)
        else:
            return render_template("search.html", cat=keyword)
if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8081)
