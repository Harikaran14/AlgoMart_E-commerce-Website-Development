from flask import Flask,render_template,jsonify,request, redirect, url_for,flash,session
import userlogin1,owner_order
from hashTable import fetch_user_orders_hash
import mysql.connector as m
import json
import os
from datetime import datetime,timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

# Establishing the connection to the database



def get_db_connection():
    return m.connect(user='root', host='localhost', passwd='1234', database='db2')

cart_file = 'cart.json'
app = Flask(__name__)
app.secret_key = "your_secret_key"
bst = userlogin1.initialize_bst()
# Retrieve from vegetables data
def fetch_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vegetables")
    rows = cursor.fetchall()
    products = []
    i = 1
    for row in rows:
        vegetable = {
            'id': row['id'],
            'name': row['name'],
            'image': f"{i}.jpeg",
            'price': row['price'],
            'quantity': row['quantity']
        }
        i += 1
        products.append(vegetable)
    cursor.close()
    conn.close()
    return products

@app.route('/')
def index():
    return render_template('startpage.html')    

@app.route('/orderpg',methods=['POST','get'])
def orderpg():
    if 'user_id' in session:
        phone_number = session['user_id']
        user_info = fetch_user_info(phone_number)
        user_orders = fetch_user_orders(phone_number)
        return render_template('index.html', user_info=user_info, user_orders=user_orders)
    else:
        flash("Please log in to view your profile.", 'danger')
        return redirect(url_for('login'))

def fetch_user_info(phone_number):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, phone_number, address,email FROM users WHERE phone_number = %s", (phone_number,))
    user_info = cursor.fetchone()
    cursor.close()
    conn.close()
    #print(user_info)
    return user_info

# Fetch user orders
def fetch_user_orders(phone_number):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch orders
    cursor.execute("SELECT * FROM orders WHERE phone_number = %s", (phone_number,))
    orders = cursor.fetchall()

    # Fetch order items for each order
    for order in orders:
        cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order['id'],))
        order['item'] = cursor.fetchall()

    cursor.close()
    conn.close()
    #print(orders)
    return orders

@app.route('/profile',methods=['POST','GET'])
def profile():
    if 'user_id' in session:
        phone_number = session['user_id']
        user_info = fetch_user_info(phone_number)
        user_orders = fetch_user_orders(phone_number)
        print(user_info)
        return render_template('profile.html', user_info=user_info, user_orders=user_orders)
    else:
        flash("Please log in to view your profile.", 'danger')
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        phone_number = request.form['phone_number']
        address = request.form['address']
        email = request.form['email']
        password = request.form['password']  # Assuming you're handling passwords too

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, phone_number, address, email, password) VALUES (%s, %s, %s, %s, %s)",
                           (username, phone_number, address, email, password))
            conn.commit()
            flash("Registration successful!", 'success')
        except Exception as e:
            conn.rollback()
            flash(f"Error during registration: {e}", 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/update_address', methods=['POST'])
def update_address():
    if 'user_id' in session:
        phone_number = session['user_id']
        new_address = request.form['new_address']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET address = %s WHERE phone_number = %s", (new_address, phone_number))
            conn.commit()
            flash("Address updated successfully!", 'success')
        except Exception as e:
            conn.rollback()
            flash(f"Error updating address: {e}", 'danger')
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('profile'))
    else:
        flash("Please log in to update your address.", 'danger')
        return redirect(url_for('login'))


def insert_order(phone_number, cart_items, total_amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    user = fetch_user_info(phone_number)
    us = user['username']
    try:
        # Insert the order
        cursor.execute("""
            INSERT INTO orders (user_name,phone_number, total_amount) 
            VALUES (%s,%s, %s)
        """, (us, phone_number, total_amount))
        order_id = cursor.lastrowid

        # Update vegetable availability
        for item in cart_items:
            # Fetch current quantity
            cursor.execute("SELECT quantity FROM vegetables WHERE name = %s", (item['name'],))
            current_quantity = cursor.fetchone()[0]
            new_quantity = current_quantity - item['quantity']
            if new_quantity < 0:
                new_quantity = 0
            # Update quantity in the database
            cursor.execute("UPDATE vegetables SET quantity = %s WHERE name = %s", (new_quantity, item['name']))

            # Insert order items
            cursor.execute("""
                INSERT INTO order_items (order_id, vegetable_name, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['name'], item['quantity'], item['price']))

        # Commit the transaction
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
# Function to insert an order
def insert_order1(phone_number, cart_items, total_amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    user=fetch_user_info(phone_number)
    us=user['username']
    try:
        # Insert the order
        cursor.execute("""
            INSERT INTO orders (user_name,phone_number, total_amount) 
            VALUES (%s,%s, %s)
        """, (us,phone_number, total_amount))
        order_id = cursor.lastrowid

        # Insert each item in the cart
        for item in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, vegetable_name, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, item['name'], item['quantity'], item['price']))

        # Commit the transaction
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def insert_order2(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print(f"Inserting order for user: {username} at {datetime.now()}")
        cursor.execute("""
            INSERT INTO successfullorders (username, orderplacetime, expectedby) 
            VALUES (%s, %s, %s)
        """, (username, datetime.now(), None))
        conn.commit()
        print("Order successfully inserted into successfullorders.")
    except m.Error as e:
        conn.rollback()
        print(f"MySQL Error: {e}")
    except Exception as e:
        conn.rollback()
        print(f"General Error: {e}")
    finally:
        cursor.close()
        conn.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    bst=userlogin1.initialize_bst()
    if request.method == 'POST':
        number = request.form['number']
        password = request.form['password']
        if number and password:
            if userlogin1.log_in(int(number), password, bst): 
                session['user_id'] = int(number)
                return redirect(url_for('orderpg'))
            else:
                return render_template('login.html',error="Invalid Login")
        else:
            return render_template('login.html',error="Invalid Login")

    return render_template('login.html')

@app.route('/api/products')
def get_products():
    products = fetch_products()
    print((products))
    return jsonify(products)

@app.route('/api/save-cart', methods=['POST'])
def save_cart():
    cart_data = request.get_json()
    with open(cart_file, 'w') as f:
        json.dump(cart_data, f)
    return jsonify({"message": "Cart saved successfully"}), 200

@app.route('/api/clear-cart', methods=['POST'])
def clear_cart():
    if os.path.exists(cart_file):
        os.remove(cart_file)
    return jsonify({"message": "Cart cleared successfully"}), 200

@app.route('/update_stock', methods=['GET', 'POST'])
def update_stock():
    products = fetch_products()
    return render_template('ownerpage.html', vegetables=products)

@app.route('/update', methods=['POST','GET'])
def update():
    conn = get_db_connection()
    cursor = conn.cursor()
    for name in request.form.getlist('name'):
        price = request.form.get(f'price[{name}]')
        quantity = request.form.get(f'quantity[{name}]')
        cursor.execute("UPDATE vegetables SET price=%s, quantity=%s WHERE name=%s", (price, quantity, name))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('update_stock')

@app.route('/ownerlogin',methods=['GET','POST'])
def ownerlogin():
    if request.method == 'POST':
        number = request.form['number']
        password = request.form['password']
        if number=='1212121212' and password=='owner':
            products=fetch_products()
            return render_template('ownerhome.html')
            #return render_template('ownerpage.html',vegetables=products)
        else:
            return render_template('ownerlogin.html')
    else:
        return render_template('ownerlogin.html')

@app.route('/bill',methods=['post','get'])
def bill():
    if request.method == 'POST':
        cart_data = request.form.get('cartData')
        cart_items = []
        #print(cart_data)
        if cart_data:
            cart_items = json.loads(cart_data)
            for item in cart_items:
                item['total_value']=round(float(item['price'])*float(item['quantity']),2)
            total_amount = sum(item['total_value'] for item in cart_items) 
            session['cart'] = cart_items  # Store cart data in session
            phone_number = session.get('phone_number') 
            if phone_number:                
                # Insert the order into the database
                insert_order(phone_number, cart_items, total_amount)
                return render_template('bill.html', cart_items=cart_items, total=total_amount)
            else:
                flash('Phone number not found in session. Please login again.', 'danger')
                #return redirect(url_for('login'))
    else:
        cart_items = session.get('cart', [])
        total_amount = sum(float(item['price']) * float(item['quantity']) for item in cart_items)
    return render_template('bill.html', cart_items=cart_items, total=total_amount)


@app.route('/confirm',methods=["POST","GET"])
def confirm():
    if request.method == 'POST':
        phone_number = session.get('user_id')
        user=fetch_user_info(phone_number)
        name=user['username']        
        if phone_number:
            cart_items = session.get('cart', [])
            #print(cart_items)
            if cart_items:
                # Calculate the total amount
                total_amount = sum(float(item['price']) * float(item['quantity']) for item in cart_items)
                
                # Insert the order into the database
                insert_order(phone_number, cart_items, total_amount)
                insert_order2(name)
                # Clear the cart
                send_order_confirmation(phone_number,cart_items)
                session.pop('cart', None)
                
                # Provide a success message and redirect to the index
                flash("Order placed successfully!", 'success')
                return redirect(url_for('orderpg'))
            else:
                flash("Your cart is empty.", 'danger')
                return redirect(url_for('orderpg'))
        else:
            flash("Please log in to place an order.", 'danger')
            return redirect(url_for('login'))
    else:
        # If it's a GET request, show the payment page (assuming you have a template for that)
        #return render_template('payment.html')
        pass
        

@app.route('/updateorder', methods=['GET', 'POST'])
def updateorder():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cq=owner_order.initialize_from_database()
    if request.method == 'POST':
        # Handling form submission
        order_id = request.form.get('order_id')
        expected_delivery_time = request.form.get('expected_delivery_time')
        
        try:
            cur.execute("""
                UPDATE orders
                SET expected_delivery_time = %s
                WHERE id = %s
            """, (expected_delivery_time, order_id))
            conn.commit()

            # Dequeue the order from the queue
            for order in cq:
                if order['order_id'] == int(order_id):
                    cq.dequeue()
                    break
        except Exception as e:
            print(f"Error updating expected delivery time: {e}")

    try:
        # Fetch orders from the queue
        orders = list(cq)
    except Exception as e:
        print(f"Error fetching orders: {e}")
        orders = []
    print(orders)
    return render_template('orders.html', orders=orders)       


@app.route('/vieworders')
def vieworders():
    user_orders_hash = fetch_user_orders_hash()
    orders = {key: value for key, value in user_orders_hash.items()}
    return render_template('vieworders.html', orders=orders)


def send_order_confirmation(phone_number, cart):
    SENDER_EMAIL = "vaibhavsp16@gmail.com"  # os.getenv("EMAIL_USER")
    SENDER_PASSWORD = "awxuuatnydkvqfeb"  # os.getenv("EMAIL_PASS")
    subject = "Order Placed"
    user_info = fetch_user_info(phone_number)
    name = user_info['username']
    order_id = 1  # Assuming a fixed order ID for demonstration; you should use the actual order ID

    body = f'''
Dear {name},

Thank you for your order. We have successfully received your order. Your order number is {order_id}.

Here are the details of your order:

Order ID: {order_id}
    '''

    body += 'Items:\n'
    for item in cart:
        body += f"- {item['name']}: {item['quantity']} x ${item['price']}\n"

    body += '''
Our team is currently processing your order, and we will keep you updated on the progress.
If you have any additional information or questions, please do not hesitate to reply to this email or
contact our support team.
'''

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = user_info['email']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the Gmail SMTP server and send the email
        context = ssl.create_default_context()
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls(context=context)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            text = msg.as_string()
            server.sendmail(SENDER_EMAIL, user_info['email'], text)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")



@app.route('/tracking', methods=['GET', 'POST'])
def tracking():
    if request.method == 'POST':
        billnumber = request.form['billnumber']
        
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute('SELECT * FROM orders WHERE id = %s', (billnumber,))
        track = cur.fetchone()
        cur.close()
        conn.close()

        if not track:
            flash('Order not found.', 'danger')
            return render_template('tracking.html', h=None, d=None, m=None)

        expectedtime = track['expected_delivery_time']

        if expectedtime is None:
            flash('Expected delivery time is not available.', 'warning')
            return render_template('tracking.html', h=None, d=None, m=None)

        current_time = datetime.now()
        timeleft = expectedtime - current_time
        if timeleft.total_seconds() < 0:
            timeleft = timedelta(0)

        seconds = timeleft.total_seconds()
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60

        return render_template('tracking.html', h=int(hours), d=int(days), m=int(minutes))
    
    return render_template('tracking.html', h=None, d=None, m=None)

@app.route('/order-confirmation')
def order_confirmation():
    order_id = 12345
    user_name = 'John Doe'
    phone_number = '123-456-7890'
    cart_items = [
        {'name': 'Tomato', 'quantity': 2, 'price': 1.50},
        {'name': 'Potato', 'quantity': 5, 'price': 0.80}
    ]
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('order_successful.html', 
                           order_id=order_id, 
                           user_name=user_name, 
                           phone_number=phone_number, 
                           cart_items=cart_items, 
                           total_amount=total_amount)



if __name__ == '__main__':
    app.run(debug=True)



'''@app.route('/owner_', methods=['GET', 'POST'])
def addexpectedtime():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        a = request.form['input1']
        id = session.get('current_id')
        try:
            cur.execute('UPDATE successfullorders SET expectedby = %s WHERE billnumber = %s', (int(a), id))
            conn.commit()
            print("Expected time updated successfully.")
        except Exception as e:
            conn.rollback()
            print(f"Error updating expected time: {e}")
        return redirect('/owner')
    else:
        if cq.isempty():
            return "No orders in the queue."
        else:
            current_element = cq.dequeue()
            session['current_id'] = current_element[0]
            table_name = str(current_element[0])
            try:
                cur.execute(f"SELECT * FROM `{table_name}`")
                bill = cur.fetchall()
                cur.execute(f"SELECT SUM(quantity * price) FROM `{table_name}`")
                total = cur.fetchone()[0]
            except Exception as e:
                print(f"Error fetching order details: {e}")
                return "Error fetching order details."
            return render_template('owner_orders.html', ce=current_element, bill=bill, total=total)
            
            
            @app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        number = request.form['number']
        if username and password and number:
            signup_mess = userlogin1.sign_up(username, number, password, bst)
            flash(signup_mess)
            return render_template('login.html', message="Sign up Successful")
    return render_template('signup.html')
    
   @app.route('/confirm_', methods=['POST'])
def place_order():
    session.pop('cart', None)
    flash("Order placed successfully!", 'success')
    return redirect(url_for('index'))'''

'''@app.route('/vieworders-', methods=['GET', 'POST'])
def vieworders_():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Handling form submission
        order_id = request.form.get('order_id')
        expected_delivery_time = request.form.get('expected_delivery_time')
        
        try:
            cur.execute("""
                UPDATE orders
                SET expected_delivery_time = %s
                WHERE id = %s
            """, (expected_delivery_time, order_id))
            conn.commit()
        except Exception as e:
            print(f"Error updating expected delivery time: {e}")

    try:
        # Fetch orders with their items
        cur.execute("""
            SELECT o.id AS order_id, o.phone_number, o.total_amount, o.order_date, o.user_name, o.expected_delivery_time,
                   oi.vegetable_name, oi.quantity, oi.price
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            ORDER BY o.order_date DESC, o.id, oi.id
        """)
        orders = cur.fetchall()
        #print("Fetched Orders:", orders)  # Debug: Print fetched orders

        # Group items by order
        grouped_orders = {}
        for order in orders:
            order_id = order['order_id']
            if order_id not in grouped_orders:
                grouped_orders[order_id] = {
                    'order_id': order_id,
                    'phone_number': order['phone_number'],
                    'total_amount': order['total_amount'],
                    'order_date': order['order_date'],
                    'user_name': order['user_name'],
                    'expected_delivery_time': order['expected_delivery_time'],
                    'item': []
                }
            item = {
                'vegetable_name': order['vegetable_name'],
                'quantity': order['quantity'],
                'price': order['price']
            }
            grouped_orders[order_id]['item'].append(item)
        #print("Grouped Orders:", grouped_orders)  # Debug: Print grouped orders
    except Exception as e:
        print(f"Error fetching orders: {e}")
        grouped_orders = {}
    finally:
        cur.close()
        conn.close()

    return render_template('vieworders.html', orders=grouped_orders.values())
'''