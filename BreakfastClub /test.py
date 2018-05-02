import sqlite3

connection = sqlite3.connect('test6.db')

cur = connection.cursor()
# Create table if it doesn't alread exist
#users
cur.execute("CREATE TABLE IF NOT EXISTS users (userId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,name varchar(100) DEFAULT NULL,email varchar(100) DEFAULT NULL,username varchar(30) DEFAULT NULL,password varchar(100) DEFAULT NULL,register_date timestamp NOT NULL DEFAULT (datetime('now', 'localtime')))")
# members
cur.execute("CREATE TABLE IF NOT EXISTS members (clientId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name varchar(50) NOT NULL, author varchar(50) DEFAULT NULL, creationDate timestamp NOT NULL DEFAULT (datetime('now', 'localtime')))")
# visits
cur.execute("CREATE TABLE IF NOT EXISTS visits (visitId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,clientId int(11) DEFAULT NULL,breakfastDate timestamp NOT NULL DEFAULT (datetime('now', 'localtime')),author varchar(50) DEFAULT NULL, FOREIGN KEY(clientId) REFERENCES members(clientId))")
# redeem
cur.execute("CREATE TABLE IF NOT EXISTS redeem (redeemId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,clientId int(11) DEFAULT NULL,redeemDate timestamp NOT NULL DEFAULT (datetime('now', 'localtime')),author varchar(50) DEFAULT NULL,redeem tinyint(1) NOT NULL DEFAULT '0', FOREIGN KEY(clientId) REFERENCES members(clientId))")


#Insert into members, visits and redeem
#users
cur.execute("INSERT OR REPLACE into users(name, email, username, password) values('users name', 'email@hotmail.com', 'username', 'password')")
#members
cur.execute("INSERT OR REPLACE into members(name) values('member name')")
#visits
cur.execute("INSERT OR REPLACE into visits(author) values('visit author')")
#redeem
cur.execute("INSERT OR REPLACE into redeem(author) values('redeem author')")

#Select values
#users
cur.execute("SELECT * from users")
#members
#cur.execute("SELECT * from members")
#visits
##redeem
#cur.execute("SELECT * from redeem")

#Special Lines



connection.commit()

rows = cur.fetchall()

for row in rows:
    print(row)

connection.close()
