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
    
def getItemsAndUsers(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from items inner join posts on items.iid=posts.iid inner join user on user.uid=posts.uid''')
    return curs.fetchall()

def getUser(conn, uid):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from user where uid = %s''',[uid])
    return curs.fetchone()

def insertUserpass(conn, username, hashed):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''INSERT into userpass(username,hashed) VALUES(%s,%s)''',
                         [username, hashed])

def insertUser(conn, username, name, gradYear, dorm, email):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''insert into user(username,name,gradYear,dorm,email) values
                (%s,%s,%s,%s,%s)''',[username,name,gradYear,dorm,email])

def getUserByUsername(conn, username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from user where username = %s''', [username])
    return curs.fetchone()
    
def getUserPassword(conn, username):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select hashed from userpass where username = %s''', [username])
    return curs.fetchone()

def check1(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from userpass''')
    return curs.fetchone()

def insertNewItem(conn, item):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    print item
    curs.execute('''insert into items (description, price, availability,urgency, category, other, role) values 
                    (%s, %s,%s,%s,%s,%s,%s)''', [item['description'], item['price'],item['available'],item['urgency'], item['category'],item['other'],item['role']])

def getItemsForSale(conn):
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('''select * from items inner join posts on items.iid=posts.iid where items.role="seller"''')
    return curs.fetchall()
