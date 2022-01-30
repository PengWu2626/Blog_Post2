from flask import Flask, render_template, g, current_app, request
import sqlite3
import datetime

app = Flask(__name__)

def get_message_db():
    """
    This function will handle creating the database of messages.

    Return
    ----------
    g.message_db: the connection for the database 'message_db'
    """
    # Check whether there is a database called message_db in the g attribute of the app
    if 'message_db' not in g:
        # if not, then connect to that database
        g.message_db = sqlite3.connect('messages_db.sqlite')
        
    # initialize our SQL database using Flask    
    # Check whether a table called messages exists in message_db, and create it if not
    # using the SQL command CREATE TABLE IF NOT EXISTS
    with current_app.open_resource('init.sql') as f:
        g.message_db.cursor().executescript(f.read().decode('utf8'))
    return g.message_db


def close_message_db(e=None):
    """
    This function will close the database connection
    """
    db = g.pop('message_db', None)

    if db is not None:
        db.close()


def insert_message(request):
    """
    This function will handle inserting a user message into the database of messages
    """
    # get the connection for our database
    db = get_message_db()
    # extract the message from request
    message = request.form['message']
    # extract the handle from request
    handle = request.form['handle']

    # make sure no empty strings
    if(message and handle):
        # using a cursor
        cursor = db.cursor()
        # insert the message into the message database
        cursor.execute(
            'INSERT INTO messages (message, handle) VALUES (?, ?)',
            (message, handle)
        )
    db.commit()
    #  close the database connection
    close_message_db()


def random_messages(n):
    """
    This function will return a collection of n random messages from the message_db
    Parameters
    ----------
    n: int; user-specified number of random messages
    
    Return
    ----------
    randommessages: list; list contains n random messages
    """ 
    # get the connection for our database 
    db = get_message_db()
    cursor = db.cursor()
    # get the list of n random messages by using SQL command
    randommessages = cursor.execute("SELECT message, handle FROM messages ORDER BY RANDOM() LIMIT '{}';".format(n)).fetchall()
    # close the database connection
    close_message_db()
    return randommessages


def all_messages():
    """
    This function will return all messages in the message bank.
    """
    db = get_message_db()
    cursor = db.cursor()
    # using SQL command to get all rows from our table
    allmessages = cursor.execute("SELECT * FROM messages").fetchall()
    return allmessages


# decorator
@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method == 'GET':
        return render_template('submit.html')
    else:
        insert_message(request)
        # extract the message from request
        message=request.form.get('message')
        # extract the handle from request
        handle=request.form.get('handle')
        # if user entered both message andhandle, then we add the current date information
        # need import datetime
        # then use function 'datetime.today()'
        if (message and handle):
            formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
            handle = "'" +handle + "' at " + formatted_date
        return render_template('submit.html',handle=handle)
        
# decorator
@app.route('/mydog/')
def mydog():
    return render_template('mydog.html')

# decorator
@app.route('/view/')
def view():
    return render_template('view.html', randmessages = random_messages(3))

# decorator
@app.route('/my_message_bank/')
def my_message_bank():
    return render_template('my_message_bank.html', allmessages = all_messages())
