'''This is the main file that runs the app.'''
from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=8080)
    