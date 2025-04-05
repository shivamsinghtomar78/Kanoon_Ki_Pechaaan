from flask import Flask, redirect 
import subprocess

app = Flask(__name__)

@app.route('/start-streamlit')
def start_streamlit():
    subprocess.Popen(["streamlit", "run", "account.py"])
    return redirect("http://localhost:8501")  # Redirect after starting

if __name__ == '__main__':
    app.run(debug=True)
