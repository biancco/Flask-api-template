from flask import Flask, Blueprint
import logging, sys, os 
from flask_cors import CORS

app = Flask(__name__)

#CORS
CORS(app)


#blueprint
bp=Blueprint('prediction',__name__,url_prefix='/')
from . import templates
app.register_blueprint(templates.bp)



#logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app_logger = logging.getLogger(__name__)
app_logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

file_handler = logging. FileHandler(os.environ['LOG_FILE'])
#file_handler = logging. FileHandler('logs/app.log')

handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

app_logger.addHandler(handler)
app_logger.addHandler(file_handler)