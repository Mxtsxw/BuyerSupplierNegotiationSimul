import socket
import json
from threading import Thread

# Classe de base pour tous les agents
class Agent:
    def __init__(self, agent_id, agent_type):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.communication_port = None  # Port utilisé pour la communication

    def communicate(self, message, target_host, target_port):
        """Envoie un message à un autre agent via socket."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((target_host, target_port))
            s.sendall(json.dumps(message).encode('utf-8'))
            response = s.recv(1024)
        return response.decode('utf-8')


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
        # accepte si le prix est supérieur ou égal
        service = next((s for s in self.services if s["type"] == offer["type"]), None)
        if service and offer["price"] >= service["price"]:
            return {"buyer_id": buyer_id, "status": "accepted", "message": f"Offer accepted by {self.agent_id}"}
        elif service:
            #contre proposition
            counter_offer = {"price": service["price"], "type": service["type"]}
            return {"buyer_id": buyer_id, "status": "counter_offer", "message": f"Counter offer from {self.agent_id}", "offer": counter_offer}
        else:
            return {"buyer_id": buyer_id, "status": "rejected", "message": f"Offer rejected by {self.agent_id}"}


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

    def negotiate(self,supplier_id,offer):
        pass


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
            return {"status": "success", "message": f"Message routed to {target_id}"}
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
    supplier.add_service({"type": "flight", "price": 500, "destination": "Paris"})
    buyer.set_preferences({"preferred_companies": ["Air France"], "budget": 600})
    buyer.set_constraints({"max_price": 600, "latest_date": "2023-12-31"})

    # Exemple de communication (à étendre avec négociations)
    message = {
        "source_id": "buyer_1",
        "target_id": "supplier_1",
        "content": {"request": "get_services"}
    }
    print(buyer.communicate(message, 'localhost', comm_manager.socket.getsockname()[1]))

    message = {
        "source_id": "supplier_1",
        "target_id": "buyer_1",
        "content": {"response": "services", "services": supplier.services}
    }

    print(supplier.communicate(message, 'localhost', comm_manager.socket.getsockname()[1]))

