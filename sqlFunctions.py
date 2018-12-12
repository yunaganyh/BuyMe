#!/usr/bin/python2.7

import sys
import MySQLdb

# ================================================================

# return the connection to MySQLdb 
def getConn(db):
    conn = MySQLdb.connect(host='localhost',
                           user='ubuntu',
                           passwd='',
                           db=db)
    conn.autocommit(True)
    return conn

#joins the items and users tables based on uid    
def getAvailableItemsAndUsers(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select user.uid, user.username, user.name, items.iid, items.description, 
                    items.price, items.category, items.photo, items.other
                    from items inner join posts on items.iid=posts.iid 
                    inner join user on user.uid=posts.uid 
                    where posts.sold = true 
                    order by items.uploaded desc''')
    return curs.fetchall()

#get items for a specific user based on user uid
def getUserPosts(conn,uid, sold):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select items.description, items.price, items.category,
                    items.other, items.photo, items.iid 
                    from items inner join posts on items.iid=posts.iid 
                    where (posts.uid=%s and posts.sold=%s)''',[uid, sold])
    return curs.fetchall()
    
def getUser(conn, uid):
    """Get user info from user table based
    on user uid"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from user where uid = %s''',[uid])
    return curs.fetchone()

def insertUserpass(conn, username, hashed):
    """Inserts password for user"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''INSERT into userpass(username,hashed) VALUES(%s,%s)''',
                         [username, hashed])

def insertUser(conn, username, name, gradYear, dorm, email):
    """Insert user into user table"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into user(username,name,gradYear,dorm,email) values
                (%s,%s,%s,%s,%s)''',[username,name,gradYear,dorm,email])

def getUserByUsername(conn, username):
    """Get user info from user table based
    on user username"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from user where username = %s''', [username])
    return curs.fetchone()

def getUserPassword(conn, username):
    """Retrieve hashed user password"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select hashed from userpass where username = %s''', [username])
    return curs.fetchone()

def insertNewItem(conn, item):
    """Insert item into items table"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    # print item['photo']
    curs.execute('''insert into items (description, price,category, other, photo, role) values 
                    (%s,%s,%s,%s, %s,%s)''', 
                    [item['description'], item['price'], item['category'],
                    item['other'], item['photo'], item['role']])

def insertNewPost(conn,userDict,iid):
    """Insert item iid into posts table with
    corresponding uid"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    uid = userDict['uid']
    curs.execute('''insert into posts (uid,iid) values 
                    (%s,%s)''', [uid,iid])
    
def getItemsForSale(conn, role):
    """Retrieve items based on whether
    role is seller or buyer"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select items.*, posts.*,user.username, user.name,user.dorm 
                    from items inner join posts on items.iid=posts.iid 
                    inner join user on user.uid=posts.uid where items.role=%s''',[role])
    return curs.fetchall()

def getItemByID(conn, iid):
    """Get item by ID(iid)"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from items where iid=%s''',[iid])
    return curs.fetchone()

def getLatestItem(conn):
    """Get the last iid inserted into items table"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select last_insert_id() from items''')
    return curs.fetchone()
    
#delete post from posts table
def deletePost(conn, iid):
    """Delete post from post table"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''delete from posts where iid = %s''', [iid])
    
def deleteItem(conn, iid):
    """Delete item from items table"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''delete from items where iid = %s''', [iid])

def updatePostDescription(conn, description,iid):
    """Update posts with new description"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update items set description = %s where iid=%s''',[description,iid])
    
def updatePostPrice(conn, price, iid):
    """Update posts with new price"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update items set price = %s where iid=%s''',[price, iid])
    
def updatePostCategory(conn, category, iid):
    """Update posts with new category"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update items set category = %s where iid=%s''',[category, iid])

def updatePostOther(conn, other, iid):
    """Update posts with new other description"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update items set other = %s where iid=%s''',[other, iid])

#update posts with new photo
def updatePostPhoto(conn, photo, iid):
    """Update posts with new photo"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update items set photo = %s where iid=%s''',[photo,iid])
    
#insert message into message table
def insertMessage(conn, sender, receiver, iid, message):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into messages(sender,receiver, iid, message) 
                values (%s,%s,%s, %s)''',
                [sender,receiver, iid,message])
    curs.execute('''select distinct last_insert_id() from messages''')
    return curs.fetchone()

def retrieveItemsToSellMessageForUser(conn,uid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select distinct messages.receiver, messages.sender, 
                    messages.iid, items.description, user.name, user.username, user.uid 
                    from messages inner join items on messages.iid = items.iid
                    inner join user on user.uid = messages.sender
                    where receiver = %s''',[uid])
    return curs.fetchall()
    
def retrieveItemsToBuyMessageForUser(conn,uid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select distinct messages.receiver, messages.sender, 
                    messages.iid, items.description, user.name, user.username, user.uid
                    from messages inner join items on messages.iid = items.iid
                    inner join user on user.uid = messages.receiver 
                    where sender = %s''',[uid])
    return curs.fetchall()
    
def markPostSold(conn, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update posts set sold = 'true' where iid = %s''',[iid])
    
def getMessageInfo(conn, uid, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)

def getItembyCategory(conn,category):
    """Gets items based on specified category"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select items.*, posts.*,user.name,user.dorm from items inner 
    join posts on items.iid=posts.iid inner join user on user.uid=posts.uid where
    (category=%s and posts.sold = true)''',[category])
    return curs.fetchall()
    
def partialDescription(conn,keyword):
    """Gets items based on partial string search term"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor) # SQL query from wmdb, to get id's movies
    word = "%" + keyword +"%"
    curs.execute('''select items.*, posts.*,user.username,user.name from items inner join posts on items.iid=posts.iid inner join user on user.uid=posts.uid where description like %s''',[word])
    results= curs.fetchall()
    return results

