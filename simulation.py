# simulation.py
from agents.buyer import BuyerAgent
from agents.supplier import SupplierAgent
from communication.server import SocketServer
import threading

from negotitation.strategy import CompanyEnum, DestinationEnum, ServiceTypeEnum



if __name__=="__main__":

    # Create buyer and supplier
    buyer = BuyerAgent(
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
    supplier = SupplierAgent(name="Supplier1")

    # Add a service to the supplier

    supplier.add_service(
        {
            "name": "flight_1",
            "type": ServiceTypeEnum.FLIGHT, "destination": DestinationEnum.PARIS, "price": 400}
    )

    # Start negotiation
    offer = {"name": "flight_1", "type": "flight", "price": 300}
    result = buyer.negotiate(supplier, "flight", offer)

    # Output the result
    print("Negotiation Result:", result)
