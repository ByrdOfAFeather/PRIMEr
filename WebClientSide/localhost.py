from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
	return render_template("index.html", static_url_path="/static")


app.run()
