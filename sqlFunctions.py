#!/usr/bin/python2.7

import sys
import MySQLdb

# ================================================================

# return the connection to MySQLdb 
def getConn(db):
    conn = MySQLdb.connect(host='localhost',
                           user='kealani',
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
                    where (posts.uid=%s and posts.sold=%s) 
                    order by items.uploaded desc''',[uid, sold])
    return curs.fetchall()
    
def getUser(conn, uid):
    """Get user info from user table based
    on user uid"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from user where uid = %s''',[uid])
    return curs.fetchone()

# def insertUserpass(conn, username, hashed):
#     """Inserts password for user"""
#     curs = conn.cursor(MySQLdb.cursors.DictCursor)
#     curs.execute('''INSERT into userpass(username,hashed) VALUES(%s,%s)''',
#                          [username, hashed])

def insertUser(conn, obj, hashed):
    """Insert user into user table"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into user(username,name,gradYear,dorm,email) values
                (%s,%s,%s,%s,%s)''',
                [obj['username'],obj['name'],obj['gradYear'],obj['dorm'],obj['email']])
    curs.execute('''INSERT into userpass(username,hashed) VALUES(%s,%s)''',
                [obj['username'], hashed])

# def getLastInsert(conn):
#     curs = conn.cursor(MySQLdb.cursors.DictCursor)
#     curs.execute('''select last_insert_id()''')
#     return curs.fetchone()

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
    curs.execute('''insert into items (description, price,category, other, photo, role) values 
                    (%s,%s,%s,%s, %s,%s)''', 
                    [item['description'], item['price'], item['category'],
                    item['other'], item['photo'], item['role']])
    curs.execute('''select last_insert_id()''')
    iid = curs.fetchone()
    return (iid['last_insert_id()'])

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
    curs.execute('''select items.iid, items.description,items.price,
                    items.category,items.other,items.role, posts.*,user.username, user.name,user.dorm 
                    from items inner join posts on items.iid=posts.iid 
                    inner join user on user.uid=posts.uid where items.role=%s
                    order by items.uploaded desc''',[role])
    return curs.fetchall()

def getItemByID(conn, iid):
    """Get item by ID(iid)"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select iid,description,price,category,other,role from items where iid=%s''',[iid])
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

def updatePost(conn, description, price, category, other, iid):
    """updates post with new values from update post form"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update items set description = %s, price = %s,
                    category=%s, other=%s where iid=%s''',
                    [description, price, category, other, iid])

#insert message into message table
def insertMessage(conn, sender, receiver, iid, message):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into messages(sender,receiver, iid, message) 
                values (%s,%s,%s, %s)''',
                [sender,receiver,iid,message])
    curs.execute('''select last_insert_id()''')
    return curs.fetchone()

def retrieveItemsToSellMessageForUser(conn,uid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select username, name, user.uid, 
                    B.message, B.sender,B.receiver,B.iid,items.description
                    from user inner join 
                    (select message, sender, receiver, messages.iid as iid from messages 
                    inner join posts on posts.iid=messages.iid 
                    where (posts.uid != sender and posts.sold='false' and receiver = %s) 
                    group by messages.iid, messages.sender) 
                    as B on user.uid = B.sender inner join items on items.iid = B.iid 
                    order by items.uploaded desc''',[uid])
    return curs.fetchall()
    
def retrieveItemsToBuyMessageForUser(conn,uid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select username, name, user.uid, B.message, B.sender,
                    B.receiver,B.iid, items.description 
                    from user inner join 
                    (select message, sender, receiver, messages.iid as iid from messages 
                    inner join posts on posts.iid=messages.iid 
                    where (posts.uid != sender and posts.sold='false' and sender = %s) 
                    group by messages.iid, messages.receiver) 
                    as B on user.uid = B.receiver inner join items on items.iid = B.iid 
                    order by items.uploaded desc''',[uid])
    return curs.fetchall()

def retrieveMessages(conn, sender, receiver, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select sender, receiver, iid, message, messageSent,username,uid 
                from messages 
                inner join user on (uid=sender) 
                where (((sender = %s and receiver = %s) or (sender=%s and receiver=%s)) 
                and iid=%s)
                order by messageSent asc''', [sender,receiver,receiver,sender,iid])
    return curs.fetchall()
    
def markPostSold(conn, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update posts set sold = 'true' where iid = %s''',[iid])

def getItemByCategoryRole(conn,category, role):
    """Gets items based on specified category"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select items.description, items.price, items.iid, 
                items.category, items.other, posts.*,user.name, user.username
                from items inner join posts on items.iid=posts.iid 
                inner join user on user.uid=posts.uid 
                where (category=%s and posts.sold=true and items.role = %s)
                order by items.uploaded desc''',
                [category, role])
    return curs.fetchall()
    
def partialDescription(conn,keyword):
    """Gets items based on partial string search term"""
    curs = conn.cursor(MySQLdb.cursors.DictCursor) # SQL query from wmdb, to get id's movies
    word = "%" + keyword +"%"
    curs.execute('''select items.iid,items.description,items.price,items.category,
                    items.other,items.role, posts.*,user.username,user.name 
                    from items inner join posts on items.iid=posts.iid 
                    inner join user on user.uid=posts.uid 
                    where (description like %s and posts.sold = true)
                    order by items.uploaded desc''',[word])
    results= curs.fetchall()
    return results

