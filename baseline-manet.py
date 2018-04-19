#!/usr/bin/env python3
# Authors: James Halvorsen
# Description: Very simple stupid MANET simulator.
# This is the Baseline MANET which implements no special forwarding behavior.
# Expect for it to perform the worst, as it does not have any means of ensuring
# that packets do not reach "black hole" nodes.

import networkx as nx
import random

# A global object for storing all network adjacencies and paths.
# We assume that every device knows the full network topology, for simplicity.
NETWORK = nx.Graph()

# A simple message with a sender, intended receiver, data, and a history of the
# indices of recipients who have forwarded on this message. The src and dst
# fields are the indices of the original sender and intended recipient.
class Message:
    def __init__(self, src, dst, content):
        self.src = src
        self.dst = dst
        self.content = content
        self.history = []
    
    # Mark a message as having been sent by a device.
    def postmark(self, index):
        self.history.append(index)
    
    # Report if any of the elements in a path are in the message's history.
    def has_cycles_in(self, path):
        for index in path:
            if index in self.history:
                return True
        return False

# Every node in the network has an index and an associated device.
# The index is how the device is found in the global NETWORK object.
# The device is an actor that creates, receives, and acts upon messages.
# Every device has a set level of "greed", indicating how likely it is to behave
# selfishly. A value of 0 means never, 1 means always, in between is random.
class Device:
    def __init__(self, index, greed):
        self.index = index
        self.greed = greed
    
    # Forwards a message to the best receiver possible.
    # In other implementations, this is where we would place our "trust" system.
    # In all implementations, we are assuming we have already made the decision
    # to forward the packet. Nodes that are selfish won't call this method.
    # Returns the next hop in the message's path, or None if dropped.
    def forward_msg(self, msg):
        # Always forward to the intended recipient if possible.
        if NETWORK.has_edge(self.index, msg.dst):
            msg.postmark(self.index)
            NETWORK.nodes[msg.dst]["device"].receive_msg(msg)
            return msg.dst
    
        # Find a path that does not return to a previously visited node.
        spl = nx.shortest_path_length(NETWORK, self.index, msg.dst)
        paths = nx.all_simple_paths(NETWORK, self.index, msg.dst, cutoff=3+spl)
        options = [p for p in list(paths) if not msg.has_cycles_in(p)]

        # If none exist, drop the packet. This should not happen.
        if len(options) == 0:
            return None
    
        # Otherwise, randomly select a path.
        # If we were less trustworthy, we might be more selective here.
        choice = random.choice(options)
        next_hop = choice[1]
    
        # Send the message on its merry way.
        msg.postmark(self.index)
        NETWORK.nodes[next_hop]["device"].receive_msg(msg)
        return next_hop
    
    # Called by other devices sending this device a message.
    # Here we decide whether to forward or drop a packet, or to do something
    # with it, as we are the intended recipient.
    def receive_msg(self, msg):
        # NOTE: we may want to consider sending a return message as a means to
        # inform our sender that we got their packet. This can be used to update
        # trust scores in our "trusty" implementation.
        if msg.dst == self.index:
            print("Received a packet:", msg.content)
        elif random.random() >= self.greed:
            self.forward_msg(msg)
        else:
            print("Packet eaten by black hole")
    
    # Create a new message to a random destination, and send it off.
    def produce_msg(self):
        # Select a random destination other than ourselves.
        destinations = [i for i in NETWORK.nodes if i != self.index]
        dst = random.choice(destinations)
        src = self.index
    
        # Create a message and send it off into the ethers.
        msg = Message(src, dst, "a")
        self.forward_msg(msg)

# Setup network connections
black_holes = [1,2,8,11,22]
for i in range(0, 26):
    greed = float(i in black_holes)
    NETWORK.add_node(i, device=Device(i, greed))

NETWORK.add_edges_from([
    ( 0,  1), ( 0,  2), ( 0,  4), ( 0, 14), ( 0, 16), ( 0, 21),
    ( 1,  2), ( 1,  3), ( 1,  4), ( 1,  5), ( 1, 15), ( 1, 16),
    ( 2,  4), ( 2, 12), ( 2, 14), ( 2, 21), ( 3,  5), ( 3, 13),
    ( 3, 15), ( 3, 17), ( 4,  6), ( 4, 12), ( 5,  7), ( 5, 11),
    ( 5, 13), ( 6,  8), ( 6, 10), ( 6, 18), ( 7,  9), ( 7, 11),
    ( 8, 10), ( 8, 18), ( 9, 11), ( 9, 19), ( 9, 22), ( 9, 25),
    (10, 12), (11, 13), (11, 18), (11, 19), (11, 24), (12, 14),
    (13, 15), (13, 17), (13, 18), (14, 21), (15, 16), (15, 17),
    (16, 21), (17, 18), (18, 19), (18, 24), (19, 20), (19, 22),
    (19, 24), (20, 22), (20, 23), (22, 23), (22, 25), (23, 25)
])


# Example of how a message might be sent.
# Note that we will need a proper benchmark, perhaps by iterating over every
# device, having it produce and send a message, and testing how many packets
# reach their intended recipient.
NETWORK.nodes[1]["device"].produce_msg()
NETWORK.nodes[2]["device"].produce_msg()
