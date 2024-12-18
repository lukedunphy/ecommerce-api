# E-commerce API with Flask

This project is a RESTful API for an e-commerce platform. The API allows users to manage products, users, and orders efficiently. It is built using Flask, SQLAlchemy, and Marshmallow, and uses a MySQL database.

---

## Features

- User management (CRUD operations)
- Product management (CRUD operations)
- Order creation and management
- Many-to-Many relationships between orders and products
- Error handling for invalid requests
- Automated timestamps for orders
- Postman collection for testing included

---

## Requirements

To run this application, you need:

- Python 3.9 or later
- Flask
- SQLAlchemy
- Marshmallow
- MySQL

Install the dependencies using:
```bash
pip install -r requirements.txt
```

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/lukedunphy/ecommerce-api.git
   cd ecommerce-api
   ```

2. Set up the MySQL database:
   - Create a database named `ecommerce`.
   - Update the database URI in `app.py` if necessary.

3. Run the application:
   ```bash
   flask run
   ```

---

## API Endpoints

### Users

- **Create User**: `POST /users`
  - Example Body:
    ```json
    {
        "name": "John Doe",
        "email": "john@example.com",
        "address": "123 Main St"
    }
    ```

- **Get All Users**: `GET /users`
- **Update User**: `PUT /users/<user_id>`
- **Delete User**: `DELETE /users/<user_id>`

### Products

- **Create Product**: `POST /products`
  - Example Body:
    ```json
    {
        "product_name": "Laptop",
        "price": 1000.0
    }
    ```

- **Get All Products**: `GET /products`
- **Update Product**: `PUT /products/<product_id>`
- **Delete Product**: `DELETE /products/<product_id>`

### Orders

- **Create Order**: `POST /orders`
  - Example Body:
    ```json
    {
        "user_id": 1
    }
    ```

- **Add Product to Order**: `GET /orders/<order_id>/add_product/<product_id>`
- **Remove Product from Order**: `DELETE /orders/<order_id>/remove_product`
  - Example Body:
    ```json
    {
        "product_id": 2
    }
    ```

- **Get All Products for an Order**: `GET /orders/<order_id>/products`
- **Get All Orders for a User**: `GET /orders/user/<user_id>`
- **Delete Order**: `DELETE /orders/<order_id>`

---

## Testing

The project includes a Postman collection for testing API endpoints. You can import the collection into Postman to test all features.

1. Open Postman.
2. Import the `ecommerce.postman_collection.json` file.
3. Run the tests in the respective folders: Users, Products, Orders.
