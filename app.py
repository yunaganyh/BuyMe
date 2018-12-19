from flask import (Flask, url_for, render_template, request, session, redirect, 
                   flash, jsonify, send_from_directory, make_response, Response)
import random, math
import MySQLdb
import sys,os
from werkzeug import secure_filename
import bcrypt
import sqlFunctions
import imghdr
import time
from datetime import datetime, timedelta
app = Flask(__name__)

app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])
                           
# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

app.config['UPLOADS'] = 'uploads'
app.config['MAX_UPLOAD'] = 260000

                           
#homepage that renders all posts     
@app.route('/', methods=['GET','POST'])
def home():
    """Displays all available posts and actionable buttons."""
    conn = sqlFunctions.getConn('c9')
    posts = sqlFunctions.getAvailableItemsAndUsers(conn)
    currentUser = session.get('username')
    print currentUser
    return render_template('main.html', posts = posts, currentUser = currentUser)

@app.route('/register/', methods=['GET','POST'])
def register():
    """Register a new user and requires a unique username."""
    conn = sqlFunctions.getConn('c9')
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
            #retrieve user from user table to see if user already exists 
            #return error if user exists
            try:
                #hash the password
                hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
                #insert user into user table and password table
                sqlFunctions.insertUser(conn,request.form, hashed)
            except MySQLdb.IntegrityError:
                flash('User already exists.')
                return redirect( url_for('register') )
            user = sqlFunctions.getUserByUsername(conn, username)
            #create session for user
            session['username'] = username
            session['user'] = user
            session['logged_in'] = True
            session.permanent= True
            return redirect( url_for('account',usernameInput=username) )
        except Exception as err:
            flash('form submission error '+str(err))
    return redirect(request.referrer)

@app.route('/account/', defaults={'usernameInput':''}, methods=['POST','GET'])
@app.route('/account/<usernameInput>', methods=['POST','GET'])
def account(usernameInput):
    """Shows a user's information and available and sold posts. If the user
    trying to look at the page is the owner of the account, then the user's
    messages and options to update, delete, and mark a post as sold is shown."""
    conn = sqlFunctions.getConn('c9')
    #check if user is in session
    if session.get('username'):
        #show account page if user logged in, redirect to home otherwise
        username = session['username']
        #retrieve posts by user
        if usernameInput == '':
            return redirect(url_for('account',usernameInput=username))
        if username == usernameInput:
            user = session['user']
            isUser = True
        elif username != usernameInput and usernameInput != '':
            user = sqlFunctions.getUserByUsername(conn, usernameInput)
            isUser = False
        availablePosts = sqlFunctions.getUserPosts(conn, user['uid'],'false')
        soldPosts = sqlFunctions.getUserPosts(conn,user['uid'],'true')
        itemsToBuyMessages = sqlFunctions.retrieveItemsToBuyMessageForUser(conn,user['uid'])
        itemsToSellMessages = sqlFunctions.retrieveItemsToSellMessageForUser(conn,user['uid'])
        return render_template('account.html', 
                                person = user, availablePosts = availablePosts,
                                soldPosts = soldPosts, itemsToBuyMessages = itemsToBuyMessages,
                                itemsToSellMessages = itemsToSellMessages,
                                isUser = isUser)
    else:
        flash('User not logged in')
        return redirect(url_for('home'))

@app.route('/login/', methods=['POST'])
def login():
    conn = sqlFunctions.getConn('c9')
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
            user = sqlFunctions.getUserByUsername(conn, username)
            session['user'] = user
            session['username'] = username
            session['logged_in'] = True
            session.permanent = True
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
            session.pop('username')
            session.pop('logged_in')
            session.pop('user')
            flash('You are logged out')
            return redirect(request.referrer)
        else:
            flash('you are not logged in. Please login or join')
            return redirect(request.referrer)
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect(request.referrer)

#returns images to display on items for sale
@app.route('/blob/<iid>')
def blob(iid):
    conn = sqlFunctions.getConn('c9')
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    numrows = curs.execute('''select iid,photo from items
                            where iid = %s''', [iid])
    row = curs.fetchone()
    photo = row['photo']
    #specifies a default image if there is no image uploaded by the user
    if photo is None:
        return send_from_directory('static','noPic.png')
    return Response(photo, mimetype='photo/'+imghdr.what(None,photo))
    
@app.route('/upload/', methods=['GET','POST'])
def uploadPost():
    """Handles the upload form submission
    Retrieves inputs from the form and creates a dictionary that will be passed into
    a function that extracts the different compenents to insert the item into the 
    Items table"""
    test = True
    if request.method == 'GET':
        return render_template('form.html')
    else:
        try:
            conn = sqlFunctions.getConn('c9')
            description = request.form.get('description')
            price = request.form.get('price')
            category = request.form.get('category')
            other = request.form.get('other')
            role = request.form.get('role')
            photo = ""
            itemDict = {}
            #first check is a picture is uploaded before formatting it
            if 'pic' not in request.files:
                photo = None
                itemDict = {'description': description, 'price': price,
                'category': category, 'other': other, 'photo': photo, 'role': role}
            else :
                f = request.files['pic']
                fsize = os.fstat(f.stream.fileno()).st_size
                if fsize > app.config['MAX_UPLOAD']:
                    raise Exception('File is too big')
                mime_type = imghdr.what(f.stream)
                if mime_type not in ['jpeg','gif','png']:
                    raise Exception('Not a JPEG, GIF or PNG: {}'.format(mime_type))
                photo = f.read()
                
                itemDict = {'description': description, 'price': price,
                'category': category, 'other': other, 'photo': photo, 'role': role}
            
            # assign an item to a specific user in posts table
            if 'user' in session:
                uid = session['user']
                iid = sqlFunctions.insertNewItem(conn, itemDict)
                sqlFunctions.insertNewPost(conn,uid,iid) 
        except Exception as err:
            flash('form submission error '+str(err))
            flash('please fill out all entries')
            return render_template('form.html')
    return redirect(url_for('home'))

@app.route('/retrievePost/', methods=['POST'])
def retrievePost():
    """Retrieves a post from the form and returns it in JSON format for an ajax callback.
    Executed when user clicks on a post in their account page to update it.
    The item info is sent back to fill out the update post form."""
    conn = sqlFunctions.getConn('c9')
    iid = request.form['iid']
    item = sqlFunctions.getItemByID(conn, iid)
    return jsonify(item)
    
@app.route('/updatePost/', methods=['POST'])
def updatePost():
    """Handles updating the post
    Takes inputs from the update posts form, updates the items,
    and returns the item JSON formatted"""
    conn = sqlFunctions.getConn('c9')
    try:
        iid = request.form['iid']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        other = request.form['other']
    except:
        return {'Did not have all required fields.'}
    if category != "other":
        other = ''
    sqlFunctions.updatePost(conn, description, price, category, other, iid)
    return jsonify(sqlFunctions.getItemByID(conn,iid))
 
@app.route('/deletePost/', methods=['POST'])
def deletePost():  
    """Deletes a post and returns"""
    conn = sqlFunctions.getConn('c9')
    sqlFunctions.deleteItem(conn,request.form['iid'])
    return jsonify(request.form['iid'])

@app.route('/markPostSold/', methods=['POST'])
def markPostSold():
    """Mark a post as sold on the account page and moves it from the list of 
    available posts to the list of sold posts."""
    conn = sqlFunctions.getConn('c9')
    sqlFunctions.markPostSold(conn,request.form['iid'])
    return jsonify(request.form['iid'])
    

@app.route('/messageUser/',methods=['POST'])
def messageUser():
    """Send a message to a user about the post in the table."""
    conn = sqlFunctions.getConn('c9')
    messageID = 0
    if 'user' in session:
        user = session['user']
        messageID = sqlFunctions.insertMessage(
            conn,user['uid'],request.form['uid'],request.form['iid'],
            request.form['description'])
    return jsonify(messageID)
    
@app.route('/userAndItemInfo/',methods=['POST'])
def getUserItemInfo():
    """Returns user and item information as a json object."""
    conn = sqlFunctions.getConn('c9')
    user = sqlFunctions.getUser(conn,request.form['uid'])
    item = sqlFunctions.getItemByID(conn,request.form['iid'])
    return jsonify({'uid':user['uid'],'username':user['username'],
                    'iid':item['iid'],'description':item['description']})

@app.route('/sale/', defaults ={'category':''}, methods=['GET','POST'])
@app.route('/sale/<category>', methods=['GET','POST'])
def getSalePosts(category):
    conn = sqlFunctions.getConn('c9')
    if request.method=="POST":
        category=request.form.get('menu-category')
        return redirect(url_for('getSalePosts',category=category))
    currentUser = ''
    if 'username' in session:
        currentUser = session['username']
    if category:
        cat=sqlFunctions.getItemByCategoryRole(conn,category,'seller')
        if cat:
            return render_template('search.html',
                                    posts=cat,category=category + ' (for sale)', 
                                    currentUser = currentUser)
        else:
            flash("There are no posts in this category")
    posts = sqlFunctions.getItemsForSale(conn,"seller")
    return render_template('search.html',
                            posts=posts,category='', 
                            currentUser = currentUser)

@app.route('/buy/', defaults ={'category':''}, methods=['GET','POST'])
@app.route('/buy/<category>', methods=['GET','POST'])
def getBuyPosts(category):
    """"renders all the posts with items for buy 
    (items users are looking for) to html template"""
    conn = sqlFunctions.getConn('c9')
    if request.method=="POST":
        category=request.form.get('menu-category')
        return redirect(url_for('getBuyPosts',category=category))
    currentUser = ''
    # retrieves the posts from the database
    if 'username' in session:
        currentUser = session['username']
    if category:
        buyposts=sqlFunctions.getItemByCategoryRole(conn,category,'buyer')
        if buyposts:
            return render_template('search.html',
                                    posts=buyposts,category=category + ' (requested)', 
                                    currentUser = currentUser)
        else:
            flash("There are no posts in this category")
    posts = sqlFunctions.getItemsForSale(conn,"buyer")
    return render_template('search.html',
                            posts=posts,category='Items Requested', 
                            currentUser = currentUser)
  
@app.route('/stringSearch/', defaults={'searchWord':''}, methods=['GET','POST'])   
@app.route('/stringSearch/<searchWord>', methods=['GET','POST'])
def stringSearch(searchWord):
    conn=sqlFunctions.getConn('c9')
    if request.method=="POST":
        searchWord = request.form.get('searchterm')
        return redirect(url_for('stringSearch',searchWord=searchWord))#   e1
    results=sqlFunctions.partialDescription(conn,searchWord)
    if not results:
            flash("There is no post that matches this keyword.")
            return redirect(url_for('getSalePosts'))
    else:
        return render_template("search.html", posts=results)
          
@app.route('/retrieveMessages/', methods=['POST'])
def retrieveMessages():
    """Retrieves messages between a sender and receiver about a unique item."""
    conn = sqlFunctions.getConn('c9')
    if session.get('user'):
        uid = session['user']['uid']
        convoHolder = request.form['uid']
        iid = request.form['iid']
        messages = sqlFunctions.retrieveMessages(conn, uid, convoHolder, iid)
        return jsonify({'messages':messages, 'sender':request.form['sender']})
    else:
        return jsonify('user not in session.')

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8080)
