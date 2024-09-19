## 서버 UI API

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

# 기존 데이터 처리 라우트
@app.route('/send_data', methods=['POST'])
def send_data():
    # 클라이언트로부터 받은 데이터
    data = request.json
    model = data.get('model')
    edge = data.get('edge')
    core = data.get('core')

    # 데이터 확인 (로그 출력)
    app.logger.debug(f"Model selected: {model}")
    app.logger.debug(f"Edge selected: {', '.join(edge) if edge else 'None'}")
    app.logger.debug(f"Core selected: {core}")

    # 응답 반환
    return jsonify({"status": "success", "message": "Data received successfully"}), 200

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
                    try:
                        data = final_response.json()
                        label = data.get('label')  # 모델 API 응답에 'label' 필드가 있다고 가정
                        if label is None:
                            return jsonify({'status': 'error', 'message': 'Invalid model response: missing label'}), 500

                        return jsonify({'status': 'success', 'label': label, 'elapsed_time': elapsed_time})
                    except (json.JSONDecodeError, KeyError) as e:
                        app.logger.error(f"Error parsing model response: {str(e)}")
                        return jsonify({'status': 'error', 'message': 'Invalid model response format'}), 500
                else:
                    app.logger.error(f"Model prediction failed with status code: {final_response.status_code}")
                    return jsonify({'status': 'error', 'message': 'Model prediction failed'}), 500
            except requests.exceptions.RequestException as e:
                app.logger.error(f"Error sending request to model API: {str(e)}")
                return jsonify({'status': 'error', 'message': 'Failed to communicate with model API'}), 500
            except Exception as e:
                app.logger.error(f"Unexpected error: {str(e)}")
                return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

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
