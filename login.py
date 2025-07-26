import mysql.connector as m

# Establishing the connection to the database
conn = m.connect(user='root', host='localhost', passwd='1234', database='db2')
cursor = conn.cursor()

# Create the users table if it does not exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        phone_number BIGINT PRIMARY KEY,
        username VARCHAR(50),
        password VARCHAR(50),
        address VARCHAR(255)
    )
""")

# Commit changes
conn.commit()

class TreeNode:
    def __init__(self, phone_number, username, password, address):
        self.phone_number = phone_number
        self.username = username
        self.password = password
        self.address = address
        self.left = None
        self.right = None

class UserBST:
    def __init__(self):
        self.root = None

    def insert(self, phone_number, username, password, address):
        if self.root is None:
            self.root = TreeNode(phone_number, username, password, address)
        else:
            self._insert(self.root, phone_number, username, password, address)

    def _insert(self, node, phone_number, username, password, address):
        if phone_number < node.phone_number:
            if node.left is None:
                node.left = TreeNode(phone_number, username, password, address)
            else:
                self._insert(node.left, phone_number, username, password, address)
        elif phone_number > node.phone_number:
            if node.right is None:
                node.right = TreeNode(phone_number, username, password, address)
            else:
                self._insert(node.right, phone_number, username, password, address)

    def search(self, phone_number):
        return self._search(self.root, phone_number)

    def _search(self, node, phone_number):
        if node is None or node.phone_number == phone_number:
            return node
        elif phone_number < node.phone_number:
            return self._search(node.left, phone_number)
        else:
            return self._search(node.right, phone_number)

# Function to sign up a user
def sign_up(username, phone_number, password, address, bst):
    # Check if user already exists in the database
    a = 'SELECT * FROM users WHERE phone_number = %s'
    b = (phone_number,)
    cursor.execute(a, b)
    if cursor.fetchone():
        return "User already exists!"

    # Insert new user into the database
    a = 'INSERT INTO users (username, phone_number, password, address) VALUES (%s, %s, %s, %s)'
    b = (username, phone_number, password, address)
    cursor.execute(a, b)
    conn.commit()

    # Insert new user into the tree
    bst.insert(phone_number, username, password, address)
    return "Sign-up successful!"

# Function to log in a user
def log_in(phone_number, password, bst):
    # Search for user in the tree
    user_node = bst.search(phone_number)
    if user_node and user_node.password == password:
        return True
    else:
        return False

# Initialize the BST and populate it with existing users from the database
bst = UserBST()
cursor.execute('SELECT phone_number, username, password, address FROM users')
for row in cursor.fetchall():
    bst.insert(row[0], row[1], row[2], row[3])

# Example sign-up and login
print(sign_up("John Doe", 1234567890, "password123", "123 Main St", bst))
print(sign_up("John Doe", 1234567890, "password123", "123 Main St", bst))  # Should return "User already exists!"
print(log_in(1234567890, "password123", bst))   # Should return True
print(log_in(1234567890, "wrongpassword", bst)) # Should return False

# Close the connection
conn.close()
