from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


class Ping(Resource):
    def get(self):
        return jsonify("pong")


api.add_resource(Ping, "/")

if __name__ == "__main__":
    app.run(debug=True)
