# imports
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, Table, String, Column, select, DateTime, Float
from typing import List
from datetime import datetime, timezone

# initialize flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://root:xQClost.123@localhost/Ecommerce_API'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# base class 
class Base(DeclarativeBase):
    pass


# initialize SQLAchemy and Marshmallow
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

# ====== models ======


# association table
order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id")),
    Column("product_id", ForeignKey("products.id"))
)

# user table
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(150), unique=True)

    # one-to-many 
    orders: Mapped[List["Order"]] = relationship(back_populates="user")


# order table
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    # use lambda function so line is called everytime a new row is created not just when column is defined
    order_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # many-to-one
    user: Mapped["User"] = relationship(back_populates="orders")

    # one-to-many
    products: Mapped[List["Product"]] = relationship(secondary=order_product, back_populates="order_products")


# product table
class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)

    # one-to-many
    order_products: Mapped[List["Order"]] = relationship(secondary=order_product, back_populates="products")




# ====== schemas ======

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

user_schema = UserSchema()  # serialzes a single user object
users_schema = UserSchema(many=True)   # allows for serializaiton of list

order_schema = OrderSchema()  # serialzes a single order object
orders_schema = OrderSchema(many=True)   # allows for serializaiton of list

product_schema = ProductSchema()  # serialzes a single product object
products_schema = ProductSchema(many=True)    # allows for serializaiton of list


# ====== user routes and endpoints ======

# create a user
@app.route('/users', methods=["POST"])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_user = User(name=user_data['name'], email=user_data['email'], address=user_data['address'])
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201


# retrieve all users
@app.route('/users', methods=["GET"])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()
    
    return users_schema.jsonify(users), 200


# retrieve user by ID
@app.route('/users/<int:id>', methods=["GET"])
def get_user(id):
    user = db.session.get(User, id)
    return user_schema.jsonify(user), 200


# update a user by ID
@app.route('/users/<int:id>', methods=["PUT"])
def update_user(id):
    user = db.session.get(User, id)

    # check to see if user exists
    if not user:
        return jsonify({"message": "User is not in the database"}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user.name = user_data['name']
    user.address = user_data['address']
    user.email = user_data['email']

    db.session.commit()
    return user_schema.jsonify(user), 200

# delete user by ID
@app.route('/users/<int:id>', methods=["DELETE"])
def delete_user(id):
    user = db.session.get(User, id)

    # check for user before deleting
    if not user:
        return jsonify({"message": "user is not in the database"}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"user {id} has been deleted"}), 200
    

# ====== product routes and endpoints ======

# create a new product
@app.route('/products', methods=["POST"])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_proudct = Product(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_proudct)
    db.session.commit()

    return user_schema.jsonify(new_proudct), 201


# retrieve all products
@app.route('/products', methods=["GET"])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products), 200


# retrieve proudct by ID
@app.route('/products/<int:id>', methods=["GET"])
def get_product(id):
    product = db.session.get(Product, id)

    return product_schema.jsonify(product), 200


# update product by ID
@app.route('/products/<int:id>', methods=["PUT"])
def update_product(id):
    product = db.session.get(Product, id)

    # check for product
    if not product:
        return jsonify({"message": "product is not in database"})
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.product_name = product_data['product_name']
    product.price = product_data['price']

    db.session.commit()
    return product_schema.jsonify(product), 200


# delete product by ID
@app.route('/products/<int:id>', methods=["DELETE"])
def delete_product(id):
    product = db.session.get(Product, id)

    # check for product
    if not product:
        return jsonify({"message": "product not in database"}), 400
    
    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": f"product {id} has been deleted"}), 200


# ====== order routes and endpoints ======

# create new order
@app.route('/orders', methods=["POST"])
def create_order():
    try:
        # Validate and deserialize the order_date (if included)
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Get user_id directly from the request JSON
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"message": "user_id is required"}), 400

    # Retrieve the user using user_id
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Create the new order
    new_order = Order(user=user)
    db.session.add(new_order)
    db.session.commit()

    # Return the created order details
    return jsonify({
        "id": new_order.id,
        "order_date": new_order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": new_order.user_id
    }), 201

    


if __name__ == "__main__":

    with app.app_context():
        # creates all tables
        db.create_all()
        # if you need to drop all tables you can run:
        #db.drop_all()

    app.run(debug=True)