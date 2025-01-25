from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'mind_reader'  # Needed for session management

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        # Save the name in the database
        conn = sqlite3.connect('mind_reader.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        # Store the name in the session
        session['player_name'] = name
        return redirect(url_for('games'))
    return render_template('index.html')

# Route for the game page
@app.route('/games', methods=['GET'])
def games():
    player_name = request.args.get('player_name')  # Get the player name from the URL query string
    return render_template('game_page.html', name=player_name)

# Route to handle feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    name = session.get('player_name', 'Player')  # Retrieve name from session
    rating = int(request.form['rating'])
    comment = request.form['comment']
    # Save feedback in the database
    conn = sqlite3.connect('mind_reader.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (name, rating, comment) VALUES (?, ?, ?)', (name, rating, comment))
    conn.commit()
    conn.close()
    return render_template('thankyou.html', name=name)


@app.route('/magic_ball')
def magic_ball():
    return render_template('index2.html')

@app.route('/language_find')
def language_find():
    return render_template('language_finder.html')

@app.route('/number_reader')
def number_reader():
    return render_template('number_reader.html')

# Database setup
def setup_database():
    conn = sqlite3.connect('mind_reader.db')
    cursor = conn.cursor()
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT
        )
    ''')
    conn.commit()
    conn.close()

setup_database()

@app.route('/feedback_form', methods=['GET'])
def feedback_form():
    name = session.get('player_name', 'Player')  # Retrieve name from session
    return render_template('feedback.html', name=name)

@app.route('/store_name', methods=['POST'])
def store_name():
    player_name = request.form['name']
    
    # Save the name in the database
    conn = sqlite3.connect('mind_reader.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name) VALUES (?)', (player_name,))
    conn.commit()
    conn.close()
    
    return '', 200  # Respond with a success status

if __name__ == '__main__':
    app.run(debug=True)
