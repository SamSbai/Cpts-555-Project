#!/usr/bin/env python3
# Authors: James Halvorsen
# Description: Very simple stupid MANET simulator.
# This is the Baseline MANET which implements no special forwarding behavior.
# Expect for it to perform the worst, as it does not have any means of ensuring
# that packets do not reach "black hole" nodes.

import networkx as nx

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
    
    def add_recipient(index):
        history.append(index)
    
    def had_recipient(index):
        return index in history

# Every node in the network has an index and an associated device.
# The index is how the device is found in the global NETWORK object.
# The device is an actor that creates, receives, and acts upon messages.
class Device:
    def __init__(self, index)
        self.index = index
    
    # Forwards a message to the best receiver possible.
    # In other implementations, this is where we would place our "trust" system.
    # In all implementations, we are assuming we have already made the decision
    # to forward the packet. Nodes that are selfish won't call this method.
    def forward_msg(self, msg):
        # TODO
        return None
    
    # Called by other devices sending this device a message.
    # Here we decide whether to forward or drop a packet, or to do something
    # with it, as we are the intended recipient.
    def receive_msg(self, msg):
        if msg.dst == self.index:
            print("Received a packet:", msg.content)
        else:
            self.forward(msg)
    
    # Create a new message to a random destination, and send it off.
    def produce_msg(self):
        return None

# Example of how a network might be set up
NETWORK.add_node(1, device=Device(1))
NETWORK.add_node(2, device=Device(2))
NETWORK.add_edge(1, 2)