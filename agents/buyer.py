from logs.logger import Logger
from negotitation.strategy import buyer_evaluate_offer
import uuid


class BuyerAgent:
    """
    Base class for buyers
    """

    def __init__(self, name=None, preferences=None, constraints=None):
        self.name = name
        self.id = str(uuid.uuid4())
        self.constraints = constraints
        self.preferences = preferences

    def to_dict(self):
        return {
            'name': self.name,
            'id': self.id,
            'constraints': self.constraints,
            'preferences': self.preferences
        }

    def get_preferences(self):
        return self.preferences

    def get_constraints(self):
        return self.constraints

    def set_preferences(self, preferences):
        self.preferences = preferences

    def set_constraints(self, constraints):
        self.constraints = constraints

    def negotiate(self, supplier, service_name, offer: dict, max_exchanges=30):
        """
        Negotiate with a supplier for a specific service.

        @param supplier: SupplierAgent instance
        @param service_name: Name of the service the buyer is negotiating for
        @param offer: Initial offer dictionary (e.g., {"type": "flight", "price": 100})
        @param max_exchanges: Maximum number of negotiation exchanges

        @return: Final negotiation result
        """
        Logger.log(f"Buyer {self.name} starts negotiation with Supplier {supplier.name} for service '{service_name}'.")
        exchanges = 0  # Track the number of exchanges

        while exchanges < max_exchanges:
            exchanges += 1
            Logger.log(f"\n--- Exchange {exchanges} ---")

            # Supplier evaluates the offer
            response = supplier.negotiate(self, offer)

            if response["status"] == "accepted":
                Logger.log(f"Buyer {self.name}: Offer accepted by Supplier {supplier.name}.")
                return {"status": "accepted", "final_offer": offer, "exchanges": exchanges}

            elif response["status"] == "rejected":
                Logger.log(f"Buyer {self.name}: Offer rejected by Supplier {supplier.name}. Reason: {response['reason']}")
                return {"status": "rejected", "exchanges": exchanges}

            elif response["status"] == "counter_offer":
                counter_offer = response["offer"]
                Logger.log(f"Buyer {self.name}: Counter offer received: {counter_offer}.")

                # Buyer evaluates the counter offer
                buyer_response = buyer_evaluate_offer(self.constraints, self.preferences, counter_offer)

                if buyer_response["status"] == "accepted":
                    Logger.log(f"Buyer {self.name}: Counter offer accepted.")
                    return {"status": "accepted", "final_offer": counter_offer, "exchanges": exchanges}

                elif buyer_response["status"] == "rejected":
                    Logger.log(f"Buyer {self.name}: Counter offer rejected. Reason: {buyer_response['reason']}")
                    return {"status": "rejected", "exchanges": exchanges}

                elif buyer_response["status"] == "counter_offer":
                    # Update the offer with the new counter offer
                    offer = buyer_response["offer"]
                    Logger.log(f"Buyer {self.name}: New counter offer proposed: {offer}.")

            else:
                Logger.log(f"Buyer {self.name}: Unexpected response from Supplier {supplier.name}.")
                return {"status": "error", "exchanges": exchanges}



        # Negotiation interrupted after reaching the max exchanges
        Logger.log(f"Buyer {self.name}: Negotiation interrupted after {exchanges} exchanges.")
        return {"status": "interrupted", "reason": "Max exchanges reached", "exchanges": exchanges}