import os
from flask import Flask, request

server = Flask(__name__)

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))