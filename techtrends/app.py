import sqlite3
import logging
import sys
from datetime import datetime
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
conn_num = {'dbconnections': 0}
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    conn_num['dbconnections'] += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

def logInfo(msg):
    dateTime = datetime.now()
    timeStr = dateTime.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    logging.info(timeStr + " " + msg)

def logError(msg):
    dateTime = datetime.now()
    timeStr = dateTime.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    logging.error(timeStr + " " + msg)


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logError("A non-existing article is accessed.")
      return render_template('404.html'), 404
    else:
      logInfo("Article is accessed: " + post['title'])
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logInfo("The \"About Page\" is retrieved.")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logInfo("A new article is created: " + title)
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route("/healthz")
def health():
    return app.response_class(
        response=json.dumps({"result": "OK - Healthy"}),
        status=200,
        mimetype='application/json'
    )

@app.route("/metrics")
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    postsNumber = len(posts)
    connection.close()
    return app.response_class(
        response = json.dumps({"db_connecition_count": str(conn_num.get('dbconnections')), "post_count": postsNumber}),
        status=200,
        mimetype='application/json'
        )

# start the application on port 3111
if __name__ == "__main__":
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    format_output = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handlers = [stderr_handler, stdout_handler]
    logging.basicConfig(format=format_output, level=logging.DEBUG, handlers=handlers)
    app.run(host='0.0.0.0', port='3111')


