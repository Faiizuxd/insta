from flask import Flask, request, render_template_string, jsonify
import threading, time, os
from instagrapi import Client

app = Flask(__name__)
SESSION_FILE = "faizu_session.json"
cl = Client()
logged_in = False
spam_thread = None  # Reference to running spammer
stop_flag = False   # Control flag

def init_client():
    global cl
    cl = Client()
    cl.set_locale('en_US')
    cl.set_device("random")
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(cl.username, cl.password)
            return True
        except Exception as e:
            print(f"[Session Load Failed] {e}")
    return False

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
    a.btn-json { color: black; background: #00ffaa; text-decoration: none; padding: 10px 20px; border-radius: 10px; display: inline-block; font-weight: bold; margin: 10px; }
  </style>
</head>
<body>
  <h1>🟢 FAIZU INSTAGRAM BOT</h1>

  {% if not login %}
  <form method="POST">
    <input type="text" name="username" placeholder="Instagram Username" required><br>
    <input type="password" name="password" placeholder="Instagram Password" required><br>
    <button type="submit">Login</button>
  </form>
  {% else %}
    <h3>✅ Logged in</h3>
    <a class="btn-json" href="/threads-json" target="_blank">📤 Export Threads (JSON)</a>
    <form method="POST" enctype="multipart/form-data" action="/send">
      <input type="text" name="thread_id" placeholder="Enter Thread ID" required><br>
      <input type="text" name="prefix" placeholder="Prefix (e.g. FAIZU):" required><br>
      <input type="number" name="delay" placeholder="Delay between messages" required><br>
      <input type="file" name="txtFile" accept=".txt" required><br>
      <button type="submit">Start Bot</button>
    </form>
    <form method="POST" action="/stop">
      <button type="submit" style="background:red; color:white;">Stop Bot</button>
    </form>
    <h2>👇 Available Group Threads:</h2>
    {% if threads %}
      {% for t in threads %}
        <div class="thread-box">
          <strong>Title:</strong> {{ t.title }}<br>
          <strong>ID:</strong> {{ t.id }}
        </div>
      {% endfor %}
    {% else %}
      <p>No group chats found</p>
    {% endif %}
  {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    global logged_in
    if not logged_in:
        logged_in = init_client()

    if request.method == 'POST' and not logged_in:
        username = request.form['username']
        password = request.form['password']
        try:
            cl.login(username, password)
            cl.dump_settings(SESSION_FILE)
            logged_in = True
        except Exception as e:
            return f"<h3 style='color:red;'>❌ Login failed: {e}</h3>"

    threads = []
    if logged_in:
        try:
            threads = cl.direct_threads()
        except Exception as e:
            return f"<h3 style='color:red;'>❌ Failed to fetch threads: {e}</h3>"

    return render_template_string(HTML, login=logged_in, threads=threads or [])

@app.route('/send', methods=['POST'])
def send_msg():
    global spam_thread, stop_flag

    thread_id = request.form['thread_id']
    prefix = request.form['prefix']
    delay = int(request.form['delay'])
    messages = request.files['txtFile'].read().decode().splitlines()

    stop_flag = False

    def spammer():
        while not stop_flag:
            for msg in messages:
                if stop_flag:
                    print("⛔ Spammer stopped.")
                    return
                try:
                    full_msg = f"{prefix} {msg}"
                    cl.direct_send(full_msg, thread_ids=[thread_id])
                    print(f"✅ Sent: {full_msg}")
                    time.sleep(delay)
                except Exception as e:
                    print(f"❌ Error: {e}")
                    time.sleep(30)

    spam_thread = threading.Thread(target=spammer, daemon=True)
    spam_thread.start()
    return "<h2 style='color:lime;'>✅ Bot Started — Leave this tab open!</h2>"

@app.route('/stop', methods=['POST'])
def stop_msg():
    global stop_flag
    stop_flag = True
    return "<h2 style='color:red;'>⛔ Bot Stopped!</h2>"

@app.route('/threads-json')
def export_threads():
    try:
        threads = cl.direct_threads()
        json_data = [{"id": t.id, "title": t.title} for t in threads]
        return jsonify(json_data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
