from flask import Flask, request, send_file, render_template
import os
import shutil
import tempfile
from werkzeug.utils import secure_filename
import roop
from roop import core

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files or 'video' not in request.files:
        return 'No file part', 400

    image = request.files['image']
    video = request.files['video']

    if image.filename == '' or video.filename == '':
        return 'No selected file', 400

    image_filename = secure_filename(image.filename)
    video_filename = secure_filename(video.filename)

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    output_video_path = os.path.join(app.config['OUTPUT_FOLDER'], 'face_changed_video_v2.mp4')

    image.save(image_path)
    video.save(video_path)

    # Perform face swap using roopf
    args = {
        'source_path': image_path,
        'target_path': video_path,
        'output_path': output_video_path,
        'keep_frames': True,
        'keep_fps': True,
        'temp_frame_quality': 1,
        'output_video_quality': 1,
        'execution_provider': 'cuda'
    }
    try:
        core.run(args)
    except Exception as e:
        return str(e), 500

    return send_file(output_video_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
