from flask import Flask, request, render_template_string
import threading
import time
from instagrapi import Client

app = Flask(__name__)
app.debug = True

html_code = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>FAIZU INSTAGRAM BOT</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
      font-family: 'Segoe UI', sans-serif;
      color: white;
    }
    .box {
      max-width: 600px;
      margin: 80px auto;
      background: rgba(0, 0, 0, 0.8);
      border-radius: 20px;
      padding: 30px;
      box-shadow: 0 0 20px #00ffaa;
    }
    h2 {
      text-align: center;
      margin-bottom: 30px;
      color: #00ffaa;
    }
    label {
      font-weight: bold;
    }
    .form-control {
      background: #111;
      color: white;
      border: 1px solid #00ffaa;
    }
    .btn-submit {
      background: #00ffaa;
      border: none;
      color: black;
      font-weight: bold;
      width: 100%;
      margin-top: 15px;
    }
  </style>
</head>
<body>
  <div class="box">
    <h2>FAIZU | Instagram GC Spammer</h2>
    <form action="/" method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label>Instagram Username:</label>
        <input type="text" class="form-control" name="username" required />
      </div>
      <div class="mb-3">
        <label>Instagram Password:</label>
        <input type="password" class="form-control" name="password" required />
      </div>
      <div class="mb-3">
        <label>Group Thread ID:</label>
        <input type="text" class="form-control" name="threadId" required />
      </div>
      <div class="mb-3">
        <label>Prefix Name (e.g., FAIZU):</label>
        <input type="text" class="form-control" name="prefix" required />
      </div>
      <div class="mb-3">
        <label>Select Message List (.txt):</label>
        <input type="file" class="form-control" name="txtFile" accept=".txt" required />
      </div>
      <div class="mb-3">
        <label>Delay Between Messages (seconds):</label>
        <input type="number" class="form-control" name="delay" min="1" required />
      </div>
      <button type="submit" class="btn btn-submit">Start Bot</button>
    </form>
  </div>
</body>
</html>
'''

def message_sender(username, password, thread_id, prefix, delay, messages):
    cl = Client()
    try:
        cl.login(username, password)
        print("Logged in successfully.")

        while True:
            for msg in messages:
                try:
                    full_message = f"{prefix} {msg}"
                    cl.direct_send(full_message, thread_ids=[thread_id])
                    print(f"Sent: {full_message}")
                    time.sleep(delay)
                except Exception as e:
                    print(f"Send error: {e}")
                    time.sleep(60)
    except Exception as login_error:
        print(f"Login Failed: {login_error}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        thread_id = request.form.get('threadId')
        prefix = request.form.get('prefix')
        delay = int(request.form.get('delay'))
        messages = request.files['txtFile'].read().decode().splitlines()

        thread = threading.Thread(target=message_sender, args=(username, password, thread_id, prefix, delay, messages))
        thread.daemon = True
        thread.start()

        return '<h3 style="color:lime; text-align:center; margin-top:30px;">Insta bot started! Leave this tab open.</h3>'

    return render_template_string(html_code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
