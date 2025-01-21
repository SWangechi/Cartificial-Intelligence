from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_cors import CORS
import os
from database.models import db, User, Product, Interaction
from recommender import collaborative_filtering, hybrid_recommendation
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://***:***@localhost/ecommerce'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'my_fallback_secret_key')

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
CORS(app)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('base.html')

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({"message": "Logged in successfully!"})
    return jsonify({"error": "Invalid credentials"}), 401

# Unauthorized handler for Flask-Login
@login_manager.unauthorized_handler
def unauthorized():
    return render_template('login.html'), 401

# Fetch all products for the catalog
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "price": f"${product.price:.2f}",
            "image_url": product.image_url
        }
        for product in products
    ]
    return jsonify(product_list)

# Product Recommendation
@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    product_id = request.args.get('product_id', type=int)
    method = request.args.get('method', 'hybrid')  # Default: Hybrid
    if method == 'collaborative':
        recommendations = collaborative_filtering(user_id)
    else:
        recommendations = hybrid_recommendation(user_id, product_id)
    
    recommendation_list = [
        {
            "id": rec["ProductID"],
            "name": Product.query.get(rec["ProductID"]).name,
            "price": f"${Product.query.get(rec['ProductID']).price:.2f}",
            "image_url": Product.query.get(rec["ProductID"]).image_url,
            "score": rec["Score"]
        }
        for rec in recommendations
    ]
    return jsonify(recommendation_list)

# User Dashboard
@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Shopping Cart
cart = []

@app.route('/cart', methods=['GET', 'POST'])
def manage_cart():
    global cart
    if request.method == 'POST':
        data = request.json
        cart.append(data)
        return jsonify({"message": "Item added to cart!", "cart": cart})
    return jsonify(cart)

# User Logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully!"})

# Initialize the database and run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures tables are created before running the app
    app.run(debug=True)
