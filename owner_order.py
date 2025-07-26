from flask import Flask, render_template, request, url_for, redirect, jsonify, session
import mysql.connector as m
import ctypes

# Initialize Flask app (if this is part of a larger app, ensure proper initialization elsewhere)
app = Flask(__name__)

# Database connection
conn = m.connect(host='localhost', user='root', password='1234', database='db2')
cur = conn.cursor()
try:
    cur.execute('create table if not exists successfullorders( billnumber int AUTO_INCREMENT primary key , username varchar(50) not null, orderplacetime datetime ,expectedby int null)')
except:
    pass

class CircularQueue:
    def __init__(self, cap=20):
        self.cap = cap
        self.front = 0
        self.rear = 0
        self.item = (ctypes.py_object * cap)()

    def next(self, pos):
        return (pos + 1) % self.cap

    def isfull(self):
        return self.front == self.next(self.rear)

    def isempty(self):
        return self.front == self.rear

    def enqueue(self, value):
        if self.isfull():
            self.inc_resize()
        self.item[self.rear] = value
        self.rear = self.next(self.rear)

    def __str__(self):
        if self.front <= self.rear:
            return str(self.item[self.front:self.rear])
        else:
            return str(self.item[self.front:self.cap] + self.item[0:self.rear])

    def __iter__(self):
        current = self.front
        while current != self.rear:
            yield self.item[current]
            current = self.next(current)

    def dequeue(self):
        if self.isempty():
            return "The queue is empty"
        value = self.item[self.front]
        self.item[self.front] = None
        self.front = self.next(self.front)
        return value

    def inc_resize(self):
        new_cap = 2 * self.cap
        new_items = (ctypes.py_object * new_cap)()
        i = 0
        while not self.isempty():
            new_items[i] = self.dequeue()
            i += 1
        self.item = new_items
        self.cap = new_cap
        self.front = 0
        self.rear = i

def initialize_from_database():
    cq = CircularQueue()
    conn = m.connect(host='localhost', user='root', password='1234', database='db2')
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT o.id AS order_id, o.phone_number, o.total_amount, o.order_date, o.user_name, o.expected_delivery_time,
                   oi.vegetable_name, oi.quantity, oi.price
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            ORDER BY o.order_date ASC, o.id, oi.id
        """)
        orders = cur.fetchall()

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

        for order in grouped_orders.values():
            if not order['expected_delivery_time']:
                cq.enqueue(order)
    except Exception as e:
        print(f"Error fetching orders: {e}")
    finally:
        cur.close()
        conn.close()
    return cq

