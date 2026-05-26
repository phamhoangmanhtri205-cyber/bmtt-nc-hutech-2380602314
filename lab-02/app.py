from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/caesar")
def caesar():
    return render_template("caesar.html")

@app.route("/vigenere")
def vigenere():
    return render_template("vigenere.html")

@app.route("/railfence")
def railfence():
    return render_template("railfence.html")

@app.route("/playfair")
def playfair():
    return render_template("playfair.html")

@app.route("/transposition")
def transposition():
    return render_template("transposition.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
