from flask import Flask, render_template

app = Flask(__name__)
app.config["TEMPLATE_AUTO_LOADING"] = True
app.config["DEBUG"] = True

@app.route("/")
def index():
	return render_template("index.html", static_url_path="/static")


app.run()
