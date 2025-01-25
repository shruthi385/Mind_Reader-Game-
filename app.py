from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import random
import cv2
import base64
from flask import request

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
    if player_name:
        session['player_name'] = player_name  # Store the player name in the session
    return render_template('game_page.html', name=player_name)


# Route to handle feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    name = session.get('player_name', 'Player')  # Retrieve name from session
    rating = int(request.form['rating'])  # Get the rating from the form
    comment = request.form['comment']
    # Save feedback in the database
    conn = sqlite3.connect('mind_reader.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO feedback (name, rating, comment) VALUES (?, ?, ?)', (name, rating, comment))
    conn.commit()
    conn.close()
    return redirect(url_for('thank_you'))  # Redirect to the thank you page

@app.route('/thank_you')
def thank_you():
    name = session.get('player_name', 'Player')  # Retrieve the name from session
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


#face reader -- starts---
# Ensure the images directory exists
if not os.path.exists('static/images'):
    os.makedirs('static/images')

# Random messages based on emotion
emotion_messages = {
   "happy": [
        "Your mind is glowing with thoughts of joy and success.",
        "You’re savoring a moment that brings a warm smile to your face.",
        "You’re thinking about the little things that make life beautiful.",
        "You feel lighthearted, as if nothing can weigh you down today.",
        "Your thoughts are filled with gratitude and laughter."
    ],
    "sad": [
        "Your mind keeps revisiting moments that bring a tinge of pain.",
        "You’re reflecting on something you wish had turned out differently.",
        "Your heart feels heavy, and your mind is searching for comfort.",
        "You’re thinking about the times that brought tears to your eyes.",
        "You’re longing for something or someone that’s missing in your life."
    ],
    "angry": [
        "Your mind is replaying moments of frustration and conflict.",
        "You’re thinking about what went wrong and how it could have been avoided.",
        "Your thoughts are burning with a desire to set things right.",
        "You feel a storm brewing inside, and your mind is trying to calm it.",
        "You’re determined to stand up for what you believe in."
    ],
    "neutral": [
        "Your mind is in a state of calm, observing without judgment.",
        "You’re thinking about the day ahead with no particular emotion.",
        "You feel steady and balanced, just going with the flow.",
        "Your thoughts are clear, like a still lake reflecting the sky.",
        "You’re neither elated nor downcast—just present in the moment."
    ],
    "excited": [
        "Your mind is buzzing with anticipation and energy!",
        "You’re thinking about all the possibilities that lie ahead.",
        "You can’t wait to dive into what’s coming next.",
        "Your thoughts are racing with enthusiasm and joy.",
        "You’re brimming with excitement for something special."
    ],
    "surprised": [
        "Your mind is caught off guard, trying to process the unexpected.",
        "You’re replaying that surprising moment over and over again.",
        "Your thoughts are filled with wonder and amazement.",
        "You’re thinking, ‘Wow, I didn’t see that coming!’",
        "Your curiosity is sparked by an unexpected twist."
    ],
    "confused": [
        "Your mind is tangled in a web of unanswered questions.",
        "You’re thinking, ‘This doesn’t quite make sense yet.’",
        "You’re trying to piece together the puzzle in front of you.",
        "Your thoughts feel scattered, like leaves in the wind.",
        "You’re searching for clarity amidst the uncertainty."
    ],
    "hopeful": [
        "Your mind is focused on brighter days ahead.",
        "You’re thinking about the possibilities that the future holds.",
        "You feel a sense of optimism growing within you.",
        "Your thoughts are full of dreams and aspirations.",
        "You’re visualizing success and happiness for yourself."
    ],
    "grateful": [
        "Your mind is filled with appreciation for the blessings in your life.",
        "You’re thinking about the people who make your life special.",
        "Your heart feels warm as you count your blessings.",
        "You’re reflecting on all the good things you’ve been given.",
        "You’re thinking, ‘I’m so lucky to have this.’"
    ],
    "fearful": [
        "Your mind is racing with ‘what ifs’ and uncertainties.",
        "You’re thinking about what could go wrong, and it’s holding you back.",
        "Your thoughts are clouded with worry and doubt.",
        "You’re bracing yourself for something you hope won’t happen.",
        "You’re trying to push past the fear that grips your mind."
    ],
    "loving": [
        "Your mind is filled with thoughts of care and affection.",
        "You’re thinking about the people who mean the world to you.",
        "Your heart is brimming with warmth and connection.",
        "You’re cherishing the bonds that make life meaningful.",
        "You’re thinking, ‘Love truly makes everything better.’"
    ],
    "bored": [
        "Your mind is wandering, searching for something to engage with.",
        "You’re thinking, ‘Isn’t there something more interesting to do?’",
        "Your thoughts are restless, craving excitement or a challenge.",
        "You feel stuck in a loop, wishing for something new.",
        "You’re looking for a spark to break the monotony."
    ],
    "curious": [
        "Your mind is bursting with questions you can’t wait to explore.",
        "You’re thinking, ‘I wonder how that works!’",
        "You’re eager to dive deeper into the unknown.",
        "Your curiosity is pulling you toward new discoveries.",
        "You’re hungry for knowledge and insight."
    ],
    "ashamed": [
        "Your mind is replaying moments you wish you could undo.",
        "You’re thinking about what went wrong and how you could’ve done better.",
        "You feel a pang of regret over something in your past.",
        "Your thoughts are clouded with self-criticism and remorse.",
        "You’re determined to learn and grow from your mistakes."
    ],
    "lonely": [
        "Your mind is longing for connection and companionship.",
        "You’re thinking, ‘I wish I had someone to share this moment with.’",
        "You feel a quiet ache for the presence of others.",
        "Your thoughts are dwelling on times when you felt more connected.",
        "You’re hoping for a chance to reach out and be heard."
    ],
    "determined": [
        "Your mind is laser-focused on achieving your goals.",
        "You’re thinking, ‘I will make this happen, no matter what.’",
        "You feel unstoppable, ready to take on any challenge.",
        "Your thoughts are clear, and your willpower is strong.",
        "You’re pushing forward with unwavering confidence."
    ],
    "inspired": [
        "Your mind is brimming with creative ideas and possibilities.",
        "You’re thinking, ‘I can’t wait to bring this vision to life!’",
        "You feel a surge of energy to do something meaningful.",
        "Your thoughts are aligned with purpose and passion.",
        "You’re ready to turn your dreams into reality."
    ],
    "relaxed": [
        "Your mind is at peace, floating gently like a cloud.",
        "You’re thinking, ‘Everything feels just right at this moment.’",
        "You feel completely at ease, as though nothing can disturb you.",
        "Your thoughts are calm, and your body feels light.",
        "You’re enjoying the tranquility of the present moment."
    ],
    "overwhelmed": [
        "Your mind is spinning with too much to handle all at once.",
        "You’re thinking, ‘How can I manage everything on my plate?’",
        "You feel weighed down by the sheer volume of tasks or emotions.",
        "Your thoughts are scattered, but you’re trying to find focus.",
        "You’re telling yourself, ‘One step at a time, I’ll get through this.’"
    ]
}


def capture_face():
    """Capture an image from the webcam and save it to the static/images folder."""
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        image_path = f'static/images/captured_image.jpg'
        cv2.imwrite(image_path, frame)
        cap.release()
        return image_path
    cap.release()
    return None

@app.route('/face')
def face():
    return render_template('faceindex.html')

@app.route('/scan')
def scan():
    try:
        # Capture the face and redirect to result page
        image_path = capture_face()
        if image_path:
            detected_emotion = random.choice(list(emotion_messages.keys()))  # Randomly select emotion for now
            session['emotion'] = detected_emotion
            session['image_path'] = image_path
            session['message'] = random.choice(emotion_messages[detected_emotion])
            return render_template('scan.html')  # Render the scanning page
        else:
            session['error'] = "Could not access the camera. Please check permissions or try again."
    except Exception as e:
        session['error'] = f"An unexpected error occurred: {e}"
    return redirect(url_for('home'))



@app.route('/result')
def result():
    detected_emotion = session.get('emotion', 'Processing...')
    image_path = session.get('image_path', '')
    message = session.get('message', '')
    return render_template('result.html', emotion=detected_emotion, image_path=image_path, message=message)

@app.route('/process_scan', methods=['POST'])
def process_scan():
    data = request.json
    image_data = data['image'].split(",")[1]  # Extract base64 part
    image_path = "static/images/captured_image.jpg"

    # Decode and save the image
    with open(image_path, "wb") as f:
        f.write(base64.b64decode(image_data))

    # Simulate emotion detection
    detected_emotion = random.choice(list(emotion_messages.keys()))
    session['emotion'] = detected_emotion
    session['image_path'] = image_path
    session['message'] = random.choice(emotion_messages[detected_emotion])

    return '', 204  # Return no content (redirect happens on the client side)
#face reader --end--

#image reader --starts--
images = {
    'blue': ['images/blue1.jpg', 'images/blue2.jpg', 'images/blue3.jpg', 'images/blue4.jpg'],
    'pink': ['images/pink1.jpg', 'images/pink2.jpg', 'images/pink3.jpg', 'images/pink4.jpg'],
    'yellow': ['images/yellow1.jpg', 'images/yellow2.jpg', 'images/yellow3.jpg', 'images/yellow4.jpg'],
    'green': ['images/green1.jpg', 'images/green2.jpg', 'images/green3.jpg', 'images/green4.jpg']
}

@app.route('/imageindex')
def imageindex():
    # Initialize the game
    session.clear()
    session['current_images'] = images  # Store current state of images
    session['chosen_images'] = []       # Track images in the selected color
    session['steps'] = 0
    return render_template('imageindex.html', images=images)

@app.route('/next', methods=['POST'])
def next_step():
    selected_color = request.form['color']  # Get the chosen color
    session['steps'] += 1

    # Narrow down images: Only keep images from the selected color
    if session['steps'] == 1:
        session['chosen_images'] = session['current_images'][selected_color]
    else:
        session['chosen_images'] = [
            img for img in session['chosen_images']
            if img in session['current_images'][selected_color]
        ]

    # Shuffle all images and redistribute across color groups
    all_images = sum(session['current_images'].values(), [])
    random.shuffle(all_images)
    num_colors = len(images)
    group_size = len(all_images) // num_colors
    redistributed_images = {
        color: all_images[i * group_size:(i + 1) * group_size]
        for i, color in enumerate(images)
    }

    # Handle any leftover images
    leftover_images = len(all_images) % num_colors
    if leftover_images:
        redistributed_images[list(redistributed_images.keys())[-1]].extend(
            all_images[-leftover_images:]
        )

    session['current_images'] = redistributed_images

    # After two steps, guess the image
    if session['steps'] == 2:
        guessed_image = session['chosen_images'][0] if session['chosen_images'] else 'images/default.jpg'
        return redirect(url_for('imageresult', image=guessed_image))

    return render_template('imageindex.html', images=redistributed_images)

@app.route('/imageresult')
def imageresult():
    guessed_image = request.args.get('image', 'images/default.jpg')
    return render_template('imageresult.html', image=guessed_image)
#image reader --ends--
if __name__ == '__main__':
    app.run(debug=True , port="5000")
