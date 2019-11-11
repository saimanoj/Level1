import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import User, Item, Base

engine = create_engine('sqlite:///fm.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(user_name="user1", pass_word="user1")
User2 = User(user_name="user2", pass_word="user2")
User3 = User(user_name="user3", pass_word="user3")
session.add(User1)
session.add(User2)
session.add(User3)
session.commit()


filename = "test.csv"

rows = [] 
  
with open(filename, 'r') as csvfile: 
    csvreader = csv.reader(csvfile) 
  
    for row in csvreader: 
        rows.append(row) 

for row in rows[1:]:
	if row[8] == 'User 1':
		user_id = 1
	elif row[8] == 'User 2':
		user_id = 2
	else:
		user_id = 3

	vendor = Item(product_id=row[0], product_name=row[1], weave=row[2], composition=row[3], 
						color=row[4], category_1=row[5], category_2=row[6], category_3=row[7], user_id= user_id)
	session.add(vendor)
	session.commit()