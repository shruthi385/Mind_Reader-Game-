import os
import random
import cv2
from flask import Flask, render_template, redirect, url_for, session
import base64
from flask import request

app = Flask(__name__)
app.secret_key = 'face_read'

# Ensure the images directory exists
if not os.path.exists('static/images'):
    os.makedirs('static/images')

# Random messages based on emotion
emotion_messages = {
    "happy": [
        "You are thinking about your bright future!",
        "You are cherishing a joyful memory!",
        "You feel joy in the little things around you.",
        "Your heart is light with happiness.",
        "You are embracing positivity and warmth."
    ],
    "sad": [
        "You are reflecting on your past challenges.",
        "You are feeling nostalgic about old times.",
        "You may be carrying the weight of past memories.",
        "Your heart feels heavy, but you're not alone.",
        "You may be searching for solace in quiet moments."
    ],
    "angry": [
        "You are frustrated about a past incident.",
        "You are thinking about overcoming difficulties.",
        "You feel your anger building up from unresolved issues.",
        "Your emotions are intense right now, take a breath.",
        "You're motivated to fight for what's right."
    ],
    "neutral": [
        "You are in a calm and composed state.",
        "You are observing things objectively.",
        "You're in a state of peaceful equilibrium.",
        "You are feeling neutral and balanced today.",
        "You are grounded, unaffected by strong emotions."
    ],
    "excited": [
        "You are eagerly anticipating what's to come.",
        "You feel a surge of energy and enthusiasm.",
        "Your excitement is contagious to those around you.",
        "Something thrilling is on the horizon for you!",
        "You can't wait to see how things unfold."
    ],
    "surprised": [
        "You were caught off guard by something unexpected.",
        "A sudden turn of events has left you in awe.",
        "You're processing a surprise that came your way.",
        "Life is full of surprises, and you're in the middle of one!",
        "The unexpected has left you with a sense of wonder."
    ],
    "confused": [
        "Things seem unclear right now, but you'll find clarity soon.",
        "You may be facing uncertainty about a situation.",
        "You're trying to make sense of things, but it's a bit muddled.",
        "Your thoughts are scattered, but it's okay to take a moment.",
        "You're unsure about a decision, but it will come together."
    ],
    "hopeful": [
        "You are looking forward to better days ahead.",
        "Your optimism shines through, even in tough times.",
        "Hope fills your heart as you think of the future.",
        "You are holding on to the belief that things will improve.",
        "A brighter tomorrow is waiting for you."
    ],
    "grateful": [
        "You feel a deep sense of appreciation for what you have.",
        "Gratitude fills your heart for the people around you.",
        "You are thankful for the blessings in your life.",
        "You recognize the good in your life and are thankful for it.",
        "Gratitude is guiding your thoughts today."
    ],
    "fearful": [
        "You may be feeling anxious about what's to come.",
        "Your mind is caught in a cycle of worry and fear.",
        "You're facing uncertainties that are hard to navigate.",
        "Fear has a hold on you, but remember you are stronger than it.",
        "You feel a sense of dread, but it will pass with time."
    ],
    "loving": [
        "Your heart is open to giving and receiving love.",
        "You are embracing the warmth of love and connection.",
        "Love is at the core of your thoughts and actions.",
        "You are surrounded by love, and it nurtures your spirit.",
        "Your relationships are the most precious thing to you right now."
    ],
    "bored": [
        "You are feeling disconnected and uninterested right now.",
        "Your mind is restless, seeking something to engage with.",
        "The world around you feels mundane and unexciting.",
        "You're in need of something stimulating to break the monotony.",
        "Boredom has settled in, but it'll pass soon enough."
    ],
    "curious": [
        "You are eager to learn and discover new things.",
        "Your mind is filled with questions, waiting for answers.",
        "You're curious about the mysteries around you.",
        "A sense of wonder drives your need to explore.",
        "You feel a deep urge to understand something new."
    ],
    "ashamed": [
        "You may be carrying the weight of past mistakes.",
        "There's a feeling of regret that lingers in your mind.",
        "You are reflecting on actions that didn't align with your values.",
        "Shame is heavy, but it can be healed with time and understanding.",
        "You are learning from your past, and growth is on the horizon."
    ],
    "lonely": [
        "You feel isolated, but remember that you are never truly alone.",
        "Loneliness has taken root, but you can seek connection.",
        "You're missing the presence of others in your life.",
        "You crave companionship, and it's okay to reach out.",
        "Though you're feeling lonely, you're surrounded by love from afar."
    ],
    "determined": [
        "You are focused on your goals and won't stop until you achieve them.",
        "Your willpower is unwavering, and you're on the path to success.",
        "Every challenge is an opportunity for you to prove yourself.",
        "You are determined to make things happen no matter the obstacles.",
        "Your inner strength is pushing you forward, keep going."
    ],
    "inspired": [
        "You are full of creative energy and new ideas.",
        "Something has sparked your imagination and passion.",
        "You're ready to take on new challenges with fresh eyes.",
        "Inspiration flows through you, and you're ready to create.",
        "You're feeling motivated to make a meaningful impact."
    ],
    "relaxed": [
        "You are at peace with yourself and the world around you.",
        "Your mind is calm, and your body feels at ease.",
        "Relaxation has taken over, and stress has melted away.",
        "You are savoring moments of tranquility and comfort.",
        "Your body and mind are in a state of rest and rejuvenation."
    ],
    "overwhelmed": [
        "You have too many things on your plate, and it feels heavy.",
        "Your mind is racing with thoughts, and it's hard to focus.",
        "Stress has built up, and you're feeling overwhelmed by it all.",
        "There's a lot going on right now, but you can handle it one step at a time.",
        "Take a deep breath, you are capable of overcoming this."
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

@app.route('/')
def home():
    return render_template('index.html')

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
if __name__ == '__main__':
    app.run(debug=True)
