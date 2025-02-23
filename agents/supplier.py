from logs.logger import Logger
from negotitation.strategy import supplier_evaluate_offer, ServiceTypeEnum, MessageTypeEnum

class SupplierAgent:
    """
    This class represents a supplier
    """

    def __init__(self, name=None, services=None):
        self.name = name
        self.services = services if services else []

    def add_service(self, service):
        self.services.append(service)

    def get_services(self):
        return self.services
    
    def remove_service(self, service_id):
        self.services = [s for s in self.services if s["id"] != service_id]
        

    def to_dict(self):
        return {
            'name': self.name,
            'services': self.services
        }

    def get_service(self, service_name):
        for service in self.services:
            if service['name'] == service_name:
                return service
        return None

    def negotiate(self, buyer, offer: dict):
        """
        Negotiate with a buyer.

        @param buyer: BuyerAgent instance
        @param offer: Offer from the buyer (e.g., {"type": "flight", "price": 100})

        @return: Response to the buyer's offer
        """
        Logger.log(f"Supplier {self.name} received an offer from Buyer {buyer.name}: {offer}")

        # Find the matching service in the catalog
        service = self.get_service(offer["name"])

        if not service:
            Logger.log(f"Supplier {self.name}: Service '{offer['type']}' not found.")
            return {"status": "rejected", "reason": "Service not found"}

        # Evaluate the offer using the strategy
        response = supplier_evaluate_offer(service, offer)
        Logger.log(f"Supplier {self.name}: Response to offer: {response}")
        return response