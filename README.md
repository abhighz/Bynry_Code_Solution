Here’s a clean and structured **README explanation (no code)** for your case study solution. You can directly include this in the README file under a **“Solution Overview”** or **“Problem Breakdown and Approach”** section:

---

## ✅ Case Study Solution Summary

### 🔹 Part 1: Code Review & Debugging

#### ✅ Problems Identified:

* Missing validation for required fields.
* No check for unique SKU constraint.
* `warehouse_id` wrongly stored in Product despite one product being in multiple warehouses.
* Price might break if not handled as decimal.
* Separate commits could cause partial data to be saved if one operation fails.
* No error handling — database could be left in an inconsistent state.

#### 🛠️ Solution Summary:

* Added field validation before processing.
* Checked for duplicate SKUs before inserting a product.
* Removed direct `warehouse_id` from the Product table; moved warehouse relations to the Inventory table.
* Used `float()` or `Decimal()` for accurate price storage.
* Wrapped the product and inventory insertions in a single transaction.
* Introduced proper HTTP response codes and error messages for frontend clarity.
* Used error handling with rollback to maintain database integrity.

---

### 🔹 Part 2: Database Design

#### ✅ Schema Overview:

* **Companies** → own multiple **Warehouses**
* **Products** → can exist in many **Warehouses** via an **Inventory** table
* **Suppliers** → provide one or more **Products**
* **Bundles** → are special products containing multiple other products
* **Inventory Logs** → track stock changes over time
* **Sales** → help determine recent activity per product

#### ❓ Gaps Identified / Questions to Ask:

* What defines “recent” sales activity? (7 days? 30 days?)
* Can a product belong to multiple suppliers?
* Should bundles have their own SKU or pricing model?
* How to track expired or damaged stock?
* Are thresholds static per product or configurable per warehouse?

#### 🧠 Design Justification:

* Used **foreign keys** to enforce integrity between products, warehouses, and suppliers.
* Indexed `sku`, `product_id`, and `company_id` for faster queries.
* Added `on_delete=cascade` behavior where appropriate to maintain relational consistency.
* Ensured **many-to-many** relationships using join tables (for product bundles and product-warehouse mapping).

---

### 🔹 Part 3: API Implementation – Low Stock Alert

#### ✅ Business Rules Implemented:

* Thresholds vary by product — fetched from Product table.
* Alert is triggered only if recent sales exist (based on past 30 days of sales).
* Alerts are returned per warehouse for each company.
* Supplier contact info is included to support quick reordering.

#### 🛠️ Solution Summary:

* Queried all warehouses of the company.
* Checked inventory levels vs. thresholds.
* Filtered for products with recent sales only.
* Estimated `days_until_stockout` using average daily sales.
* Gathered supplier data for each alerting product.
* Returned a structured JSON response containing all this info.

#### ⚠️ Edge Cases Handled:

* Company ID not found → returns `404 Not Found`.
* No recent sales or low-stock → returns empty alert list with `total_alerts = 0`.
* Missing supplier → handled with `null` or placeholder values.

---

Let me know if you'd like a short summary version too.
