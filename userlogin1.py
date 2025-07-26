import mysql.connector as m

def get_db_connection():
    return m.connect(user='root', host='localhost', passwd='1234', database='db2')

class TreeNode:
    def __init__(self, username, phone_number, password):
        self.username = username
        self.phone_number = phone_number
        self.password = password
        self.left = None
        self.right = None

class UserBST:
    def __init__(self):
        self.root = None

    def insert(self, username, phone_number, password):
        if self.root is None:
            self.root = TreeNode(username, phone_number, password)
        else:
            self._insert(self.root, username, phone_number, password)

    def _insert(self, node, username, phone_number, password):
        if int(phone_number) < node.phone_number:
            if node.left is None:
                node.left = TreeNode(username, phone_number, password)
            else:
                self._insert(node.left, username, phone_number, password)
        elif int(phone_number) > node.phone_number:
            if node.right is None:
                node.right = TreeNode(username, phone_number, password)
            else:
                self._insert(node.right, username, phone_number, password)

    def search(self, phone_number):
        return self._search(self.root, phone_number)

    def _search(self, node, phone_number):
        if node is None or node.phone_number == phone_number:
            return node
        elif int(phone_number) < int(node.phone_number):
            return self._search(node.left, phone_number)
        else:
            return self._search(node.right, phone_number)

# Function to sign up a user
def initialize_bst():
    bst = UserBST()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('create table users (username varchar(30) not null , phone_number varchar(10) unique, password varchar(30))')
    except:
        pass        
    cursor.execute('SELECT username, phone_number, password FROM users')
    for row in cursor.fetchall():
        bst.insert(row[0], row[1], row[2])
    cursor.close()
    conn.close()
    return bst
def sign_up(username, phone_number, password, bst):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists in the database
    cursor.execute('SELECT * FROM users WHERE phone_number = %s', (phone_number,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return "User already exists!"

    # Insert new user into the database
    cursor.execute('INSERT INTO users (username, phone_number, password) VALUES (%s, %s, %s)', (username, phone_number, password))
    conn.commit()
    cursor.close()
    conn.close()

    # Insert new user into the tree
    bst.insert(username, phone_number, password)
    return "Sign-up successful!"

# Function to log in a user
def log_in(phone_number, password, bst):
    # Search for user in the tree
    user_node = bst.search(int(phone_number))
    if user_node and user_node.password == password:
        print(user_node.phone_number)
        return True
    else:
        return False


