from flask import Flask, render_template, request, redirect, url_for
import uuid

from agents.buyer import BuyerAgent
from agents.supplier import SupplierAgent
from logs.logger import Logger
from negotitation.strategy import DestinationEnum, CompanyEnum, find_optimal_coalition_IDP

app = Flask(__name__)

default_supplier = SupplierAgent(name="Supplier1",
                  services=[
        {   "id": str(uuid.uuid4()),
            "name": "flight_1",
            "type": "flight",
            "destination": DestinationEnum.PARIS,
            "price": 400
        }
    ])

default_buyer = BuyerAgent(
    name="Buyer1",
    offer=300,
    constraints={
        "max_price": 800,
        "destination": DestinationEnum.PARIS,
        "last_date": "2024-12-01"
    },
    preferences={
        "budget": 100,
        "preferred_company": CompanyEnum.RAYAN_AIR
    }
)

#buyers_list = [default_buyer]
buyers_list = [
        BuyerAgent(
            name="Buyer1",
            offer=300,
            constraints={
                "max_price": 800,
                "destination": DestinationEnum.PARIS,
                "last_date": "2021-12-01"
            },
            preferences={
                "budget": 500,
                "preferred_company": CompanyEnum.RAYAN_AIR
            }
        ),
        BuyerAgent(
            name="Buyer2",
            offer=150,
            constraints={
                "max_price": 700,
                "destination": DestinationEnum.PARIS,
                "last_date": "2021-12-01"
            },
            preferences={
                "budget": 200,
                "preferred_company": CompanyEnum.AIR_FRANCE
            }
        ),
        BuyerAgent(
            name="Buyer3",
            offer=100,
            constraints={
                "max_price": 900,
                "destination": DestinationEnum.PARIS,
                "last_date": "2021-12-01"
            },
            preferences={
                "budget": 150,
                "preferred_company": CompanyEnum.RAYAN_AIR
            }
        )
    ]

@app.route('/', methods=['GET'])
def index():
    Logger.clear()
    return render_template(
        'index.html',
        supplier=default_supplier.to_dict(),
        buyers=[b.to_dict() for b in buyers_list],
        logs=[]
    )

@app.route('/negotiate', methods=['GET'])
def negotiate():

    buyer_id = request.args.get('buyer_id')
    service_id = request.args.get('service_id')
    buyer = next((b for b in buyers_list if b.id == buyer_id), None)
    service = next((s for s in default_supplier.services if s["id"] == service_id), None)
    
    offer = {"name": service['name'], "type":service['type'] , "price": buyer.offer}

    if service['destination'] != buyer.constraints["destination"]:
        Logger.log(f"Offer rejected by supplier due to different destination")
    else:
        Logger.log(buyer.negotiate(default_supplier, service['name'] , offer))

    return render_template(
        'index.html',
        supplier=default_supplier.to_dict(),
        buyers=[b.to_dict() for b in buyers_list],
        logs=Logger.logs
    )

@app.route("/logs/clear", methods=['GET'])
def clear_logs():
    Logger.clear()
    return redirect('/')

@app.route("/service/edit", methods=['POST'])
def edit_service():
    service_id = request.form.get('edit-service-id')
    service_name = request.form.get('edit-service-name')
    service_type = request.form.get('edit-service-type')
    service_destination = request.form.get('edit-service-destination')
    service_price = request.form.get('edit-service-price')

    for service in default_supplier.services:
        if service["id"] == service_id:
            service["name"] = service_name
            service["type"] = service_type
            service["destination"] = service_destination
            service["price"] = float(service_price)
            break
    return redirect('/')

@app.route("/buyer/add", methods=['POST'])
def add_buyer():
    buyer_name = request.form.get('buyer_name')
    max_price = request.form.get('max_price')
    offered_price= request.form.get('offer')
    destination = request.form.get('destination')
    last_date = request.form.get('buyer_last_date')
    budget = request.form.get('budget')
    preferred_company = request.form.get('preferred_company')

    buyer = BuyerAgent(
        name=buyer_name,
        offer=float(offered_price),
        constraints={
            "max_price": float(max_price),
            "destination": destination,
            "last_date": last_date
        },
        preferences={
            "budget": float(budget),
            "preferred_company": preferred_company,
        }
    )
    buyers_list.append(buyer)
    for elem in buyers_list:
        print (elem.to_dict())
    return redirect('/')

@app.route("/service/add", methods=['POST'])
def add_service():
    service_id = str(uuid.uuid4())
    service_name = request.form.get('service_name')
    service_type = request.form.get('service_type')
    service_destination = request.form.get('service_destination')
    service_price = request.form.get('service_price')

    default_supplier.add_service({
        "id": service_id,
        "name": service_name,
        "type": service_type,
        "destination": service_destination,
        "price": float(service_price)
    })
    return redirect('/')

@app.route("/buyer/edit", methods=['POST'])
def edit_buyer():
    buyer_id = request.form.get('edit-buyer-id')
    buyer_name = request.form.get('edit-buyer-name')
    offered_price = request.form.get('edit-buyer-offer')
    max_price = request.form.get('edit-buyer-max-price')
    destination = request.form.get('edit-buyer-destination')
    last_date = request.form.get('edit-buyer-latest-date')
    budget = request.form.get('edit-buyer-budget')
    preferred_company = request.form.get('edit-buyer-preferred-companies')

    for buyer in buyers_list:
        if buyer.id == buyer_id:
            buyer.name = buyer_name
            buyer.offer = float(offered_price)
            buyer.constraints = {
                "max_price": float(max_price),
                "destination": destination,
                "last_date": last_date
            }
            buyer.preferences = {
                "budget": float(budget),
                "preferred_company": preferred_company,
            }
            break
    return redirect('/')
    

@app.route("/buyer/remove", methods=['POST'])
def remove_buyer():
    buyer_id = request.form.get('remove-buyer-id')
    for buyer in buyers_list:
        if buyer.id == buyer_id:
            buyers_list.remove(buyer)
            break
    return redirect('/')

@app.route("/service/remove", methods=['POST'])
def remove_service():
    service_id = request.form.get('remove-service-id')
    default_supplier.remove_service(service_id)
    return redirect('/')



@app.route("/coalition", methods=['GET'])
def coalition():
    # Find the optimal coalition
    best_coalition, best_value, message = find_optimal_coalition_IDP(buyers_list)
    Logger.log(message)
    Logger.log("=== Résultat Optimal ===")
    Logger.log(f"Coalition optimale: {[agent.name for agent in best_coalition]}")
    Logger.log(f"Valeur optimale: {best_value}")
    return render_template(
        'index.html',
        supplier=default_supplier.to_dict(),
        buyers=[b.to_dict() for b in buyers_list],
        logs=Logger.logs
    )

if __name__ == '__main__':
    app.run(debug=True)
