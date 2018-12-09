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
    conn = sqlFunctions.getConn('c9')
    posts = sqlFunctions.getAvailableItemsAndUsers(conn)
    currentUser = ''
    if 'username' in session:
        currentUser = session['username']
    return render_template('main.html', posts = posts, currentUser = currentUser)

#register user and add them into the user database
@app.route('/register/', methods=['GET','POST'])
def register():
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
            user = sqlFunctions.getUserByUsername(conn, username)
            #create session for user
            session['username'] = username
            session['user'] = user
            session['logged_in'] = True
            session['visits'] = 1
            session.permanent= True
            return redirect( url_for('account',usernameInput=username) )
        except Exception as err:
            flash('form submission error '+str(err))
    return redirect(request.referrer)

#account page for user    
@app.route('/account/', defaults={'usernameInput':''}, methods=['POST','GET'])
@app.route('/account/<usernameInput>', methods=['POST','GET'])
def account(usernameInput):
    print request.method
    conn = sqlFunctions.getConn('c9')
    #check if user is in session
    try: 
        loggedIn = session['logged_in']
    except:
        loggedIn = None
    #show account page if user logged in, redirect to home otherwise
    if loggedIn:
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
            session['visits'] = 1
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

# renders all the posts with items for sale to html template
@app.route('/sale/')
def getSalePosts():
    conn = sqlFunctions.getConn('c9')
    # retrieves the posts from the database
    saleposts=sqlFunctions.getItemsForSale(conn, "seller")
    print saleposts
    currentUser = ''
    if 'username' in session:
        currentUser = session['username']
    return render_template('forsale.html', posts=saleposts, currentUser = currentUser)

@app.route('/blob/<iid>')
def blob(iid):
    conn = sqlFunctions.getConn('c9')
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    numrows = curs.execute('''select iid,photo from items
                            where iid = %s''', [iid])
    if numrows == 0:
        flash('No picture for item {}'.format(iid))
        return redirect(url_for('home'))
    row = curs.fetchone()
    photo = row['photo']
    print "photo info",len(photo),imghdr.what(None,photo)
    return Response(photo, mimetype='photo/'+imghdr.what(None,photo))
    
@app.route('/blobs/')
def blobs():
    conn = sqlFunctions.getConn('c9')
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select iid,photo from items')
    pics = curs.fetchall()
    print len(pics), 'found'
    return render_template('main.html',pics=pics)

"""
Handles the upload form submission
Retrieves inputs from the form and creates a dictionary that will be passed into
a function that extracts the different compenents to insert the item into the 
Items table
"""
@app.route('/upload/', methods=['GET','POST'])
def uploadPost():
    conn = sqlFunctions.getConn('c9')
    test = True
    if request.method == 'GET':
        return render_template('form.html')
    else:
        try:
            description = request.form.get('description')
            price = request.form.get('price')
            category = request.form.get('category')
            other = request.form.get('other')
            role = request.form.get('role')
            
            f = request.files['pic']
            fsize = os.fstat(f.stream.fileno()).st_size
            print 'file size is ',fsize
            
            if fsize > app.config['MAX_UPLOAD']:
                raise Exception('File is too big')
            mime_type = imghdr.what(f.stream)
            if mime_type not in ['jpeg','gif','png']:
                raise Exception('Not a JPEG, GIF or PNG: {}'.format(mime_type))
            photo = f.read()
            
            itemDict = {'description': description, 'price': price,
            'category': category, 'other': other, 'photo': photo, 'role': role}
            
            # below is to assign an item to a specific user
            # status = ('username' in session)
            # print status
            if 'user' in session:
                uid = session['user']
                sqlFunctions.insertNewItem(conn, itemDict) #add item to the database
                iid = sqlFunctions.getLatestItem(conn)
                iid = iid['last_insert_id()']
                sqlFunctions.insertNewPost(conn,uid,iid) #add uid and iid to post table
        except Exception as err:
            flash('form submission error '+str(err))
    return redirect(url_for('home'))

"""
Retrieves a post from the form 
and returns it in JSON format 
"""
@app.route('/retrievePost/', methods=['POST'])
def retrievePost():
    conn = sqlFunctions.getConn('c9')
    iid = request.form['iid']
    item = sqlFunctions.getItemByID(conn, iid)
    return jsonify(item)
    
"""
Handles updating the post
Takes inputs from the update posts form, updates the items,
and returns the item JSON formatted
"""
@app.route('/updatePost/', methods=['POST'])
def updatePost():
    conn = sqlFunctions.getConn('c9')
    try:
        iid = request.form['iid']
        if 'description' in request.form:
            sqlFunctions.updatePostDescription(conn, request.form['description'],iid)
        if 'price' in request.form:
            sqlFunctions.updatePostPrice(conn, request.form['price'],iid)
        if 'category' in request.form:
            sqlFunctions.updatePostCategory(conn, request.form['category'], iid)
        if 'other' in request.form:
            sqlFunctions.updatePostOther(conn, request.form['other'], iid)
        return jsonify(sqlFunctions.getItemByID(conn,iid))
    except:
        flash('Invalid item')
    return jsonify({})
 
"""
Deletes a post and returns
"""
@app.route('/deletePost/', methods=['POST'])
def deletePost():  
    conn = sqlFunctions.getConn('c9')
    sqlFunctions.deleteItem(conn,request.form['iid'])
    return jsonify(request.form['iid'])

@app.route('/markPostSold/', methods=['POST'])
def markPostSold():
    conn = sqlFunctions.getConn('c9')
    sqlFunctions.markPostSold(conn,request.form['iid'])
    return jsonify(request.form['iid'])
    

@app.route('/messageUser/',methods=['POST'])
def messageUser():
    conn = sqlFunctions.getConn('c9')
    print request.form
    messageID = None
    if 'user' in session:
        user = session['user']
        messageID = sqlFunctions.insertMessage(
            conn,user['uid'],request.form['uid'],request.form['iid'],
            request.form['description'])
    return jsonify(messageID)
    
@app.route('/userAndItemInfo/',methods=['POST'])
def getUserItemInfo():
    conn = sqlFunctions.getConn('c9')
    user = sqlFunctions.getUser(conn,request.form['uid'])
    item = sqlFunctions.getItemByID(conn,request.form['iid'])
    return jsonify({'user':user,'item':item})

@app.route('/openConversation/', methods=['POST'])
def openConversation():
    conn = sqlFunctions.getConn('c9')

@app.route('/sale/',methods=['GET','POST'])
def search():
    if request.method=="GET":
        return render_template('forsale.html')
    else:
        category=request.form.get('menu-category')
        # print category
        return redirect(url_for('searchCategory',category=category))

@app.route('/sale/<category>', methods=['GET','POST'])
def searchCategory(category):
    conn = sqlFunctions.getConn('c9')
    if request.method=="GET":
        cat=sqlFunctions.getItembyCategory(conn,category)
        if cat:
            return render_template('search.html',cat=cat,category=category)
        else:
            flash("There are no posts in this category")
            return redirect(request.referrer)
    
@app.route('/stringSearch/', methods=['POST'])
def stringSearch():
    conn=sqlFunctions.getConn('c9')
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
    app.run('0.0.0.0',8080)
