from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/agv/alerts', methods = ['POST'])
def sendalert():
    request.get_json(force=True)

    parser = reqparse.RequestParser()
    parser.add_argument('message', required=True)
    args = parser.parse_args()

    msg = (args['message'])
    
    return msg
  
  
# driver function
if __name__ == '__main__':
  
    	app.run(    debug=False, \
                host='0.0.0.0', \
                port=int(os.getenv('PORT', '5000')), threaded=True)
