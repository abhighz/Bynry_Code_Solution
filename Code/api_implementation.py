# Warehouse lookup: Based on the given company_id, fetch all warehouses.
#
# Inventory check: For each product in each warehouse, check if quantity is below threshold.
#
# Recent sales check: Only consider products with activity in the last 30 days.
#
# Daily sales calculation: Required to estimate days_until_stockout.
#
# Supplier fetch: Get supplier info from join table.
#
# Alert format: Matches the required JSON structure exactly.



from flask import jsonify
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app import app, db
from models import Company, Warehouse, Product, Inventory, Supplier, SupplierProduct, Sale

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    try:
        # Step 1: Get all warehouses for the company
        warehouses = Warehouse.query.filter_by(company_id=company_id).all()
        warehouse_ids = [w.id for w in warehouses]

        # Step 2: Get all inventory items in these warehouses
        inventories = Inventory.query.filter(Inventory.warehouse_id.in_(warehouse_ids)).all()

        alerts = []

        for inventory in inventories:
            product = Product.query.get(inventory.product_id)
            warehouse = Warehouse.query.get(inventory.warehouse_id)

            # Step 3: Check if product has recent sales (in last 30 days)
            last_30_days = datetime.utcnow() - timedelta(days=30)
            recent_sales = Sale.query.filter(
                Sale.product_id == product.id,
                Sale.warehouse_id == inventory.warehouse_id,
                Sale.sold_at >= last_30_days
            ).all()

            if not recent_sales:
                continue  # Skip if no recent sales

            # Step 4: Calculate average daily sales for the product
            total_qty_sold = sum(sale.quantity for sale in recent_sales)
            avg_daily_sales = total_qty_sold / 30 if total_qty_sold > 0 else 0.1  # Avoid div by 0

            # Step 5: Check if current stock is below threshold
            if inventory.quantity < product.threshold:
                # Step 6: Get supplier info (first one)
                supplier = db.session.query(Supplier).join(SupplierProduct).filter(
                    SupplierProduct.product_id == product.id
                ).first()

                supplier_info = {
                    "id": supplier.id,
                    "name": supplier.name,
                    "contact_email": supplier.contact_info
                } if supplier else None

                # Step 7: Estimate days until stockout
                days_until_stockout = int(inventory.quantity / avg_daily_sales)

                # Step 8: Build alert entry
                alerts.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "sku": product.sku,
                    "warehouse_id": warehouse.id,
                    "warehouse_name": warehouse.name,
                    "current_stock": inventory.quantity,
                    "threshold": product.threshold,
                    "days_until_stockout": days_until_stockout,
                    "supplier": supplier_info
                })

        return jsonify({
            "alerts": alerts,
            "total_alerts": len(alerts)
        }), 200

    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500
