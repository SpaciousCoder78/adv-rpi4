from flask import Flask, request, Response, jsonify

app = Flask(__name__)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.get_json()  # retrieve variables from request body
    # process data as needed
    return jsonify({"message": "Data received", "received": data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
