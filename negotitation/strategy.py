# negotiation/strategy.py
import itertools

from logs.logger import Logger


def supplier_evaluate_offer(service, offer):
    """
    Evaluate an offer from a buyer and decide whether to accept, reject, or counter-offer.
    By default, the supplier will reject the offer if the price is too far from the expected price.
    If the price is lower than the expected price, the supplier will counter-offer with a higher price of 5%.
    If the price is within the expected range, the supplier will accept the offer.
    """

    # TODO : Voir si offre supérieur au prix => refus ??
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

def evaluate_offer_coalition(agent, offer):
    """
    Évalue une offre en fonction des contraintes et préférences de l'agent.

    :param agent: Dictionnaire représentant l'agent (constraints et preferences).
    :param offer: Dictionnaire représentant l'offre (price, destination, date).
    :return: Score de l'offre (plus il est élevé, mieux l'offre correspond à l'agent).
    """
    score = 0

    # Contraintes strictes (Hard Constraints)
    if offer["destination"] != agent["constraints"]["destination"]:
        return -float('inf')  # Rejeter immédiatement si la destination ne correspond pas

    if offer["price"] > agent["constraints"]["max_price"]:
        return -float('inf')  # Rejeter immédiatement si le prix dépasse le budget

    if offer["date"] > agent["constraints"]["last_date"]:
        return -float('inf')  # Rejeter immédiatement si la date dépasse la limite

    # Préférences (Soft Constraints)
    preferences = agent["preferences"]

    # Préférence pour le budget (inversement proportionnel au prix)
    if "budget" in preferences:
        max_price = agent["constraints"]["max_price"]
        price_score = 1 - (offer["price"] / max_price)  # Plus le prix est proche de 0, mieux c'est
        score += price_score * 0.6  # Pondération (60%)

    # Préférence pour la destination
    if "destination" in preferences:
        destination_score = 1  # Destination idéale, ajouter une préférence forte
        score += destination_score * 0.4  # Pondération (40%)

    return score


def coalition_value(coalition):
    """
    Calcule la valeur d'une coalition d'agents.
    Plus les contraintes et préférences des agents sont alignées, plus la valeur est élevée.
    """
    if len(coalition) == 0:
        return -float('inf')  # Une coalition vide n'a pas de valeur

    score = 0
    destinations = [agent.constraints["destination"] for agent in coalition]
    budget_limits = [agent.constraints["max_price"] for agent in coalition]
    deadlines = [agent.constraints["last_date"] for agent in coalition]

    # Vérifier si les destinations sont alignées
    if len(set(destinations)) == 1:  # Tous les agents veulent la même destination
        score += 50  # Bonus pour compatibilité de destination

    # Vérifier si les budgets permettent un partage
    if max(budget_limits) <= 800:  # Tous les agents peuvent coopérer dans le budget
        score += 30

    # Vérifier si les dates sont compatibles
    latest_date = max(deadlines)
    if all(deadline >= latest_date for deadline in deadlines):  # Toutes les dates respectées
        score += 20

    # Préférences spécifiques des agents
    for agent in coalition:
        if agent.preferences.get("budget"):
            score += 10  # Bonus si l'agent priorise le budget
        if agent.preferences.get("destination"):
            score += 20  # Bonus si l'agent priorise la destination

    return score

def find_optimal_coalition_IDP(agents):
    """
    Applique l'algorithme IDP pour trouver la coalition optimale parmi un ensemble d'agents.
    """
    n = len(agents)
    best_coalition = []
    best_value = -float('inf')

    # Explorer toutes les coalitions possibles
    for size in range(1, n + 1):  # Taille de la coalition (de 1 à n agents)
        for coalition in itertools.combinations(agents, size):  # Toutes les combinaisons de taille 'size'
            value = coalition_value(coalition)
            Logger.log(f"Coalition: {[agent.name for agent in coalition]}, Value: {value}")
            if value > best_value:
                best_value = value
                best_coalition = coalition

    return best_coalition, best_value




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
