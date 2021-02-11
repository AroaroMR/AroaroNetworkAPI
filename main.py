from fastapi import FastAPI, Request
import networkx as nx
import sqlite3
import json

app = FastAPI()


class Node:
    def __init__(self, id):
        self.id = id
        self.degree = 0
        self.closeness = 0
        self.betweenness =0


@app.get("/")
async def root():
    return {"message": "Hello World"}

def retrieve_network(id):
    conn = sqlite3.connect("network_storage.db")
    cur = conn.cursor()
    cur.execute("SELECT network FROM networks WHERE id = ?", (id,))
    network_string = cur.fetchone()[0]
    conn.close()
    return json.loads(network_string)

def save_network(network_data):
    network_json = json.loads(network_data)
    network_id = network_json["network_id"]
    network_string = network_json["network"][0]

    g = nx.node_link_graph(network_string)

    degree_dict = dict(g.degree())
    closeness_dict = nx.closeness_centrality(g)
    betweenness_dict = nx.betweenness_centrality(g)

    node_list = []

    for node in g.nodes:
        temp_node = Node(node)
        temp_node.degree = round(degree_dict[node], 4)
        temp_node.closeness = round(closeness_dict[node], 4)
        temp_node.betweenness = round(betweenness_dict[node], 4)
        node_list.append(temp_node)

    node_list.sort(key=lambda x: x.id)
    network_string = json.dumps([ob.__dict__ for ob in node_list])
    conn = sqlite3.connect("network_storage.db")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO networks(id, network) VALUES (?, ?)", (network_id, network_string))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Non-Unique Network ID used")

@app.get("/networks/{network_id}")
async def get_network(network_id: str):
    try:
        network_json = retrieve_network(network_id)
        return network_json
    except TypeError:
        pass

@app.post("/networks/")
async def post_network(request: Request):
    save_network(await request.body())
    return request.body
