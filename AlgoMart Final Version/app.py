from flask import Flask, render_template, request, url_for , redirect, jsonify, session
from flask_session import Session
import mysql.connector as m
import ctypes
import os
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

EMAIL_ADDRESS = "ncheran59@gmail.com"
EMAIL_PASSWORD = "xpln xxpt qggd lhgd"  # NOT your Gmail password, but an App Password



conn=m.connect(host='localhost',user='root',password='hari2004',database='ecommerce')
cur=conn.cursor()
print("connected to mysql")
cur.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        category VARCHAR(30) ,
        primary key (category)
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        phone_number BIGINT PRIMARY KEY,
        password VARCHAR(30) NOT NULL,
        name VARCHAR(30),
        address VARCHAR(200),
        email varchar(200)
        
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS products (
        item VARCHAR(30) PRIMARY KEY,
        quantity INT NOT NULL,
        price INT NOT NULL,
        category VARCHAR(30),
        FOREIGN KEY (category) REFERENCES categories(category)
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS successfullorders (
        billnumber INT AUTO_INCREMENT PRIMARY KEY,
        phone_number BIGINT NOT NULL,
        orderplacetime DATETIME,
        expectedby DATETIME NULL,
        FOREIGN KEY (phone_number) REFERENCES customers(phone_number)
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS orderitems (
        ordernumber INT AUTO_INCREMENT PRIMARY KEY,
        orderid INT,
        product VARCHAR(30),
        quantity INT,
        FOREIGN KEY (orderid) REFERENCES successfullorders(billnumber  ),
        FOREIGN KEY (product) REFERENCES products(item)
    )
''')

conn.commit()


class TreeNode:
    def __init__(self, phone_number, password):
        self.phone_number = phone_number
        self.password = password
        self.left = None
        self.right = None

class UserBST:
    def __init__(self):
        self.root = None

    def insert(self, phone_number, password):
        if self.root is None:
            self.root = TreeNode(phone_number, password)
        else:
            self._insert(self.root, phone_number, password)

    def _insert(self, node, phone_number, password):
        if phone_number < node.phone_number:
            if node.left is None:
                node.left = TreeNode(phone_number, password)
            else:
                self._insert(node.left, phone_number, password)
        elif phone_number > node.phone_number:
            if node.right is None:
                node.right = TreeNode(phone_number, password)
            else:
                self._insert(node.right, phone_number, password)

    def search(self, phone_number):
        return self._search(self.root, phone_number)

    def _search(self, node, phone_number):
        if node is None or node.phone_number == phone_number:
            return node
        elif phone_number < node.phone_number:
            return self._search(node.left, phone_number)
        else:
            return self._search(node.right, phone_number)


class Node:
    def _init_(self, vegetable_name, quantity):
        self.vegetable_name = vegetable_name
        self.quantity = quantity
        self.next = None


class LinkedList:
    def _init_(self):
        self.head = None

    def add_to_cart(self, vegetable_name, quantity):
        new_node = Node(vegetable_name, quantity)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def display_cart(self):
        current = self.head
        if not current:
            print("Cart is empty")
            return

        print("Vegetables in cart:")
        while current:
            print(f"{current.vegetable_name}: {current.quantity}")
            current = current.next

    def remove_from_cart(self, vegetable_name):
        current = self.head
        prev = None

        while current and current.vegetable_name != vegetable_name:
            prev = current
            current = current.next

        if not current:
            print(f"{vegetable_name} not found in cart")
            return

        if not prev:
            self.head = current.next
        else:
            prev.next = current.next

        print(f"{vegetable_name} removed from cart")


class CircularQueue:
    def __init__(self,cap=20):
        self.cap=cap
        self.front=0
        self.rear=0
        self.item=(ctypes.py_object * cap)()
    def __str__(self):
        if self.front<=self.rear:
            return str(self.item[self.front:self.rear+1])
        else:
            return str(self.item[self.front:self.cap]+self.item[0:self.rear+1])
    def next(self,pos):
        return (pos + 1) % self.cap
    def isfull(self):
        return self.front==self.next(self.rear)
    def isempty(self):
        return self.front==self.rear
    def enqueue(self,value):
        if self.isfull():
            self.inc_resize()
        self.item[self.rear]=value
        self.rear=self.next(self.rear)

    def showfront(self):
        if self.isempty():
            return ("The queue is empty") 
        return self.item[self.front]
    def dequeue(self):
        if self.isempty():
            return ("The queue is empty") 
        value=self.item[self.front] 
        self.item[self.front]= None 
        self.front=self.next(self.front)
        return value
    def inc_resize(self):    
        temp=(ctypes.py_object*(2*self.cap))()
        for i in range(self.cap-1):
            temp[i]=self.item[i]
        self.item=temp
        self.cap=2*self.cap   

class BSTNode:
    def __init__(self, key, product):
        self.key = key       # product name (string)
        self.product = product  # entire row (tuple/dict from DB)
        self.left = None
        self.right = None

def insert(root, key, product):
    if root is None:
        return BSTNode(key, product)
    if key.lower() < root.key.lower():
        root.left = insert(root.left, key, product)
    else:
        root.right = insert(root.right, key, product)
    return root

def search_prefix(root, prefix, results):
    if root is None:
        return
    # traverse left
    search_prefix(root.left, prefix, results)

    # check current node
    if root.key.lower().startswith(prefix.lower()):
        results.append(root.product)

    # traverse right
    search_prefix(root.right, prefix, results)

def update_bst_quantity(root, item, qty_to_reduce,p=None):
    if not root:
        return None
    
    if item.lower() < root.key.lower():
        root.left = update_bst_quantity(root.left, item, qty_to_reduce)
    elif item.lower() > root.key.lower():
        root.right = update_bst_quantity(root.right, item, qty_to_reduce)
    else:
        # Found the product
        prod_list = list(root.product)  # convert tuple to list for mutability
        prod_list[1] -= qty_to_reduce   # decrease quantity (index 1 assumed to be quantity)
        if prod_list[1] < 0:            # safeguard
            prod_list[1] = 0
        if p is not None:
            prod_list[2]=p
        root.product = tuple(prod_list) # update node with new tuple
    return root



bst = UserBST()
cur.execute('SELECT phone_number, password FROM customers')
for row in cur.fetchall():
    bst.insert(int(row[0]), row[1])





app = Flask(__name__, template_folder='templates')

app.secret_key = 'your_unique_secret_key'
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)


 
upfolder="static/productimages"
app.config["UPLOAD_FOLDER"] = upfolder
os.makedirs(upfolder,exist_ok=True)



@app.route('/')
def firstpage():
    session.clear()
    return render_template('frontpage.html')


@app.route('/ownerlogin', methods=['GET','POST'])
def ownerlogin():
    if request.method=='POST':
        user=request.form['username']
        passw=request.form['password']
        
        if user=='Hari' and passw=='bowled':
            session['username']=user
            session['password']=passw
            return redirect('/view_orderitems')  
        else:
            flash="Wrong owner login details. Please enter again"
            return render_template('ownerlogin.html',error=flash)
    
    else:
        
        return render_template('ownerlogin.html')


@app.route('/customerlogin',methods=['GET','POST'])
def customerlogin():
    if request.method=='POST':
        phone_number=int(request.form['phone_no'])
        passw=request.form['password']
        
        user_node = bst.search(phone_number)
        if user_node and user_node.password == passw:
            session['phone_number']=phone_number
            session['passw']=passw
            return redirect('/homepage')
        else:
            flash="Wrong customer login details. Please enter again"
            return render_template('login.html',error=flash)
    else:
        
        return render_template('login.html')


@app.route('/customersignup',methods=['GET','POST'])
def customersignup():
    if request.method=='POST':
        phone_number=int(request.form['phone_no'])
        passw=request.form['password']
        name=request.form['name']
        address=request.form['address']
        email=request.form['email']
        cur.execute('SELECT * FROM customers WHERE phone_number = %s', (phone_number,))
        if cur.fetchone():
            #already exists
            flash="Customer Phone Number already exists"
            return render_template('signup.html',error=flash)
        cur.execute('INSERT INTO customers(phone_number,password,name,address,email) VALUES (%s, %s , %s , %s,%s )', (phone_number, passw, name , address, email ))
        conn.commit()

        # Insert new user into the tree
        bst.insert(phone_number, passw)
        session['phone_number']=phone_number
        session['passw']=passw
        session['cart']={}
        return redirect('/homepage')
        
    else:
        return render_template('signup.html')
@app.route("/owneradd")
def owneradd():
    return render_template("Owner-additems.html")

@app.route("/ownerUpload",methods= ["POST"])
def ownerUpload():
    name=request.form["itemName"]
    cat=request.form["itemCat"]
    try:
        cur.execute("insert into  categories values( %s)",(cat,))
        conn.commit()
    except:
        pass

    price=request.form["price"]
    qty=request.form["quantity"]
    img=request.files["file"]
    imgpth=os.path.join(app.config["UPLOAD_FOLDER"],img.filename)
    img.save(imgpth)
    cur.execute("insert into products values(%s,%s,%s,%s)",(name,qty,price,cat))
    conn.commit()
    cur.execute("SELECT * FROM products WHERE quantity > 0")
    all_products = cur.fetchall()

    bst_root = None
    for product in all_products:
        bst_root = insert(bst_root, product[0], product)

    return redirect("/view_orderitems")

cur.execute("SELECT * FROM products WHERE quantity > 0")
all_products = cur.fetchall()
print(all_products)
bst_root = None
for product in all_products:
    bst_root = insert(bst_root, product[0], product)


@app.route('/homepage',methods=["GET","post"])
def homepage():
    if 'phone_number' not in session:
        return redirect("/")
    if 'cart' not in session:
        session['cart']={}
    if request.method == 'POST':
        if 'search' in request.form:
            item = request.form["search"]
            results = []
            search_prefix(bst_root, item, results)
            return render_template('homepage.html', items=results, cart=session['cart'])

            
    results = []
    search_prefix(bst_root, '', results)
    return render_template('homepage.html', items=results, cart=session['cart'])

@app.route('/homepage/additem', methods=['POST'])
def additem():
    if 'phone_number' not in session:
        return redirect("/")
    if request.method == 'POST':
        item = request.form['item']
        cur.execute('SELECT quantity FROM products WHERE item=%s', (item,))
        x = cur.fetchone()
        if x and x[0] > 0:
            if 'cart' not in session:
                session['cart'] = {}
            if item in session['cart']:
                if session['cart'][item]==x[0]:
                    return redirect('/homepage')
                session['cart'][item] += 1
            else:
                session['cart'][item] = 1
            '''cur.execute('UPDATE products SET quantity=quantity-1 WHERE item=%s', (item,))'''
            conn.commit()
        return redirect('/homepage')

@app.route('/homepage/removeitem', methods=['POST'])
def removeitem():
    if 'phone_number' not in session:
        return redirect("/")
    if request.method == 'POST':
        item = request.form['item']
        cur.execute('SELECT quantity FROM products WHERE item=%s', (item,))
        x = cur.fetchone()
        if x and x[0] >= 0:
            if 'cart' not in session:
                session['cart'] = {}
            if item in session['cart'] and session['cart'][item]>0:
                session['cart'][item] -= 1
                '''cur.execute('UPDATE products SET quantity=quantity+1 WHERE item=%s', (item,))'''
                if session['cart'][item]==0:
                    del session['cart'][item]
                conn.commit()
            else:
                pass
            
        return redirect('/homepage')




@app.route('/bill',methods=['GET','POST'])
def bill():
    if 'phone_number' not in session:
        return redirect("/")
    #better use a temp table cart which gets deleted at end of payment
    cur.execute('create table if not exists cart(itemname varchar(20), quantity int, price int null) ')
    for i in session['cart']:
        cur.execute('insert into cart(itemname,quantity) values(%s,%s)',(i,session['cart'][i]))
        conn.commit()
        cur.execute('SELECT price FROM products WHERE item=%s', (i,))
        price = cur.fetchone()
        cur.execute('update cart set price=%s where itemname=%s',(price[0],i))
        conn.commit()

    cur.execute('select SUM(quantity*price) from cart')
    total=cur.fetchone()
    cur.execute("select * from cart")
    bill=cur.fetchall()
    cur.execute('Drop table cart')
    conn.commit()
    if total[0] is not None and total[0]>=200 :
        return render_template('bill.html',bill=bill,total=total)
    else:
        return redirect('/addmoreitem')
    
@app.route('/addmoreitem', methods=["POST","GET"])
def addmoreitem():
    if 'phone_number' not in session:
        return redirect("/")
    if request.method=="POST":
        return redirect('/homepage') 
    else:
        return render_template("addmoreitem.html")   

    
@app.route('/payment',methods=['GET','POST'])
def payment():

    if request.method=='POST':
        return render_template('payment.html')

@app.route('/processing', methods=['GET', 'POST'])
def processing():
    if request.method == "POST" and session['phone_number']!='':
        # Insert order into successfullorders
        cur.execute('INSERT INTO successfullorders(phone_number, orderplacetime) VALUES (%s, NOW())', (session['phone_number'],))
        conn.commit()
         
        # Fetch the latest billnumber for the given phone number
        cur.execute('SELECT billnumber FROM successfullorders WHERE phone_number = %s ORDER BY orderplacetime DESC LIMIT 1', (session['phone_number'],))
        x = cur.fetchone()
        billno = x[0]
        for k in session['cart']: 
            cur.execute('INSERT INTO orderitems (orderid, product, quantity) VALUES (%s, %s, %s)',(billno, k, session['cart'][k]))
            conn.commit()

        # Use a separate cursor for creating the table
        '''create_table_cursor = conn.cursor()
        create_table_cursor.execute(f'drop table if exists `{billno}`')
        create_table_cursor.execute(f'CREATE TABLE `{billno}` (itemname VARCHAR(20), quantity INT, price INT)')
        create_table_cursor.close()
        conn.commit()

        # Insert items into the new table and update prices
        for item_name, quantity in session['cart'].items():
            cur.execute(f'INSERT INTO `{billno}` (itemname, quantity) VALUES (%s, %s)', (item_name, quantity))
            conn.commit()
            
            # Fetch the price of the item from owneritems
            cur.execute('SELECT price FROM products WHERE item = %s', (item_name,))
            price = cur.fetchone()
            
            # Update the price in the new table
            cur.execute(f'UPDATE `{billno}` SET price = %s WHERE itemname = %s', (price[0], item_name))
            conn.commit()
'''
        # Clear the cart
        for k in session['cart']:
            qty = session['cart'][k]
            cur.execute("UPDATE products SET quantity = quantity - %s WHERE item = %s", (qty, k))
            # Update BST
            update_bst_quantity(bst_root, k, qty)
            conn.commit()

        cur.execute(f'select p.item, o.quantity, p.price from orderitems o join products p on o.product=p.item where orderid=%s',(billno,))
        bill=cur.fetchall()
        cur.execute('SELECT SUM(o.quantity * p.price) FROM orderitems o, products p WHERE o.product = p.item AND o.orderid = %s',(billno,))
        a=cur.fetchall()
        total=a[0]
       

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        cur.execute("select email from customers where phone_number = %s",(session['phone_number'],))
        em=list(cur.fetchone())
        msg["To"] = em[0]
        msg["Subject"] = "Your Order Summary - Thank you for shopping!"

        # Order summary body
        order_list = "\n".join([f"{i[0]}   {i[1]} x Rs.{i[2]} " for i in bill])
        body = f"""Hello,\nThank you for your order! Here is your summary: \nBill no. {billno}\n\nItem     (Quantity x Price)\n\n{order_list}\n\nTOTAL PRICE: {total[0]}\n\nWe will process your order shortly.
        """

        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail server and send
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, em[0], msg.as_string())
        server.quit()

        session['cart'] = {}
        session['phone_number']=''
        return render_template('processing.html',billno=billno)
    else:
        return redirect('/')

@app.route('/ordersummary/<int:billnumber>',methods=['GET','POST'])
def billing(billnumber):
    
    '''cur.execute("select * from `%s`",(billnumber,))
    
    bill=cur.fetchall()
    cur.execute('select SUM(quantity*price) from `%s`',(billnumber,))
    total=cur.fetchall()  
    return render_template('bill.html',bill=bill,total=total)#copy the code to display bill in owner module an use it here
    '''
    cur.execute(f'select p.item, o.quantity, p.price from orderitems o join products p on o.product=p.item where orderid=%s',(billnumber,))
    bill=cur.fetchall()
    cur.execute('SELECT SUM(o.quantity * p.price) FROM orderitems o, products p WHERE o.product = p.item AND o.orderid = %s',(billnumber,))
    a=cur.fetchall()
    total=a[0]
    return render_template('ordersummary.html',bill=bill,total=total)

@app.route('/updateitem',methods=['GET','POST'])
def updateitem():
    if request.method=='POST':
        item=request.form["item"]
        q=int(request.form['quantity'])
        p=request.form['price']
        cur.execute("update products set quantity= %s, price = %s where item=%s",(q,p,item))
        update_bst_quantity(bst_root, item, q, p)
        conn.commit()
    cur.execute("select item, quantity, price from products")
    prod=cur.fetchall()
    return render_template('Owner-updateitem.html',prod=prod)


@app.route('/view_orderitems', methods=['GET'])
def view_orderitems():
    # Check if the user is logged in as the owner
    if 'username' in session and session['username'] == 'Hari':
        # Fetch all order items, ordered by orderid
        cur.execute('SELECT orderid, product, quantity FROM orderitems ORDER BY orderid')
        orderitems = cur.fetchall()

        # Group items by orderid
        orders = {}
        for orderid, product, quantity in orderitems:
            if orderid not in orders:
                orders[orderid] = []
            orders[orderid].append({'product': product, 'quantity': quantity})

        # Render the orders in the template
        return render_template('view_orderitems.html', orders=orders)
    else:
        flash=("Login as an owner first")
        return redirect('/ownerlogin',error=flash)
    
@app.route('/view_customer_orders/<int:phone_number>', methods=['GET'])
def view_customer_orders(phone_number):
    # Check if the user is logged in as the owner
    if 'username' in session and session['username'] == 'Hari':
        # Join the successfullorders and customers tables based on the phone_number
        query = '''
            SELECT so.billnumber, so.orderplacetime, so.expectedby,
                   c.name, c.address, c.phone_number , c.email
            FROM successfullorders so
            JOIN customers c ON so.phone_number = c.phone_number
            WHERE c.phone_number = %s
            ORDER BY so.orderplacetime ASC
        '''
        cur.execute(query, (phone_number,))
        orders = cur.fetchall()

        # Render the orders in the template
        return render_template('view_customer_orders.html', orders=orders)
    else:
        flash = "Login as an owner first"
        return redirect('/ownerlogin',error=flash)


cur.execute('select * from successfullorders where expectedby is null order by orderplacetime')
table=cur.fetchall()
queue=CircularQueue()
for i in table:
    queue.enqueue(i)

@app.route('/updateorders',methods=['GET','POST'])
def updateorders():
    print(session)
    if 'username' in session and session['username'] == 'Hari':
        if request.method=='POST':
            print("inside post")
            eb_str=request.form['expectedby']
            eb = datetime.strptime(eb_str, "%Y-%m-%d")
            bn=request.form['bn']
            print(bn)
            cur.execute('UPDATE successfullorders SET expectedby = %s WHERE billnumber = %s', (eb, bn))
            conn.commit()
            cur.execute('select * from successfullorders where billnumber=%s',(bn,))
            os=cur.fetchone()
            msg = MIMEMultipart()
            msg["From"] = EMAIL_ADDRESS
            cur.execute("select email from customers where phone_number = %s",(os[1],))
            em=list(cur.fetchone())
            msg["To"] = em[0]
            msg["Subject"] = "Delivery Date Update- Thank you for shopping!"

            # Order summary body
            
            body = f"""Hello,\nThank you for your order! Here is your Update:\n\nBill No.  Phone No. OrderPlaced ExpectedDate\n\n{os[0]}      {os[1]}    {os[2]}    {os[3]}\n\nnWe will deliver your order before the expected Date.
            """

            msg.attach(MIMEText(body, "plain"))

            # Connect to Gmail server and send
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, em[0], msg.as_string())
            server.quit()

        if queue.isempty():
            return render_template('emptyqueue.html')
        else:
            # Attempt to dequeue the current order
            current_element = queue.dequeue()
            
            # Ensure current_element is not None
            if current_element is None:
                return render_template('emptyqueue.html')
            
            # Fetch order items
            cur.execute("SELECT * FROM orderitems WHERE orderid = %s", (current_element[0],))
            bill = cur.fetchall()
            
            # Calculate total price
            cur.execute('SELECT SUM(o.quantity * p.price) FROM orderitems o, products p WHERE o.product = p.item AND o.orderid = %s', (current_element[0],))
            result = cur.fetchone()
            
            # If result is None, set total to 0
            total = result
            

            cur.execute('Select * from customers where phone_number = (select phone_number from successfullorders where billnumber= %s)',(current_element[0],))
            adr=cur.fetchone()
            return render_template('ownersite.html', ce=current_element, bill=bill, total=total , adr=adr)
    else:
        flash = "Login as an owner first"
        return redirect('/ownerlogin',error=flash)




'''


cur.execute('select * from successfullorders where expectedby is null order by orderplacetime')
table=cur.fetchall()
print(table)
queue=CircularQueue()


@app.route('/ownersite', methods=['GET', 'POST'])
def addexpectedtime():
    if 'username' in session and session['username'] == 'Hari':
        if request.method == 'POST':
            a = request.form['input1']
            id = session.get('current_id')
            
            # Update expected time
            cur.execute('UPDATE successfullorders SET expectedby = %s WHERE billnumber = %s', (a, id))
            conn.commit()
            return redirect('/ownersite')
        else:
            if queue.isempty():
                return render_template('emptyqueue.html')
            else:
                # Attempt to dequeue the current order
                current_element = queue.dequeue()
                
                # Ensure current_element is not None
                if current_element is None:
                    return render_template('emptyqueue.html')
                
                session['current_id'] = current_element[0]
                
                # Fetch order items
                cur.execute("SELECT * FROM orderitems WHERE orderid = %s", (current_element[0],))
                bill = cur.fetchall()
                
                # Calculate total price
                cur.execute('SELECT SUM(o.quantity * p.price) FROM orderitems o, products p WHERE o.product = p.item AND o.orderid = %s', (current_element[0],))
                result = cur.fetchone()
                
                # If result is None, set total to 0
                total = result[0] if result and result[0] is not None else 0
                
                return render_template('ownersite.html', ce=current_element, bill=bill, total=total)
    else:
        flash = "Login as an owner first"
        return redirect('/ownerlogin')



@app.route('/customer/tracking/<int:billnumber>',methods=['GET','POST'])
def tracking(billnumber):
    cur.execute('select * from successfullorders where billnumber=%s',(billnumber,))
    track=cur.fetchall()
    current_time=datetime.datetime.now()
    expectedtime=track[0][3]

    timeleft=expectedtime-current_time
    if timeleft.seconds < 0:
        timeleft = datetime.timedelta(0)

    # Extract the difference in days, seconds, and microseconds
    seconds = timeleft.seconds
    days=timeleft.days
    print('sec',seconds)
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    return render_template('tracking.html', h=hours,d=days,m=minutes )
'''
if __name__=="__main__":
    app.run(debug=True,port=5001)

conn.close()















'''
'''