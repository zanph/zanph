from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
app = Flask(__name__)
"""
set environment variable $ROULETTE_SETTINGS to point to a file
containing your desired configuration
"""
app.config.from_envvar('ROULETTE_SETTINGS', silent=True)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.debug = True
    app.run()
