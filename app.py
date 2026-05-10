import streamlit as st
import pandas as pd
import psycopg2
import re
import random

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "seller_logged_in" not in st.session_state:
    st.session_state.seller_logged_in = False

# ======================================================
# DATABASE CONNECTION
# ======================================================
@st.cache_resource
def get_connection():
    conn = psycopg2.connect(
        host="db.oqbsidbsivwtsguwwqde.supabase.co",
        database="postgres",
        user="postgres",
        password="Bloodrag7803",
        port="5432"
    )
    return conn
conn = get_connection()
cursor = conn.cursor()

# ======================================================
# LOGIN SECTION
# ======================================================

st.title("Wholesale Inventory Management System")

role = st.selectbox(
    "Login As",
    ["Admin", "Seller"],
    key="role_select"
)

# ======================================================
# ADMIN LOGIN
# ======================================================

if role == "Admin":

    # ==========================================
    # SHOW LOGIN PAGE ONLY IF NOT LOGGED IN
    # ==========================================

    if not st.session_state.admin_logged_in:

        admin_id = st.text_input(
            "Admin ID",
            key="admin_id"
        )

        admin_password = st.text_input(
            "Password",
            type="password",
            key="admin_password"
        )

        if st.button(
            "Admin Login",
            key="admin_login_btn"
        ):

            if (
                admin_id == "admin"
                and admin_password == "admin"
            ):

                st.session_state.admin_logged_in = True

                st.rerun()

            else:

                st.error(
                    "Invalid Admin Credentials"
                )

    # ==================================================
    # AFTER LOGIN
    # ==================================================

    if st.session_state.admin_logged_in:

        st.success("Admin Login Successful")

        # ADD LOGOUT HERE

        if st.button(
            "Logout",
            key="admin_logout_btn"
        ):

            st.session_state.clear()

            st.rerun()
        # ==========================================
        # DASHBOARD METRICS
        # ==========================================

        total_products_query = """
        SELECT COUNT(*) AS total_products
        FROM products
        """

        total_products = pd.read_sql(
            total_products_query,
            conn
        ).iloc[0]["total_products"]

        total_suppliers_query = """
        SELECT COUNT(*) AS total_suppliers
        FROM suppliers
        """

        total_suppliers = pd.read_sql(
            total_suppliers_query,
            conn
        ).iloc[0]["total_suppliers"]

        inventory_value_query = """
        SELECT SUM(
            CAST(price AS BIGINT) *
            CAST(stock_quantity AS BIGINT)
            ) AS inventory_value
        FROM products
        """

        inventory_value = pd.read_sql(
            inventory_value_query,
            conn
        ).iloc[0]["inventory_value"]

        low_stock_query = """
        SELECT COUNT(*) AS low_stock

        FROM products

        WHERE stock_quantity < 10
        """

        low_stock = pd.read_sql(
            low_stock_query,
            conn
        ).iloc[0]["low_stock"]

        # ==========================================
        # DASHBOARD CARDS
        # ==========================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Products",
                total_products
            )

        with col2:
            st.metric(
                "Total Suppliers",
                total_suppliers
            )

        with col3:
            st.metric(
                "Inventory Value",
                f"₹{inventory_value:,.0f}"
            )

        with col4:
            st.metric(
                "Low Stock Products",
                low_stock
            )
        # ==================================================
        # PRODUCT MANAGEMENT
        # ==================================================

        st.header("Product Management")

        # ==================================================
        # ADD PRODUCT
        # ==================================================

        with st.expander("➕ Add Product"):

            col1, col2 = st.columns(2)

            with col1:

                product_id = st.number_input(
                    "Product ID",
                    step=1,
                    min_value=1,
                    key="admin_product_id"
                )

                product_name = st.text_input(
                    "Product Name",
                    key="admin_product_name"
                )

            with col2:

                category = st.text_input(
                    "Category",
                    key="admin_category"
                )

                price = st.number_input(
                    "Price",
                    min_value=0.0,
                    key="admin_price"
                )

            stock_quantity = st.number_input(
                "Stock Quantity",
                step=1,
                min_value=0,
                key="admin_stock"
            )

            if st.button(
                "Add Product",
                key="add_product_btn"
            ):

                query = """
                INSERT INTO products
                (
                    product_id,
                    product_name,
                    category,
                    price,
                    stock_quantity
                )

                VALUES (%s, %s, %s, %s, %s)
                """

                cursor.execute(
                    query,
                    (
                        product_id,
                        product_name,
                        category,
                        price,
                        stock_quantity
                    )
                )

                conn.commit()

                st.success(
                    "Product Added Successfully"
                )

        # ==================================================
        # UPDATE PRODUCT
        # ==================================================

        with st.expander("✏️ Update Product"):

            update_product_id = st.number_input(
                "Enter Product ID",
                step=1,
                min_value=1,
                key="update_product_id"
            )

            if st.button(
                "Fetch Product",
                key="fetch_product_btn"
            ):

                fetch_query = """
                SELECT *
                FROM products
                WHERE product_id = %s
                """

                product_df = pd.read_sql(
                    fetch_query,
                    conn,
                    params=[update_product_id]
                )

                if not product_df.empty:

                    st.session_state.product_data = (
                        product_df.iloc[0]
                    )

                else:

                    st.error("Product Not Found")

            # ==============================================
            # SHOW PRODUCT DATA
            # ==============================================

            if "product_data" in st.session_state:

                product = st.session_state.product_data

                col1, col2 = st.columns(2)

                with col1:

                    updated_name = st.text_input(
                        "Product Name",
                        value=product["product_name"],
                        key="updated_name"
                    )

                    updated_category = st.text_input(
                        "Category",
                        value=product["category"],
                        key="updated_category"
                    )

                with col2:

                    updated_price = st.number_input(
                        "Price",
                        value=float(product["price"]),
                        key="updated_price"
                    )

                    updated_stock = st.number_input(
                        "Stock Quantity",
                        value=int(
                            product["stock_quantity"]
                        ),
                        key="updated_stock"
                    )

                if st.button(
                    "Update Product",
                    key="final_update_btn"
                ):

                    update_query = """
                    UPDATE products

                    SET
                        product_name = %s,
                        category = %s,
                        price = %s,
                        stock_quantity = %s

                    WHERE product_id = %s
                    """

                    cursor.execute(
                        update_query,
                        (
                            updated_name,
                            updated_category,
                            updated_price,
                            updated_stock,
                            update_product_id
                        )
                    )

                    conn.commit()

                    st.success(
                        "Product Updated Successfully"
                    )

        with st.expander(
            "📦 View Inventory",
            expanded=True
        ):

            # ==========================================
            # SEARCH + FILTER
            # ==========================================

            col1, col2 = st.columns(2)

            with col1:

                search_product = st.text_input(
                    "🔍 Search Product",
                    key="search_product"
                )

            with col2:

                category_filter = st.selectbox(
                    "📂 Filter By Category",
                    [
                        "All",
                        "Beverages",
                        "Snacks",
                        "Dairy",
                        "Personal Care",
                        "Stationery"
                    ],
                    key="category_filter"
                )

            # ==========================================
            # QUERY
            # ==========================================

            query = """
            SELECT *
            FROM products
            WHERE 1=1
            """

            params = []

            # SEARCH FILTER

            if search_product:

                query += """
                AND product_name LIKE %s
                """

                params.append(
                    f"%{search_product}%"
                )

            # CATEGORY FILTER

            if category_filter != "All":

                query += """
                AND category = %s
                """

                params.append(category_filter)

            # ==========================================
            # EXECUTE QUERY
            # ==========================================

            df = pd.read_sql(
                query,
                conn,
                params=params
            )

            # ==========================================
            # LOW STOCK ALERT
            # ==========================================

            low_stock_df = df[
                df["stock_quantity"] < 10
            ]

            if not low_stock_df.empty:

                st.warning(
                    f"⚠️ {len(low_stock_df)} "
                    f"products are low in stock"
                )

                st.subheader(
                    "🚨 Low Stock Products"
                )

                st.dataframe(
                    low_stock_df[
                        [
                            "product_id",
                            "product_name",
                            "category",
                            "stock_quantity"
                        ]
                    ],
                    use_container_width=True
                )

            # ==========================================
            # SHOW INVENTORY
            # ==========================================

            st.dataframe(
                df,
                use_container_width=True
            )

            # ==================================================
            # TOP PURCHASED PRODUCTS
            # ==================================================

            st.header("Purchase Analytics")

            top_products_query = """
            SELECT

                p.product_name,

                SUM(pr.quantity)
                AS total_purchased

            FROM purchases pr

            JOIN products p
            ON pr.product_id = p.product_id

            GROUP BY p.product_name

            ORDER BY total_purchased DESC

            LIMIT 5
            """

            top_products_df = pd.read_sql(
                top_products_query,
                conn
            )

            st.subheader("🏆 Top Purchased Products")

            st.dataframe(
                top_products_df,
                use_container_width=True
            )

        # ==================================================
        # PURCHASE HISTORY
        # ==================================================

        with st.expander(
            "🛒 Purchase History",
            expanded=False
        ):

            purchase_history_query = """
            SELECT

                p.purchase_id,

                s.supplier_name,

                pr.product_name,

                p.quantity,

                p.purchase_price,

                p.purchase_date

            FROM purchases p

            JOIN suppliers s
            ON p.supplier_id = s.supplier_id

            JOIN products pr
            ON p.product_id = pr.product_id

            ORDER BY p.purchase_id DESC
            """

            purchase_history_df = pd.read_sql(
                purchase_history_query,
                conn
            )

            st.dataframe(
                purchase_history_df,
                use_container_width=True
            )
# ======================================================
# SELLER LOGIN
# ======================================================

if role == "Seller":

    # ==========================================
    # SHOW LOGIN/REGISTER ONLY
    # IF NOT LOGGED IN
    # ==========================================

    if not st.session_state.seller_logged_in:

        seller_page = st.selectbox(
            "Select Option",
            ["Login", "Register"],
            key="seller_page"
        )

        # ==================================================
        # REGISTER PAGE
        # ==================================================

        if seller_page == "Register":

            st.subheader("Seller Registration")

            new_supplier_name = st.text_input(
                "Supplier Name",
                key="new_supplier_name"
            )

            new_contact_person = st.text_input(
                "Contact Person",
                key="new_contact_person"
            )

            new_email = st.text_input(
                "Email",
                key="new_email"
            )

            new_phone = st.text_input(
                "Phone Number",
                key="new_phone"
            )

            new_city = st.text_input(
                "City",
                key="new_city"
            )

            new_password = st.text_input(
                "Create Password",
                type="password",
                key="new_password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                key="confirm_password"
            )

            if st.button(
                "Register Seller",
                key="register_seller_btn"
            ):

                email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

                if not re.match(
                    email_pattern,
                    new_email
                ):

                    st.error("Invalid Email Format")

                elif new_password != confirm_password:

                    st.error("Passwords Do Not Match")

                elif not (
                    len(new_password) >= 8
                    and re.search(r"[A-Z]", new_password)
                    and re.search(r"[a-z]", new_password)
                    and re.search(r"[0-9]", new_password)
                    and re.search(r"[!@#$%^&*]", new_password)
                ):

                    st.error(
                        """
                        Password must contain:
                        - 1 uppercase
                        - 1 lowercase
                        - 1 number
                        - 1 special character
                        - minimum 8 characters
                        """
                    )

                else:

                    register_query = """
                    INSERT INTO suppliers
                    (
                        supplier_name,
                        contact_person,
                        phone,
                        email,
                        city
                    )

                    VALUES (%s, %s, %s, %s, %s)
                    """

                    cursor.execute(
                        register_query,
                        (
                            new_supplier_name,
                            new_contact_person,
                            new_phone,
                            new_email,
                            new_city
                        )
                    )

                    conn.commit()

                    st.success(
                        "Seller Registered Successfully"
                    )

                    st.info(
                        "Now go to Login page"
                    )

        # ==================================================
        # LOGIN PAGE
        # ==================================================

        if seller_page == "Login":

            st.subheader("Seller Login")

            seller_email = st.text_input(
                "Email",
                key="seller_email"
            )

            seller_password = st.text_input(
                "Phone Number",
                type="password",
                key="seller_password"
            )

            if st.button(
                "Seller Login",
                key="seller_login_btn"
            ):

                login_query = """
                SELECT *
                FROM suppliers

                WHERE email = %s
                AND phone = %s
                """

                seller_df = pd.read_sql(
                    login_query,
                    conn,
                    params=[
                        seller_email,
                        seller_password
                    ]
                )

                if not seller_df.empty:

                    st.session_state.seller_logged_in = True

                    st.session_state.supplier_id = int(
                        seller_df.iloc[0]["supplier_id"]
                    )

                    st.session_state.supplier_name = (
                        seller_df.iloc[0]["supplier_name"]
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid Seller Credentials"
                    )
    # ==================================================
    # AFTER LOGIN
    # ==================================================

    if st.session_state.seller_logged_in:

        st.success("Seller Login Successful")

        if st.button(
        "Logout",
        key="seller_logout_btn"):

            st.session_state.clear()        

            st.rerun()

        # ==========================================
        # AVAILABLE PRODUCTS
        # ==========================================

        with st.expander(
            "🏬 Available Products",
            expanded=True
        ):

            products_query = """
            SELECT
                product_id,
                product_name,
                category,
                price,
                stock_quantity

            FROM products
            """

            products_df = pd.read_sql(
                products_query,
                conn
            )

            st.dataframe(
                products_df,
                use_container_width=True
            )

        # ==========================================
        # PURCHASE FROM ADMIN
        # ==========================================

        with st.expander(
            "🛒 Purchase From Warehouse"
        ):

            st.write(
                f"Logged in Supplier ID: "
                f"{st.session_state.supplier_id}"
            )

            product_options_query = """
            SELECT
                product_id,
                product_name,
                price,
                stock_quantity

            FROM products
            """

            product_options_df = pd.read_sql(
                product_options_query,
                conn
            )

            product_options = {
                f"{row['product_id']} - "
                f"{row['product_name']}": row

                for _, row
                in product_options_df.iterrows()
            }

            selected_product = st.selectbox(
                "Select Product",
                list(product_options.keys()),
                key="selected_product"
            )

            selected_row = product_options[selected_product]

            product_id = int(
                selected_row["product_id"]
            )

            product_name = selected_row["product_name"]

            product_price = float(
                selected_row["price"]
            )

            available_stock = int(
                selected_row["stock_quantity"]
            )

            st.write(
                f"Price Per Unit: ₹{product_price}"
            )

            st.write(
                f"Available Stock: {available_stock}"
            )

            quantity = st.number_input(
                "Quantity",
                step=1,
                min_value=1,
                max_value=available_stock,
                key="purchase_quantity"
            )

            total_price = quantity * product_price

            st.write(
                f"Total Price: ₹{total_price}"
            )

            purchase_date = st.date_input(
                "Purchase Date",
                key="purchase_date"
            )

            if st.button(
                "Purchase Product",
                key="purchase_btn"
            ):

                # ======================================
                # PURCHASE ENTRY
                # ======================================

                purchase_query = """
                INSERT INTO purchases
                (
                    supplier_id,
                    product_id,
                    quantity,
                    purchase_price,
                    purchase_date
                )

                VALUES (%s, %s, %s, %s, %s)
                """

                cursor.execute(
                    purchase_query,
                    (
                        st.session_state.supplier_id,
                        product_id,
                        quantity,
                        total_price,
                        str(purchase_date)
                    )
                )

                # ======================================
                # REDUCE ADMIN STOCK
                # ======================================

                update_query = """
                UPDATE products

                SET stock_quantity =
                    stock_quantity - %s

                WHERE product_id = %s
                """

                cursor.execute(
                    update_query,
                    (
                        quantity,
                        product_id
                    )
                )

                # ======================================
                # ADD TO SELLER INVENTORY
                # ======================================

                check_query = """
                SELECT *
                FROM seller_inventory

                WHERE supplier_id = %s
                AND product_id = %s
                """

                check_df = pd.read_sql(
                    check_query,
                    conn,
                    params=[
                        st.session_state.supplier_id,
                        product_id
                    ]
                )

                # EXISTING PRODUCT

                if not check_df.empty:

                    seller_update_query = """
                    UPDATE seller_inventory

                    SET quantity =
                        quantity + %s

                    WHERE supplier_id = %s
                    AND product_id = %s
                    """

                    cursor.execute(
                        seller_update_query,
                        (
                            quantity,
                            st.session_state.supplier_id,
                            product_id
                        )
                    )

                # NEW PRODUCT

                else:

                    seller_insert_query = """
                    INSERT INTO seller_inventory
                    (
                        supplier_id,
                        product_id,
                        quantity
                    )

                    VALUES (%s, %s, %s)
                    """

                    cursor.execute(
                        seller_insert_query,
                        (
                            st.session_state.supplier_id,
                            product_id,
                            quantity
                        )
                    )

                conn.commit()

                st.success(
                    "Product Purchased Successfully"
                )

        # ==========================================
        # MY INVENTORY
        # ==========================================

        with st.expander(
            "📦 My Inventory"
        ):

            seller_inventory_query = """
            SELECT

                si.product_id,

                p.product_name,

                p.category,

                p.price,

                si.quantity

            FROM seller_inventory si

            JOIN products p
            ON si.product_id = p.product_id

            WHERE si.supplier_id = %s
            """

            seller_inventory_df = pd.read_sql(
                seller_inventory_query,
                conn,
                params=[
                    st.session_state.supplier_id
                ]
            )

            st.dataframe(
                seller_inventory_df,
                use_container_width=True
            )

        # ==========================================
        # SELL TO CUSTOMER
        # ==========================================

        with st.expander(
            "💰 Sell To Customer"
        ):

            seller_products_query = """
            SELECT

                si.product_id,

                p.product_name,

                p.price,

                si.quantity

            FROM seller_inventory si

            JOIN products p
            ON si.product_id = p.product_id

            WHERE si.supplier_id = %s
            """

            seller_products_df = pd.read_sql(
                seller_products_query,
                conn,
                params=[
                    st.session_state.supplier_id
                ]
            )

            if seller_products_df.empty:

                st.warning(
                    "No products in seller inventory"
                )

            else:

                seller_product_options = {

                    f"{row['product_id']} - "
                    f"{row['product_name']}": row

                    for _, row
                    in seller_products_df.iterrows()
                }

                selected_sale_product = st.selectbox(
                    "Select Product To Sell",
                    list(
                        seller_product_options.keys()
                    ),
                    key="sale_product"
                )

                sale_row = seller_product_options[
                    selected_sale_product
                ]

                sale_product_id = int(
                    sale_row["product_id"]
                )

                sale_product_name = (
                    sale_row["product_name"]
                )

                sale_price = float(
                    sale_row["price"]
                )

                seller_stock = int(
                    sale_row["quantity"]
                )

                st.write(
                    f"Available Seller Stock: "
                    f"{seller_stock}"
                )

                customer_name = st.text_input(
                    "Customer Name",
                    key="customer_name"
                )

                sale_quantity = st.number_input(
                    "Quantity",
                    step=1,
                    min_value=1,
                    max_value=seller_stock,
                    key="sale_quantity"
                )

                final_sale_price = (
                    sale_quantity * sale_price
                )

                st.write(
                    f"Total Sale Amount: "
                    f"₹{final_sale_price}"
                )

                sale_date = st.date_input(
                    "Sale Date",
                    key="sale_date"
                )

                if st.button(
                    "Sell Product",
                    key="sell_product_btn"
                ):

                    # ==================================
                    # INSERT SALE
                    # ==================================

                    sales_query = """
                    INSERT INTO sales
                    (
                        supplier_id,
                        product_id,
                        customer_name,
                        quantity,
                        total_price,
                        sale_date
                    )

                    VALUES (%s, %s, %s, %s, %s, %s)
                    """

                    cursor.execute(
                        sales_query,
                        (
                            st.session_state.supplier_id,
                            sale_product_id,
                            customer_name,
                            sale_quantity,
                            final_sale_price,
                            str(sale_date)
                        )
                    )

                    # ==================================
                    # REDUCE SELLER STOCK
                    # ==================================

                    reduce_seller_stock_query = """
                    UPDATE seller_inventory

                    SET quantity =
                        quantity - %s

                    WHERE supplier_id = %s
                    AND product_id = %s
                    """

                    cursor.execute(
                        reduce_seller_stock_query,
                        (
                            sale_quantity,
                            st.session_state.supplier_id,
                            sale_product_id
                        )
                    )

                    conn.commit()

                    st.success(
                        "Product Sold Successfully"
                    )
        # ==================================================
        # SALES HISTORY
        # ==================================================

        with st.expander(
            "💰 My Sales History",
            expanded=False
        ):

            sales_history_query = """
            SELECT

                sales.sale_id,

                products.product_name,

                sales.customer_name,

                sales.quantity,

                sales.total_price,

                sales.sale_date

            FROM sales

            JOIN products
            ON sales.product_id = products.product_id

            WHERE sales.supplier_id = %s

            ORDER BY sales.sale_id DESC
            """

            sales_history_df = pd.read_sql(
                sales_history_query,
                conn,
                params=[
                    st.session_state.supplier_id
                ]
            )

            st.dataframe(
                sales_history_df,
                use_container_width=True
            )