from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask import abort

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# Custom error handler for 404 Not Found
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

# Custom error handler for 400 Bad Request
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request, please check your data"}), 400

# Route to get all messages
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    if not messages:
        return jsonify({"error": "No messages found"}), 404
    return jsonify([message.to_dict() for message in messages]), 200

# Route to create a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()

    if not data or 'body' not in data or 'username' not in data:
        abort(400, description="Missing 'body' or 'username' in request data")

    try:
        new_message = Message(
            body=data['body'],
            username=data['username']
        )
        db.session.add(new_message)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(new_message.to_dict()), 201

# Route to get a specific message by ID
@app.route('/messages/<int:id>', methods=['GET'])
def get_message_by_id(id):
    message = db.session.get(Message, id)  # Updated
    if not message:
        abort(404, description="Message not found")
    return jsonify(message.to_dict()), 200

# Route to update a message by ID (PATCH)
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)  # Updated
    if not message:
        abort(404, description="Message not found")

    data = request.get_json()

    if not data or 'body' not in data:
        abort(400, description="Missing 'body' in request data")

    try:
        message.body = data.get('body', message.body)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify(message.to_dict()), 200

# Route to delete a message by ID
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)  # Updated
    if not message:
        abort(404, description="Message not found")

    try:
        db.session.delete(message)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return '', 204

if __name__ == '__main__':
    app.run(port=5555)
