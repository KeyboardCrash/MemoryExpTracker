from flask import Flask, request, jsonify
import os
from track import *

app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

# Define API routes
@app.route('/', methods=['GET'])
def home():
    return '''
        <h1>Memory Express Tracker v1.0</h1>
        <p>Scrapes Memory Express for high demand products</p>
    '''

@app.route('/api/v1/memoryexpress/gpu/all', methods=['GET'])
def gpu_all():
    return jsonify(productData)

@app.route('/api/v1/memoryexpress/gpu/temp', methods=['GET'])
def gpu_tempData():
    return jsonify(tempData)

# Try to spin up the web server
try:
    from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher
except ImportError:
    from cherrypy.wsgiserver import CherryPyWSGIServer as WSGIServer, WSGIPathInfoDispatcher as PathInfoDispatcher

d = PathInfoDispatcher({'/': app})
server = WSGIServer(('0.0.0.0', 5000), d)

if __name__ == '__main__':
   try:
      server.start()
   except KeyboardInterrupt:
      server.stop()