from flask import Flask, request, render_template_string
import threading
import time
from instagrapi import Client

app = Flask(__name__)
cl = Client()
logged_in = False

HTML = '''
<!DOCTYPE html>
<html>
<head>
  <title>FAIZU InstaBot</title>
  <style>
    body { background-color: #000; color: #00ffaa; font-family: Arial; text-align: center; padding-top: 30px; }
    input, button, textarea { padding: 10px; margin: 10px; border-radius: 10px; border: none; width: 80%; max-width: 400px; }
    button { background-color: #00ffaa; color: #000; font-weight: bold; cursor: pointer; }
    .thread-box { background: #111; margin: 10px auto; padding: 10px; border-radius: 10px; max-width: 600px; }
  </style>
</head>
<body>
  <h1>🟢 FAIZU INSTAGRAM BOT</h1>

  {% if not logged_in %}
  <form method="POST">
    <input type="text" name="username" placeholder="Instagram Username" required><br>
    <input type="password" name="password" placeholder="Instagram Password" required><br>
    <button type="submit">Login</button>
  </form>
  {% else %}
    <h3>✅ Logged in</h3>
    <h2>👇 Available Group Threads:</h2>
    {% for t in threads %}
      <div class="thread-box">
        <strong>Title:</strong> {{ t.title }}<br>
        <strong>ID:</strong> {{ t.id }}
      </div>
    {% endfor %}

    <form method="POST" enctype="multipart/form-data" action="/send">
      <input type="text" name="thread_id" placeholder="Enter Thread ID" required><br>
      <input type="text" name="prefix" placeholder="Prefix (e.g. FAIZU):" required><br>
      <input type="number" name="delay" placeholder="Delay between messages" required><br>
      <input type="file" name="txtFile" accept=".txt" required><br>
      <button type="submit">Start Bot</button>
    </form>
  {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    global logged_in, cl

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            cl.login(username, password)
            logged_in = True
        except Exception as e:
            return f"<h3>❌ Login failed: {e}</h3>"

    if logged_in:
        threads = cl.direct_threads()
        return render_template_string(HTML, logged_in=True, threads=threads)

    return render_template_string(HTML, logged_in=False)

@app.route('/send', methods=['POST'])
def send_msg():
    thread_id = request.form['thread_id']
    prefix = request.form['prefix']
    delay = int(request.form['delay'])
    messages = request.files['txtFile'].read().decode().splitlines()

    def spammer():
        while True:
            for msg in messages:
                try:
                    final_msg = f"{prefix} {msg}"
                    cl.direct_send(final_msg, thread_ids=[thread_id])
                    print(f"✅ Sent: {final_msg}")
                    time.sleep(delay)
                except Exception as e:
                    print(f"❌ Error: {e}")
                    time.sleep(30)

    threading.Thread(target=spammer, daemon=True).start()

    return "<h2>✅ Bot Started — Leave this tab open!</h2>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
