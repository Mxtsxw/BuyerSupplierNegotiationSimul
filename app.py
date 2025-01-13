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
supplier.add_service({"type": "flight", "price": 1900, "destination": "Paris"})
buyer.set_preferences({"preferred_companies": ["Air France"], "budget": 600})
buyer.set_constraints({"max_price": 800, "latest_date": "2023-12-31"})

@app.route('/')
def index():
    return render_template('index.html', supplier=supplier, buyer=buyer, logs=[])

@app.route('/negotiate', methods=['POST'])
def negotiate():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    offer_type = data.get('type')
    offer_price = data.get('price')
    offer_destination = data.get('destination')
    print(offer_type, offer_price, offer_destination)

    if offer_price is None or offer_type is None or offer_destination is None:
        return jsonify({"error": "Invalid offer data"}), 400

    try :
        offer_price = int(offer_price)
    except ValueError:
        return jsonify({"error": "Invalid offer price"}), 400

    offer = {"type": data.get('type'), "price": offer_price, "destination": data.get('destination')}
    response = buyer.negotiate("supplier_1", offer, 'localhost', comm_manager.socket.getsockname()[1])

    logs = Logger.logs
    Logger.logs = []  # Clear logs after extracting

    return jsonify({"response": response, "logs": logs})

@app.route('/update_preferences_constraints', methods=['POST'])
def update_preferences_constraints():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    preferences = data.get('preferences')
    constraints = data.get('constraints')

    if preferences:
        buyer.set_preferences(preferences)
    if constraints:
        buyer.set_constraints(constraints)

    print(buyer.preferences)
    print(buyer.constraints)


    return jsonify({"status": "success", "message": "Preferences and constraints updated successfully"})

@app.route('/update_services', methods=['POST'])
def update_services():
    data = request.json
    if not data or 'services' not in data:
        return jsonify({"error": "No services data provided"}), 400

    # Update the services in the supplier
    supplier.services = data['services']


    return jsonify({"status": "success", "message": "Services updated successfully"})

@app.route('/get_preferences_constraints', methods=['GET'])
def get_preferences_constraints():
    return jsonify({"preferences": buyer.preferences, "constraints": buyer.constraints})

@app.route('/get_services', methods=['GET'])
def get_services():
    return jsonify({"services": supplier.services})



if __name__ == "__main__":
    app.run(debug=True)
