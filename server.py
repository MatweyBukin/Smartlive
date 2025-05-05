from flask import Flask , request, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from ultralytics import YOLO
import json

app = Flask(__name__)
yolo = YOLO()
SHOW_TR = 0.8
ON_LIST = [0]

@app.route('/<user_token>', methods=['GET', 'POST'])
def upload_file(user_token):
    if request.method == 'POST':
        file = request.files["file"]
        filename = secure_filename(file.filename)
        filepatch = os.path.join("files",user_token,filename)
        os.makedirs('files\\'+user_token, exist_ok=True)
        file.save(filepatch)
        result_list = yolo(filepatch,verbose = False)
        result = result_list[0]
        i = 0
        for box in result.boxes:
            box = result.boxes[i]
            if float(box.conf[0]) >= SHOW_TR:
                cls = int(box.cls[0])
                if cls in ON_LIST:
                    return json.dumps(1)
            i+=1
        return json.dumps(0)
    return '''
    <!doctype html>
    <title>Загрузить новый файл</title>
    <h1>Загрузить новый файл</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    </html>
    '''

@app.route('/file/<user_token>/<path:filename>')
def serve_file(user_token,filename):
    dir = os.path.join("files",user_token)
    return send_from_directory(dir, filename)

@app.route('/get_user_files/<user_token>')
def get_user_files(user_token):
    dir = os.path.join("files",user_token)
    patchs = os.listdir(dir)
    urls = []
    for p in patchs:
        urls.append(url_for("serve_file",user_token = user_token,filename = p,_external = True))
    return json.dumps(urls)

app.run()