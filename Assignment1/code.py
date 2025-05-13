# Team Members
# 1. Akshay Santoshi : CS21BTECH11012
# 2. Nitya Bhamidipaty : CS21BTECH11041

import numpy as np
import pregel
import pandas as pd
import matplotlib.pyplot as plt

# Main Class for TrustRank
class TrustRankVertex(pregel.Vertex):
    
    def __init__(self, vertex_id, bad_sender_list, outgoing_edges, vertex_objs, damping_factor=0.85, max_iterations=50):
        
        out_vertices = []
        if vertex_id in outgoing_edges:
            out_vertices = outgoing_edges[vertex_id]
            
        if vertex_id in outgoing_edges:
            self.outgoing_edges = outgoing_edges[vertex_id]
        else:
            self.outgoing_edges = []
        
        super().__init__(vertex_id, 0, list(out_vertices))

        self.damping_factor = damping_factor # alpha
        self.max_iterations = max_iterations 
        
        # initialize the trust value of bad senders to 1/(no. of bad senders) and others to 0
        if vertex_id in bad_sender_list:
            self.bad_node = True
            self.value = 1/len(bad_sender_list)
        else:
            self.bad_node = False
            self.value = 0

        self.out_deg = 0
        self.out_deg = sum(amount for _, amount in out_vertices) # out degree is the sum of amounts of outgoing edges
            
        self.const_value = self.value # initial value
        self.vertex_objs = vertex_objs # dictionary of vertex objects needed for sending messages

    def update(self):
        if self.superstep < self.max_iterations:
            
            self.value = (1-self.damping_factor) * self.const_value + self.damping_factor* sum([trustrank for (vertex,trustrank) in self.incoming_messages])
            if self.out_deg != 0:
                self.outgoing_messages = [(self.vertex_objs[id], self.value * amount/ self.out_deg) for id, amount in self.out_vertices]
            else:
                self.outgoing_messages = []
        else:
            # stop after max_iterations supersteps
            self.active = False


if __name__ == '__main__':
    # Read the Excel file
    payments_df = pd.read_excel('Payments.xlsx')
    bad_nodes_df = pd.read_excel('bad_sender.xlsx')


    # Extract columns into separate lists
    sender_list = payments_df['Sender'].astype(int).tolist()
    receiver_list = payments_df['Receiver'].astype(int).tolist()
    amount_list = payments_df['Amount'].astype(int).tolist()
    bad_sender_list = bad_nodes_df['Bad Sender'].astype(int).tolist()

    nodes_list = list(set(sender_list + receiver_list + bad_sender_list)) # Get unique nodes

    outgoing_edges = {}

    # Replaced multiple directed edges from a node to another anoder node with single directed edge with amounts added
    for sender, receiver, amount in zip(sender_list, receiver_list, amount_list):
        if sender not in outgoing_edges:
            outgoing_edges[sender] = []
        found = False
        for i, (recv, amt) in enumerate(outgoing_edges[sender]):
            if recv == receiver:
                outgoing_edges[sender][i] = (recv, amt + amount)
                found = True
                break
        if not found:
            outgoing_edges[sender].append((receiver, amount))
            
    # Creating vertex objects
    vertices = []
    vertex_objs = {}
    for node_id in nodes_list:
        if node_id in vertex_objs:
            vertices.append(vertex_objs[node_id])
        else:
            vertex_objs[node_id] = TrustRankVertex(node_id, bad_sender_list, outgoing_edges, vertex_objs, 0.85, 50) # alpha and 50 same for all nodes
            vertices.append(vertex_objs[node_id])
            
    # Run the Pregel algorithm
    Pregel = pregel.Pregel(vertices, 4)
    Pregel.run()
    
    # Print the trust values
    trust_values = []
    df = {'Node': [], 'Trust Value': []}
    print("Node ID, Trust Value")
    for vertex in Pregel.vertices:
        print(vertex.id, vertex.value)
        trust_values.append(vertex.value) # for plotting
        df['Node'].append(vertex.id)
        df['Trust Value'].append(vertex.value)

    # Save the trust values to an Excel file
    df = pd.DataFrame(df)
    df.to_excel('TrustValuesResult.xlsx', index=False)
    

    print("\n\n\n")
    print("Bad Senders and their Trust Values")
    print("Node ID, Trust Value")
    for bad_sender in bad_sender_list: # Print the trust value of bad senders 
        print(bad_sender, vertex_objs[bad_sender].value)
        
    
    ## Plotting the histogram

    plt.hist(trust_values, bins='auto', edgecolor='black', alpha=0.7)
    plt.xlabel('Value Range')
    plt.ylabel('Frequency')
    plt.title('Histogram of Trust Values')

   
    plt.savefig('Histogram.png')
    plt.show()