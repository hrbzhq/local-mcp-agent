from waitress import serve

# Import app from web_app in this package
from web_app import app

if __name__ == '__main__':
    # bind to localhost:5000
    serve(app, host='127.0.0.1', port=5000)
