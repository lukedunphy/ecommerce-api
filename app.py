# imports
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError, fields
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, Table, String, Column, select, DateTime, Float
from typing import List
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

load_dotenv()

db_password = os.getenv('DB_PASSWORD')
print(f"Database Password: {db_password}")

# initialize flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+mysqlconnector://root:{db_password}@localhost/Ecommerce_API'
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
    Column("order_id", ForeignKey("orders.id"),primary_key=True),
    Column("product_id", ForeignKey("products.id"),primary_key=True)
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
    # order_date = ma.auto_field(dump_only=True, default=lambda: datetime.now(timezone.utc))
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Original 
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # many-to-one
    user: Mapped[List["User"]] = relationship(back_populates="orders")

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

    id = ma.auto_field(dump_only=True)
    user_id = fields.Integer()
    order_date = fields.DateTime()
    # products = fields.List(fields.Nested(ProductSchema))


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
    
    new_product = Product(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product), 201


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
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Retrieve user
    user_id = order_data['user_id']
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "user not found"}), 404

    # Create a new order
    new_order = Order(user=user)  # No need to handle order_date explicitly
    db.session.add(new_order)
    db.session.commit()
    
    return order_schema.jsonify(new_order), 201

# add a product to an order
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=["GET"])
def add_product(order_id, product_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "order not found"}), 404
    
    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({"message": "product not found"}), 404
    
    try:
        db.session.execute(
            order_product.insert().values(order_id=order_id, product_id=product_id)
        )
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "product already exists in the order"}), 400
    
    return jsonify({"message": "product has been added to the order"}), 201


# remove a proudct from an order
@app.route('/orders/<int:order_id>/remove_product', methods=['Delete'])
def remove_product(order_id):
    product_id = request.json.get("product_id")
    if not product_id:
        return jsonify({"message": "missing product_id in request body"}), 400 
    
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "order not found"}), 404
    
    # retrieve product
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "product not found"}), 404
    
    if product not in order.products:
        return jsonify({"message": "product is not in this order"}), 400
    
    order.products.remove(product)
    db.session.commit()

    return jsonify({"message": "product removed from the order"}), 200


# get all orders for a user
@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "user not found"}), 404
    
    orders = user.orders
    return jsonify(orders_schema.dump(orders)), 200


# get all products for an order
@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_products_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "order not found"}), 404
    
    products = order.products
    return jsonify(products_schema.dump(products)), 200
    


if __name__ == "__main__":

    with app.app_context():
        # creates all tables
        db.create_all()
        # if you need to drop all tables you can run:
        # db.drop_all()

    app.run(debug=True)