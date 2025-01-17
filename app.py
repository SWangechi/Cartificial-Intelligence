from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database.models import db, User, Product, Interaction
from recommender import collaborative_filtering, hybrid_recommendation

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URL'] = 'mysql+pymysql://username:password@localhost/ecommerce'
app.config['SECRET_KEY'] = 'my_secret_key'

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))

# USer Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"})

# User login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        return jsonify({"message:" "Logged in successfully!"})
    return jsonify({"error": "Invalid credentials"}), 401

# Product recommendation
@app.route('./recommendations/<int:user_id>', methods=['GET'])
@login_required
def recommendations(user_id):
    product_id = request.args.get('product_id', type=int)
    product_id = request.args.get('method', 'hybrid')
    if method == 'collaborative':
        recs = collaborative_filtering(user_id)
    else:
        recs = hybrid_recommendation(user_id, product_id)
    return jsonify(recs)

# Logout
@app.route('./logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"})

if __name__=='__main__':
    app.run(debug=True)       