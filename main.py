from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
import os
from arg import Arg

app = Flask(__name__, static_url_path='/static')
arg = Arg()
app.config['SECRET_KEY'] = arg.KEY

def authenticate(username, password):
    return username == arg.USERNAME and password == arg.PASSWORD

def child_dir(path):
    return os.path.abspath(path).startswith(os.path.abspath(arg.BASE_DIR))

def get_type_video(filename):
    if filename.endswith('.mp4'):
        return 'video/mp4'
    elif filename.endswith('.avi'):
        return 'video/avi'
    elif filename.endswith('.mkv'):
        return 'video/mkv'
    else:
        return 'video/mp4'

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('show_directory'))
    return render_template('index.html')

@app.route('/change_display_mode')
def change_display_mode():
    if 'username' not in session:
        return redirect(url_for('login'))
    directory = request.args.get('dir')
    if directory is None:
        directory = ''
    arg.only_media = not arg.only_media
    return redirect(f'/directory?dir={directory}')

@app.route('/directory')
def show_directory():
    
    if 'username' not in session:
        return redirect(url_for('login'))
    
    directory = request.args.get('dir')
    if directory is None:
        directory = ''

    if directory:
        directory_path = arg.BASE_DIR + '/' + directory
    else:
        directory_path = arg.BASE_DIR

    if not os.path.isdir(directory_path):
        return f"Directory not found: {directory_path}"
    if not child_dir(arg.BASE_DIR):
        return f"Invalid directory path: {directory_path}"
    
    entries = os.listdir(directory_path)

    if arg.only_media:
        video_files = [entry for entry in entries if entry.endswith(('.mp4', '.avi', '.mkv'))]
        image_files = [entry for entry in entries if entry.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        dirs = [entry for entry in entries if os.path.isdir(directory_path + '/' + entry)]
        return render_template('directory.html', only_media=arg.only_media, directory=directory, video_files=video_files, image_files=image_files, entries=dirs)
    else:
        files = [entry for entry in entries if os.path.isfile(directory_path + '/' + entry)]
        dirs = [entry for entry in entries if os.path.isdir(directory_path + '/' + entry)]
        return render_template('directory.html', only_media=arg.only_media, directory=directory, entries=dirs, files=files)

@app.route('/file/<path:filename>')
def show_file(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    return send_from_directory(arg.BASE_DIR, filename)

@app.route('/play_video/<path:filename>')
def play_video(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    type_video = get_type_video(filename)
    return render_template('video.html', filedir=arg.BASE_DIR + '/' + filename, filename = filename, type_video = type_video) # if you want to play video with a player, use Video.js
   
@app.route('/raw_video/<path:filename>')
def raw_video(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    return send_from_directory(arg.BASE_DIR, filename) 


@app.route('/show_image/<path:filename>')
def show_image(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    return send_from_directory(arg.BASE_DIR, filename)


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

if __name__ == '__main__':
    app.run(port=arg.PORT, host=arg.HOST)