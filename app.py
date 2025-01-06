from flask import Flask, render_template, request, jsonify
from agents import SupplierAgent, BuyerAgent, CommunicationManager, Logger
import threading

app = Flask(__name__)

# Initialize agents and communication manager
comm_manager = CommunicationManager()
threading.Thread(target=comm_manager.start, daemon=True).start()

supplier = SupplierAgent("supplier_1")
buyer = BuyerAgent("buyer_1")
comm_manager.register_agent(supplier)
comm_manager.register_agent(buyer)

# Configure supplier services and buyer preferences
supplier.add_service({"type": "flight", "price": 1200, "destination": "Paris"})
buyer.set_preferences({"preferred_companies": ["Air France"], "budget": 600})
buyer.set_constraints({"max_price": 800, "latest_date": "2023-12-31"})

@app.route('/')
def index():
    return render_template('index.html', supplier=supplier, buyer=buyer, logs=[])

@app.route('/negotiate', methods=['POST'])
def negotiate():
    data = request.json
    offer = {"type": data['type'], "price": data['price'], "destination": data['destination']}


    # Assuming buyer.negotiate accepts a callback for logging
    response = buyer.negotiate("supplier_1", offer, 'localhost', comm_manager.socket.getsockname()[1])

    return jsonify({"response": response, "logs": Logger.logs})

if __name__ == "__main__":
    app.run(debug=True)
