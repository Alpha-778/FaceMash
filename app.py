from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import psycopg2
import os
import random
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace this with a strong key
app.permanent_session_lifetime = timedelta(days=30)

# DB config
DB_CONFIG = {
    "dbname": "defaultdb",
    "user": "avnadmin",
    "password": "AVNS_w8Ct71HRTpe6brtEfgJ",
    "host": "servicesite-credit-system-114.l.aivencloud.com",
    "port": 20178,
    "sslmode": "require"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_random_images():
    image_folder = os.path.join('static', 'images')
    images = os.listdir(image_folder)
    return random.sample(images, 2)

@app.route('/')
def index():
    img_pair = get_random_images()
    session['current_pair'] = img_pair
    img_left = url_for('static', filename=f'images/{img_pair[0]}')
    img_right = url_for('static', filename=f'images/{img_pair[1]}')
    return render_template('index.html', img_left=img_left, img_right=img_right)

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    choice = data.get('choice')
    if choice not in ['left', 'right']:
        return jsonify({'status': 'error', 'message': 'Invalid choice'}), 400

    pair = session.get('current_pair')
    if not pair or len(pair) != 2:
        return jsonify({'status': 'error', 'message': 'No image pair found'}), 400

    voted_image = pair[0] if choice == 'left' else pair[1]
    user_id = request.remote_addr  # Can also use session ID here

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO votes (choice, image_name, user_id) VALUES (%s, %s, %s);", (choice, voted_image, user_id))
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM votes;")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM votes WHERE choice = 'left';")
    left = cur.fetchone()[0]
    right = total - left
    cur.close()
    conn.close()

    left_percent = round((left / total) * 100, 1) if total else 0
    right_percent = 100 - left_percent

    return jsonify({
        'status': 'success',
        'message': f'You voted for {choice.upper()}',
        'left_percent': left_percent,
        'right_percent': right_percent
    })

@app.route('/next')
def next_vote():
    return redirect(url_for('index'))

@app.route('/leaderboard')
def leaderboard():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT image_name, COUNT(*) as vote_count
        FROM votes
        GROUP BY image_name
        ORDER BY vote_count DESC
        LIMIT 10;
    """)
    leaderboard = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('leaderboard.html', leaderboard=leaderboard)

@app.route('/new_pair')
def new_pair():
    img_pair = get_random_images()
    session['current_pair'] = img_pair
    return jsonify({
        'img_left': url_for('static', filename=f'images/{img_pair[0]}'),
        'img_right': url_for('static', filename=f'images/{img_pair[1]}')
    })


if __name__ == '__main__':
    app.run(debug=True)
