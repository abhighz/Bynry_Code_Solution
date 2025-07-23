# Problem Explaination:-

# 1. **Like checking for missing fields before using them**
#    So that the API doesn't crash if any required field (like `name`, `sku`, or `price`) is not provided in the request.
#
# 2. **Like checking if the SKU already exists**
#    So that duplicate products with the same SKU can't be created, keeping the product catalog clean and unique.
#
# 3. **Like removing `warehouse_id` from the Product model**
#    Because a product can be stored in multiple warehouses, so that relationship should be managed in the `Inventory` table, not directly in the product.
#
# 4. **Like converting the `price` to float**
#    So that decimal values like 99.99 are correctly stored, not rounded or broken.
#
# 5. **Like using `db.session.flush()` after adding the product**
#    So that we can get the product’s ID before committing to the database, which is needed to create the related inventory.
#
# 6. **Like creating the inventory only after the product is created**
#    So that the inventory can correctly reference the new product using its ID.
#
# 7. **Like committing both product and inventory in one transaction**
#    So that both are saved together, and if anything fails, both are rolled back to prevent incomplete data.
#
# 8. **Like using `try-except` with `rollback()`**
#    So that the database stays clean even if something goes wrong during the process.
#
# 9. **Like sending proper HTTP status codes (400, 409, 500, 201)**
#    So that the frontend or client knows exactly what happened — whether it’s success or any kind of error.


from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from app import app, db
from models import Product, Inventory

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()

    # Check if all required fields are present
    required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Check if the SKU already exists
    if Product.query.filter_by(sku=data['sku']).first():
        return jsonify({"error": "SKU already exists"}), 409

    try:
        # Create the product (without warehouse_id, since product can be in multiple warehouses)
        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=float(data['price'])  # Convert to float to support decimals
        )
        db.session.add(product)
        db.session.flush()  # Get product.id before committing

        # Create the inventory entry for the given warehouse
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data['warehouse_id'],
            quantity=data['initial_quantity']
        )
        db.session.add(inventory)

        # Commit both product and inventory together
        db.session.commit()

        return jsonify({
            "message": "Product created successfully",
            "product_id": product.id
        }), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error", "details": str(e)}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
