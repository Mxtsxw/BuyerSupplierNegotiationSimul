from flask import Flask, render_template, request

from agents.buyer import BuyerAgent
from agents.supplier import SupplierAgent
from logs.logger import Logger
from negotitation.strategy import DestinationEnum, CompanyEnum, find_optimal_coalition_IDP

app = Flask(__name__)

default_supplier = SupplierAgent(name="Supplier1",
                  services=[
        {
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
    buyer = BuyerAgent(name=buyer_name)
    buyers_list.append(buyer)
    return render_template(
        'index.html',
        supplier=default_supplier.to_dict(),
        buyers=[b.to_dict() for b in buyers_list],
        logs=Logger.logs
    )

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
