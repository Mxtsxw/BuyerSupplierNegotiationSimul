# negotiation/strategy.py
def supplier_evaluate_offer(service, offer):
    """
    Evaluate an offer from a buyer and decide whether to accept, reject, or counter-offer.
    By default, the supplier will reject the offer if the price is too far from the expected price.
    If the price is lower than the expected price, the supplier will counter-offer with a higher price of 5%.
    If the price is within the expected range, the supplier will accept the offer.
    """
    if abs(offer["price"] - service["price"]) / service["price"] > 0.4:
        return {"status": "rejected", "reason": "Offer too far from expected price"}
    elif offer["price"] < service["price"]:
        counter_price = min(offer["price"] * 1.05, service["price"])
        return {"status": MessageTypeEnum.COUNTER_OFFER, "offer": {"name": offer["name"], "type": offer["type"], "price": round(counter_price, 2)}}
    else:
        return {"status": "accepted"}

def buyer_evaluate_offer(constraints, preferences, offer):
    """
    Evaluate an offer from a supplier and decide whether to accept, reject, or counter-offer.
    By default, the buyer will reject the offer if the price is too high.
    If the price is within the budget, the buyer will accept the offer.
    If the price is higher than the budget, the buyer will counter-offer with a lower price of 5%.
    """
    if offer["price"] > constraints["max_price"]:
        return {"status": "rejected", "reason": "Price too high"}
    elif offer["price"] > preferences["budget"]:
        # Lower the price to the budget by 5%
        adjusted_price = round(offer["price"] * 0.90, 2)
        return {"status": MessageTypeEnum.COUNTER_OFFER, "offer": {"name": offer["name"], "type": offer["type"], "price": adjusted_price}}
    else:
        return {"status": "accepted"}


class ServiceTypeEnum:
    FLIGHT = "flight"

class MessageTypeEnum:
    NEGOTIATION = "negotiation"
    OFFER = "offer"
    ACCEPT = "accept"
    REJECT = "reject"
    COUNTER_OFFER = "counter_offer"

class CompanyEnum:
    AIR_FRANCE = "Air France"
    RAYAN_AIR = "Rayan Air"

class DestinationEnum:
    NYC = "NYC"
    PARIS = "Paris"
    LONDON = "London"
    DUBAI = "Dubai"
