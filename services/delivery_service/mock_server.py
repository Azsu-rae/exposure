# mock_payment_server.py  ← create this outside your Django project
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/payment/notify/", methods=["POST"])
def receive_notification():
    data = request.get_json()
    print(f"\n✅ Payment service received: {data}\n")
    
    if data.get("delivery_success"):
        print(f"   → Order {data['order_id']}, {data['delivery_status']}: CAPTURE payment")
    elif data.get("delivery_status") == "CANCELLED":
        print(f"   → Order {data['order_id']}, {data['delivery_status']}: CANCEL and REFUND payment")    
    else:
        print(f"   → Order {data['order_id']}, {data['delivery_status']}: hold payment")

    return jsonify({"received": True}), 200

if __name__ == "__main__":
    app.run(port=8001)