from flask import Flask, jsonify

app = Flask(__name__)

# Mock data similar to https://jsonplaceholder.typicode.com/users/<id>
mock_users = {
    1: {"id": 1, "name": "Leanne Graham", "username": "Bret", "email": "Sincere@april.biz"},
    2: {"id": 2, "name": "Ervin Howell", "username": "Antonette", "email": "Shanna@melissa.tv"},
    3: {"id": 3, "name": "Clementine Bauch", "username": "Samantha", "email": "Nathan@yesenia.net"},
    4: {"id": 4, "name": "Patricia Lebsack", "username": "Karianne", "email": "Julianne.OConner@kory.org"},
}

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = mock_users.get(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True,  host='127.0.0.1', port=5000)
