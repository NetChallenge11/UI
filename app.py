## 수정된 UI API 코드 (Head와 Tail 모델 통합 가정)

from flask import Flask, render_template, request, jsonify, logging
import requests
import io
import time

app = Flask(__name__)

# 기존 라우트
@app.route('/')
def index():
    return render_template('index.html')

# 새로운 페이지로 이동하는 라우트
@app.route('/upload_page')
def upload_page():
    return render_template('upload.html')

# 이미지 업로드 및 전송 처리 라우트
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400

    file = request.files['file']

    try:
        # 시간 측정 시작
        start_time = time.time()

        # 통합된 모델 API로 이미지 전송 및 최종 결과 반환
        final_response = send_image_to_model(file)

        # 시간 측정 종료 및 경과 시간 계산
        end_time = time.time()
        elapsed_time = end_time - start_time

        if final_response.status_code == 200:
            # 모델의 최종 예측 결과와 경과 시간을 클라이언트로 반환
            # (통합된 모델 API의 응답 형식에 따라 label 추출 방식 수정 필요)
            return jsonify({'status': 'success', 'label': final_response.json()['prediction'][0], 'elapsed_time': elapsed_time}) 
        else:
            return jsonify({'status': 'error', 'message': 'Model prediction failed'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def send_image_to_model(file):
    model_url = "http://full-model-service/predict"  # 통합된 모델 API의 URL 및 포트로 수정 (가정)
    files = {'file': file.read()}
    app.logger.debug(f"Sending image to model, file size: {len(files['file'])} bytes")
    response = requests.post(model_url, files=files, timeout=10)
    app.logger.debug(f"Response status code: {response.status_code}")
    return response

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True)
