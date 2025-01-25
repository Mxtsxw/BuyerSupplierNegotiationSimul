from flask import Flask, render_template

from agents.buyer import BuyerAgent
from agents.supplier import SupplierAgent
from negotitation.strategy import DestinationEnum, CompanyEnum

app = Flask(__name__)

s = SupplierAgent(name="Supplier1")
b = BuyerAgent(
    name="Buyer1",
    constraints={
        "max_price": 800,
        "destination": DestinationEnum.PARIS,
        "last_date": "2021-12-01"
    },
    preferences={
        "budget": 100,
        "preferred_company": CompanyEnum.RAYAN_AIR
    }
)

@app.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html',
        supplier=s.to_dict(),
        buyers=[b.to_dict()],
        logs=[]
    )

if __name__ == '__main__':
    app.run(debug=True)
