import yaml
import os

class Arg:
    def __init__(self):

        self.cfg_check_list = ['usr', 'pwd', 'dir', 'host', 'port', 'key', 'only_media']

        # load yaml config
        if not os.path.isfile('config.yaml'):
            print("Config file not found. Creating default config.yaml")
            with open('config.yaml', 'w') as f:
                f.write('usr: admin\n')
                f.write('pwd: admin\n') 
                f.write('dir: C://\n') 
                f.write('host: 0.0.0.0\n') 
                f.write('port: 5000\n') 
                f.write('key: SECRET_KEY\n') 
                f.write('only_media: True\n') 

        with open('config.yaml', 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            assert all(key in config for key in self.cfg_check_list) , "Please check if config.yaml contains all of the following keys: " + str(cfg_check_list)
            assert all([type(config['usr']) == str, type(config['pwd']) == str, type(config['dir']) == str, type(config['host']) == str, type(config['port']) == int, type(config['key']) == str, type(config['only_media']) == bool])
            assert os.path.isdir(config['dir'])
            assert config['port'] > 0 and config['port'] < 65535
            assert len(config['host'].split('.')) == 4
            assert all([int(x)>=0 and int(x)<=255 for x in config['host'].split('.')])
            self.USERNAME = config['usr']  # your username
            self.PASSWORD = config['pwd'] # your password
            self.BASE_DIR = config['dir'] # your root directory, if windows, use like this: C://Users//user//Videos
            self.HOST = config['host'] # your host (0.0.0.0 means all interfaces)
            self.PORT = config['port'] # your port 
            self.KEY = config['key'] # your secret key in string (used for session, not important)
            self.only_media = config['only_media'] # True if you want to show only media files
