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

#get user info from user table based on user uid    
def getUser(conn, uid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from user where uid = %s''',[uid])
    return curs.fetchone()

#insert password for user
def insertUserpass(conn, username, hashed):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''INSERT into userpass(username,hashed) VALUES(%s,%s)''',
                         [username, hashed])

#insert user into user table
def insertUser(conn, username, name, gradYear, dorm, email):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into user(username,name,gradYear,dorm,email) values
                (%s,%s,%s,%s,%s)''',[username,name,gradYear,dorm,email])

#get user info from user table based on user username
def getUserByUsername(conn, username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from user where username = %s''', [username])
    return curs.fetchone()

#retrieve hashed user password    
def getUserPassword(conn, username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select hashed from userpass where username = %s''', [username])
    return curs.fetchone()

#insert item into items table
def insertNewItem(conn, item):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into items (description, price,category, other, role) values 
                    (%s,%s,%s,%s,%s)''', 
                    [item['description'], item['price'], item['category'],
                    item['other'],item['role']])

def insertNewPost(conn,userDict,iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    uid = userDict['uid']
    iid = iid['max(iid)']
    curs.execute('''insert into posts (uid,iid) values 
                    (%s,%s)''', [uid,iid])
    
#retrieve items based on whether role is seller or buyer
def getItemsForSale(conn, role):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select items.*,posts.* from items inner join posts on items.iid=posts.iid where items.role=%s''',[role])
    return curs.fetchall()

#get item by ID:
def getItemByID(conn, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from items where iid=%s''',[iid])
    return curs.fetchone()

def getLatestItem(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select max(iid) from items''')
    return curs.fetchone()
    
def deleteItem(conn, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''delete from items where iid=%s''',[iid])
    
#delete post from posts table
def deletePost(conn, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''delete from posts where iid = %s''', [iid])

#update posts with new description
def updatePostDescription(conn, description,iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update items set description = %s where iid=%s''',[description,iid])
    
#update posts with new price
def updatePostPrice(conn, price, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update items set price = %s where iid=%s''',[price, iid])
#update posts with new category
def updatePostCategory(conn, category, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update items set category = %s where iid=%s''',[category, iid])

#update posts with new other description
def updatePostOther(conn, other, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update items set other = %s where iid=%s''',[other, iid])

#update posts with new photo
def updatePostPhoto(conn, photo, iid):
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
    curs.execute('''select distinct receiver, sender, iid from messages where receiver = %s''',[uid])
    distinctMessages = curs.fetchall()
    print distinctMessages
    for i in distinctMessages:
        curs.execute('''select distinct items.description from items inner join messages 
                        where (items.iid = messages.iid and items.iid = %s)''',
                        [i['iid']])
        i['description'] = curs.fetchone()['description']
        sender = getUser(conn, i['sender'])
        i['name'] = sender['name']
        i['username'] = sender['username']
    print 'MESSAGES RECEIVED'
    print distinctMessages
    return distinctMessages
    
def retrieveItemsToBuyMessageForUser(conn,uid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select distinct receiver, sender, iid from messages where sender = %s''',[uid])
    distinctMessages = curs.fetchall()
    print distinctMessages
    for i in distinctMessages:
        curs.execute('''select distinct items.description from items inner join messages 
                        where (items.iid = messages.iid and items.iid = %s)''',
                        [i['iid']])
        i['description'] = curs.fetchone()['description']
        receiver = getUser(conn, i['receiver'])
        i['name'] = receiver['name']
        i['username'] = receiver['username']
    print 'MESSAGES SENT'
    print distinctMessages
    return distinctMessages
    
def markPostSold(conn, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''update posts set sold = 'true' where iid = %s''',[iid])
    
def getMessageInfo(conn, uid, iid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)