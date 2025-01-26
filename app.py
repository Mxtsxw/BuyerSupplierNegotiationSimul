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

buyers_list = [default_buyer]

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
    offer = {"name": "flight_1", "type": "flight", "price": 300}

    Logger.log(default_buyer.negotiate(default_supplier, "flight", offer))

    return render_template(
        'index.html',
        supplier=default_supplier.to_dict(),
        buyers=[b.to_dict() for b in buyers_list],
        logs=Logger.logs
    )

@app.route("/logs/clear", methods=['GET'])
def clear_logs():
    Logger.clear()
    return render_template(
        'index.html',
        supplier=default_supplier.to_dict(),
        buyers=[b.to_dict() for b in buyers_list],
        logs=Logger.logs
    )

@app.route("/buyer/add", methods=['POST'])
def add_buyer():
    buyer_name = request.form.get('buyer_name')
    max_price = request.form.get('max_price')
    destination = request.form.get('destination')
    last_date = request.form.get('buyer_last_date')
    budget = request.form.get('budget')
    preferred_company = request.form.get('preferred_company')

    buyer = BuyerAgent(
        name=buyer_name,
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
    max_price = request.form.get('edit-buyer-max-price')
    destination = request.form.get('edit-buyer-destination')
    last_date = request.form.get('edit-buyer-latest-date')
    budget = request.form.get('edit-buyer-budget')
    preferred_company = request.form.get('edit-buyer-preferred-companies')

    for buyer in buyers_list:
        if buyer.id == buyer_id:
            buyer.name = buyer_name
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
    best_coalition, best_value = find_optimal_coalition_IDP(buyers_list)
    Logger.log()
    return render_template(
        'coalition.html',
        buyers=[b.to_dict() for b in buyers_list]
    )

if __name__ == '__main__':
    app.run(debug=True)
