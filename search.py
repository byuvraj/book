import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('postgresql://postgres:yuvraJ@@localhost:5432/postgres')
db =  scoped_session(sessionmaker(bind=engine))

def search(name):
    name = '%'+name+'%'
    try:
        books_found1 = db.execute("SELECT id, isbn, title, author, year,rating FROM book WHERE title LIKE :name",{"name": name}).fetchall()
        books_found2 = db.execute("SELECT id, isbn, title, author, year,rating FROM book WHERE isbn LIKE :name",{"name": name}).fetchall()
        books_found3 = db.execute("SELECT id, isbn, title, author, year,rating FROM book WHERE author LIKE :name",{"name": name}).fetchall()
        if books_found1 is None and books_found2 is None and books_found3 is None:
            print("No book found")
    except ValueError:
        print ("No book found")
    books_found = books_found1 +books_found2 + books_found3  
    return books_found
if __name__ == "__main__":
    search(name = input("Type Title of book to search:\n"))