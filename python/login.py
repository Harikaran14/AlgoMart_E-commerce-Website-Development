import mysql.connector as m

# Establishing the connection to the database
conn = m.connect(user='root', host='localhost', passwd='1234', database='db2')
cursor = conn.cursor()

# Create the users table if it does not exist
cursor.execute("CREATE TABLE IF NOT EXISTS users (phone_number BIGINT PRIMARY KEY, password VARCHAR(50))")

# Commit changes
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

# Function to sign up a user
def sign_up(phone_number, password):
    # Check if user already exists in the database
    a = 'SELECT * FROM users WHERE phone_number = %s'
    b = (phone_number,)
    cursor.execute(a, b)
    if cursor.fetchone():
        return "User already exists!"

    # Insert new user into the database
    a = 'INSERT INTO users (phone_number, password) VALUES (%s, %s)'
    b = (phone_number, password)
    cursor.execute(a, b)
    conn.commit()

    # Insert new user into the tree
    bst.insert(phone_number, password)
    return "Sign-up successful!"

# Function to log in a user
def log_in(phone_number, password):
    # Search for user in the tree
    user_node = bst.search(phone_number)
    if user_node and user_node.password == password:
        return "Login successful!"
    else:
        return "Invalid phone number or password!"

# Initialize the BST and populate it with existing users from the database
bst = UserBST()
cursor.execute('SELECT phone_number, password FROM users')
for row in cursor.fetchall():
    bst.insert(row[0], row[1])

# Example sign-up and login
print(sign_up(1234567890, "password123"))
print(sign_up(1234567890, "password123"))  # Should return "User already exists!"
print(log_in(1234567890, "password123"))   # Should return "Login successful!"
print(log_in(1234567890, "wrongpassword")) # Should return "Invalid phone number or password!"

# Close the connection
conn.close()
