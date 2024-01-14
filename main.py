from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
import os
import yaml

app = Flask(__name__, static_url_path='/static')

cfg_check_list = ['usr', 'pwd', 'dir', 'host', 'port', 'key', 'only_media']

# load yaml config
if not os.path.isfile('config.yaml'):
    print("Config file not found. Creating default config.yaml")
    with open('config.yaml', 'w') as f:
        f.write('usr: admin\n')
        f.write('pwd: admin\n')
        f.write('dir: /home/pi/Videos\n')
        f.write('host: 0.0.0.0\n')
        f.write('port: 5000\n')
        f.write('key: SECRET_KEY\n')
        f.write('only_media: True\n')

with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    assert all(key in config for key in cfg_check_list) , "Invalid config.yaml! Please check if config.yaml contains all of the following keys: " + str(cfg_check_list)
    assert all([type(config['usr']) == str, type(config['pwd']) == str, type(config['dir']) == str, type(config['host']) == str, type(config['port']) == int, type(config['key']) == str, type(config['only_media']) == bool]), "Invalid config.yaml! Please check if config.yaml contains valid data types"
    assert os.path.isdir(config['dir']), "Invalid config.yaml! Please check if config.yaml contains a valid directory path"
    assert config['port'] > 0 and config['port'] < 65535, "Invalid config.yaml! Please check if config.yaml contains a valid port number"
    assert len(config['host'].split('.')) == 4, "Invalid config.yaml! Please check if config.yaml contains a valid host address"
    assert all([int(x)>=0 and int(x)<=255 for x in config['host'].split('.')]), "Invalid config.yaml! Please check if config.yaml contains a valid host address"
    USERNAME = config['usr']
    PASSWORD = config['pwd']
    BASE_DIR = config['dir']
    HOST = config['host']
    PORT = config['port']
    app.config['SECRET_KEY'] = config['key']
    global only_media
    only_media = config['only_media']

def authenticate(username, password):
    return username == USERNAME and password == PASSWORD

def child_dir(path):
    return os.path.abspath(path).startswith(os.path.abspath(BASE_DIR))

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
    global only_media
    only_media = not only_media
    return redirect(f'/directory?dir={directory}')

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
    if not child_dir(BASE_DIR):
        return f"Invalid directory path: {directory_path}"
    
    entries = os.listdir(directory_path)

    global only_media
    if only_media:
        video_files = [entry for entry in entries if entry.endswith(('.mp4', '.avi', '.mkv'))]
        image_files = [entry for entry in entries if entry.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        dirs = [entry for entry in entries if os.path.isdir(directory_path + '/' + entry)]
        return render_template('directory.html', only_media=only_media, directory=directory, video_files=video_files, image_files=image_files, entries=dirs)
    else:
        files = [entry for entry in entries if os.path.isfile(directory_path + '/' + entry)]
        dirs = [entry for entry in entries if os.path.isdir(directory_path + '/' + entry)]
        return render_template('directory.html', only_media=only_media, directory=directory, entries=dirs, files=files)

@app.route('/file/<path:filename>')
def show_file(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    return send_from_directory(BASE_DIR, filename)

@app.route('/play_video/<path:filename>')
def play_video(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    type_video = get_type_video(filename)
    return render_template('video.html', filedir=BASE_DIR + '/' + filename, filename = filename, type_video = type_video) # if you want to play video with a player, use Video.js
   
@app.route('/raw_video/<path:filename>')
def raw_video(filename):
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

if __name__ == '__main__':
    app.run(port=PORT, host=HOST)