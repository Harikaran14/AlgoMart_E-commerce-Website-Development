import mysql.connector as m
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class Hashtable:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.size = 0
        self.buckets = [None] * self.capacity

    def _hash(self, key):
        hashsum = 0
        for idx, c in enumerate(key):
            hashsum += (idx + len(key)) ** ord(c)
            hashsum = hashsum % self.capacity
        return hashsum

    def put(self, key, value):
        index = self._hash(key)
        if self.buckets[index] is None:
            self.buckets[index] = Node(key, value)
            self.size += 1
        else:
            current = self.buckets[index]
            while current.next:
                if current.key == key:
                    current.value = value
                    return
                current = current.next
            if current.key == key:
                current.value = value
            else:
                current.next = Node(key, value)
                self.size += 1

    def get(self, key):
        index = self._hash(key)
        current = self.buckets[index]
        while current:
            if current.key == key:
                return current.value
            current = current.next
        return None

    def items(self):
        for bucket in self.buckets:
            current = bucket
            while current:
                yield current.key, current.value
                current = current.next

def fetch_user_orders_hash():
    conn = m.connect(user='root', host='localhost', passwd='1234', database='db2')
    user_orders_hash = Hashtable()

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, phone_number, total_amount, order_date,expected_delivery_time,user_name FROM orders")
    orders = cursor.fetchall()

    for order in orders:
        phone_number = order['phone_number']
        if user_orders_hash.get(phone_number) is None:
            user_orders_hash.put(phone_number, {})
        
        cursor.execute("SELECT vegetable_name, quantity, price FROM order_items WHERE order_id = %s", (order['id'],))
        order_items = cursor.fetchall()
        
        order_details = {
            'order_id': order['id'],
            'total_amount': order['total_amount'],
            'order_date': order['order_date'],
            'expected_delivery':order['expected_delivery_time'],
            'username':order['user_name'],
            'order_items': order_items
        }

        user_orders_hash.get(phone_number)[order['id']] = order_details

    cursor.close()
    conn.close()
    print(user_orders_hash)
    return user_orders_hash