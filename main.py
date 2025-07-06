from flask import Flask, request, render_template_string
import threading
import time
from instagrapi import Client

app = Flask(name)

HTML = '''

<!DOCTYPE html>  <html>  
<head>  
  <title>FAIZU InstaBot</title>  
  <style>  
    body { background-color: #111; color: #00ffaa; font-family: Arial; text-align: center; padding-top: 60px; }  
    input, button { padding: 10px; margin: 10px; border-radius: 10px; border: none; }  
    button { background-color: #00ffaa; color: #000; font-weight: bold; }  
  </style>  
</head>  
<body>  
  <h1>FAIZU Instagram Group Bot</h1>  
  <form method="POST" enctype="multipart/form-data">  
    <input type="text" name="username" placeholder="Username" required><br>  
    <input type="password" name="password" placeholder="Password" required><br>  
    <input type="text" name="thread_id" placeholder="Group Thread ID" required><br>  
    <input type="text" name="prefix" placeholder="Prefix (e.g. FAIZU)" required><br>  
    <input type="file" name="txtFile" accept=".txt" required><br>  
    <input type="number" name="delay" placeholder="Delay (sec)" required><br>  
    <button type="submit">Start Bot</button>  
  </form>  
</body>  
</html>  
'''  def spam_messages(username, password, thread_id, prefix, delay, messages):
cl = Client()
try:
cl.login(username, password)
print("✅ Login successful!")

while True:  
        for msg in messages:  
            try:  
                full_msg = f"{prefix} {msg}"  
                cl.direct_send(full_msg, thread_ids=[thread_id])  
                print(f"[SENT] {full_msg}")  
                time.sleep(delay)  
            except Exception as e:  
                print(f"[ERROR] {e}")  
                time.sleep(30)  
except Exception as e:  
    print(f"[LOGIN ERROR] {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
if request.method == 'POST':
username = request.form['username']
password = request.form['password']
thread_id = request.form['thread_id']
prefix = request.form['prefix']
delay = int(request.form['delay'])
messages = request.files['txtFile'].read().decode().splitlines()

thread = threading.Thread(target=spam_messages, args=(username, password, thread_id, prefix, delay, messages))  
    thread.daemon = True  
    thread.start()  

    return "<h2 style='color:lime'>✅ Bot Started — Leave this tab open!</h2>"  

return render_template_string(HTML)

if name == 'main':
app.run(host='0.0.0.0', port=5000)
