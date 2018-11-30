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
def getItemsAndUsers(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from items inner join posts on items.iid=posts.iid 
    inner join user on user.uid=posts.uid''')
    return curs.fetchall()

#get items for a specific user based on user uid
def getUserPosts(conn,user):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from items inner join posts on items.iid=posts.iid 
    where posts.uid=%s''',[user['uid']])
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
    # print item
    curs.execute('''insert into items (description, price, availability,urgency, category, other, role) values 
                    (%s, %s,%s,%s,%s,%s,%s)''', [item['description'], item['price'],item['available'],item['urgency'], item['category'],item['other'],item['role']])

#retrieve items based on whether role is seller or buyer
def getItemsForSale(conn, role):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from items inner join posts on items.iid=posts.iid where items.role=%s''',[role])
    return curs.fetchall()
