import socket
import json
from threading import Thread
import random

# Classe de base pour tous les agents
class Agent:
    def __init__(self, agent_id, agent_type):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.communication_port = None  # Port utilisé pour la communication

    def communicate(self, message, target_host, target_port):
        """Envoie un message à un autre agent via socket."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((target_host, target_port))
                s.sendall(json.dumps(message).encode('utf-8'))
                response = s.recv(1024)
                return json.loads(response.decode('utf-8'))
        except (ConnectionRefusedError, ConnectionResetError):
            return {"status": "error", "message": "Connection error"}


# Classe pour les agents fournisseurs
class SupplierAgent(Agent):
    def __init__(self, agent_id):
        super().__init__(agent_id, "Supplier")
        self.services = []  # Liste des services proposés par le fournisseur

    def add_service(self, service):
        """Ajoute un service au catalogue du fournisseur."""
        self.services.append(service)

    def negotiate(self,buyer_id,offer):
        """Logique de négociation pour les fournisseurs."""
        service = next((s for s in self.services if s["type"] == offer["type"]), None)
        if service :
            interval = abs(offer["price"] - service["price"]) / service["price"] * 100
            if interval > 40:
                return {"buyer_id": buyer_id, "status": "rejected", "message": "Offer too far from expected price"}
            #si l'offre est plus basse que le prix, proposer une contre offre avec une légère augmentation
            if offer["price"] < service["price"]:
                counter_price = offer["price"] * 1.05  # augmentation de 5%
                if counter_price > service["price"]:
                    counter_price = service["price"]
                counter_offer = {"type": offer["type"], "price":  round(counter_price, 2)}
                print(f"Counter offer: {counter_offer} proposed by {self.agent_id}")
                return {"buyer_id": buyer_id, "status": "counter_offer",
                        "message": f"Counter offer from {self.agent_id}", "offer": counter_offer}
            else:
                return {"buyer_id": buyer_id, "status": "accepted", "message": f"Offer accepted by {self.agent_id}"}

        else:
            return {"buyer_id": buyer_id, "status": "rejected", "message": f"Service not found in {self.agent_id}"}



# Classe pour les agents acheteurs
class BuyerAgent(Agent):
    def __init__(self, agent_id):
        super().__init__(agent_id, "Buyer")
        self.preferences = {}  # Préférences de l'acheteur
        self.constraints = {}  # Contraintes de l'acheteur

    def set_preferences(self, preferences):
        """Définit les préférences de l'acheteur."""
        self.preferences = preferences

    def set_constraints(self, constraints):
        """Définit les contraintes de l'acheteur."""
        self.constraints = constraints

    def negotiate(self,supplier_id,offer,supplier_host,supplier_port):
        """Logique de négocaiton pour les acheteurs."""
        message = {"source_id": self.agent_id, "target_id": supplier_id,
                   "content": {"action": "negotiate", "offer": offer}}

        response = self.communicate(message, supplier_host, supplier_port)

        if response.get("status") == "counter_offer":
            #Vérifie les contraintes avant d'accepter  l'offre
            counter_offer = response["offer"]
            if counter_offer["price"] <= self.constraints["max_price"]:
                print(f"Counter offer: {counter_offer} accepted by {self.agent_id}")
                return {"status": "accepted", "message": "Counter-offer accepted"}
            else:
                #si la contre-offre dépasse le budget, on propose une offre avec une légère réduction
                adjusted_offer = {"price": self.constraints["max_price"] * 0.95,"type": counter_offer["type"]}  # réduction de 5%
                print(f"Counter offer rejected. New Adjusted offer: {adjusted_offer} proposed by {self.agent_id}")
                #return {"status": "counter_offer", "message": "New offer sent", "offer": adjusted_offer}
                return self.negotiate(supplier_id, adjusted_offer, supplier_host, supplier_port)

        elif response.get("status") == "accepted":
            # Si l'offre initiale est acceptée, vérifier les contraintes
            if offer["price"] <= self.constraints["max_price"]:
                print(f"Offer: {offer} accepted by {self.agent_id}")
                return {"status": "accepted", "message": "Offer accepted"}
            else:
                print(f"Offer: {offer} rejected by {self.agent_id} due to constraints")
                return {"status": "rejected", "message": "Offer rejected due to constraints"}

        else:
            print(f"Offer rejected by {self.agent_id}")
            return {"status": "rejected", "message": "Offer rejected"}




# Système de communication pour gérer les interactions entre agents
class CommunicationManager:
    def __init__(self, host='localhost', port=0):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.agents = {}

    def start(self):
        """Démarre un thread pour écouter les connexions entrantes."""
        Thread(target=self.listen_for_connections, daemon=True).start()

    def listen_for_connections(self):
        """Écoute les connexions entrantes et les traite."""
        print(f"Communication manager listening on {self.host}:{self.socket.getsockname()[1]}")
        while True:
            conn, addr = self.socket.accept()
            Thread(target=self.handle_connection, args=(conn, addr), daemon=True).start()

    def handle_connection(self, conn, addr):
        """Gère une connexion entrante."""
        try:
            data = conn.recv(1024)
            if data:
                message = json.loads(data.decode('utf-8'))
                print(f"Received message from {addr}: {message}")
                response = self.route_message(message)
                conn.sendall(json.dumps(response).encode('utf-8'))
        finally:
            conn.close()

    def register_agent(self, agent):
        """Enregistre un agent dans le système."""
        agent.communication_port = self.socket.getsockname()[1]
        self.agents[agent.agent_id] = agent

    def route_message(self, message):
        """Transmet le message au bon agent."""
        target_id = message.get("target_id")
        if target_id in self.agents:
            agent = self.agents[target_id]
            if message["content"]["action"]=="negotiate":
                return agent.negotiate(message["source_id"],message["content"]["offer"])

        return {"status": "error", "message": "Agent not found"}


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le gestionnaire de communication
    comm_manager = CommunicationManager()
    comm_manager.start()

    # Création des agents
    supplier = SupplierAgent("supplier_1")
    buyer = BuyerAgent("buyer_1")

    # Enregistrement des agents dans le gestionnaire de communication
    comm_manager.register_agent(supplier)
    comm_manager.register_agent(buyer)

    # Ajout de services et de préférences
    supplier.add_service({"type": "flight", "price": 1200, "destination": "Paris"})
    buyer.set_preferences({"preferred_companies": ["Air France"], "budget": 600})
    buyer.set_constraints({"max_price": 800, "latest_date": "2023-12-31"})


    # Négociation
    offer = {
        "type": "flight",
        "price": random.randint(int(buyer.constraints.get("max_price", 0) * 0.8), int(buyer.constraints.get("max_price", 0))),
        "destination": "Paris"
    }

    buyer_response = buyer.negotiate("supplier_1", offer, 'localhost', comm_manager.socket.getsockname()[1])
    print(f"Final negotiation response: {buyer_response}")


