from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import Config
from models import db
from models.user import User
from models.chat import Chat
from models.message import Message

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/chats', methods=['GET'])
@jwt_required()
def get_chats():
    user_id = get_jwt_identity()
    chats = Chat.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": chat.id, "title": chat.title} for chat in chats]), 200

@app.route('/chats', methods=['POST'])
@jwt_required()
def create_chat():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_chat = Chat(title=data['title'], user_id=user_id)
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({"id": new_chat.id, "title": new_chat.title}), 201

@app.route('/chats/<int:chat_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(chat_id):
    messages = Message.query.filter_by(chat_id=chat_id).all()
    return jsonify([{"id": msg.id, "text": msg.text, "sender": msg.sender} for msg in messages]), 200

@app.route('/chats/<int:chat_id>/messages', methods=['POST'])
@jwt_required()
def send_message(chat_id):
    data = request.get_json()
    new_message = Message(text=data['text'], sender=data['sender'], chat_id=chat_id)
    db.session.add(new_message)
    db.session.commit()
    # TODO: Implement chatbot logic to generate a response
    # bot_response = generate_bot_response(data['text'])
    # bot_message = Message(text=bot_response, sender='bot', chat_id=chat_id)
    # db.session.add(bot_message)
    # db.session.commit()
    return jsonify({"message": "Message sent successfully"}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)