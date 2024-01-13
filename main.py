from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
import os

app = Flask(__name__)

USERNAME = 'admin'
PASSWORD = 'admin'
BASE_DIR = 'MY_FOLDER_PATH'  
PORT = 5000
app.config['SECRET_KEY'] = '_MY_SECRET_KEY_' 

def authenticate(username, password):
    return username == USERNAME and password == PASSWORD

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('show_directory'))
    return render_template('index.html')

@app.route('/directory')
def show_directory():
    
    if 'username' not in session:
        return redirect(url_for('login'))
    
    directory = request.args.get('dir')
    if directory is None:
        directory = ''

    if directory:
        directory_path = BASE_DIR + '/' + directory
    else:
        directory_path = BASE_DIR
    if not os.path.isdir(directory_path):
        return f"Directory not found: {directory_path}"

    entries = os.listdir(directory_path)

    video_files = [entry for entry in entries if entry.endswith(('.mp4', '.avi', '.mkv'))]
    image_files = [entry for entry in entries if entry.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    dirs = [entry for entry in entries if os.path.isdir(directory_path + '/' + entry)]

    return render_template('directory.html', directory=directory, video_files=video_files, image_files=image_files, entries=dirs)

@app.route('/play_video/<path:filename>')
def play_video(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    return send_from_directory(BASE_DIR, filename)


@app.route('/show_image/<path:filename>')
def show_image(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    return send_from_directory(BASE_DIR, filename)


@app.route('/login', methods=['GET', 'POST'])
def login():    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session['username'] = username
            return redirect(url_for('show_directory'))
        else:
            return render_template('login.html', error=True)
    else:
        if 'username' in session:
            return redirect(url_for('show_directory'))
        return render_template('login.html', error=False)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# @app.before_request
# def require_auth():
#     if request.path.startswith('/directory') or request.path.startswith('/play_video') or request.path.startswith('/show_image'):
#         if not request.authorization or not authenticate(request.authorization.username, request.authorization.password):
#             return 'Unauthorized', 401

if __name__ == '__main__':
    app.run(port=PORT)