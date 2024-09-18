from flask import Flask, render_template, request, jsonify, logging
import requests
import io

app = Flask(__name__)

# 기존 라우트
@app.route('/')
def index():
    return render_template('index.html')

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
        # 이미지를 Head 모델 API로 전송하고, Head에서 Tail로 중간 추론 값 전송 및 최종 결과 반환
        final_response = send_image_to_head_and_tail(file)

        if final_response.status_code == 200:
            # Tail 모델의 최종 예측 결과를 받아 클라이언트로 반환
            return jsonify({'status': 'success', 'label': final_response.json()['label']})
        else:
            return jsonify({'status': 'error', 'message': 'Model prediction failed'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def send_image_to_head_and_tail(file):
    head_url = "http://head-service/head_predict_and_forward"
    files = {'file': file.read()}
    app.logger.debug(f"Sending image to Head model, file size: {len(files['file'])} bytes")
    response = requests.post(head_url, files=files, timeout=10)
    app.logger.debug(f"Response status code: {response.status_code}")
    return response

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True)
    