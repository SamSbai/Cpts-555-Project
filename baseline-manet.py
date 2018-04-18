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
class Device:
    # TODO: consider a "selfishness score" to show how likely a node is to be
    # selfish. A score of 1 is always selfish, 0 is never selfish. In between is
    # a perhaps random choice. (DISCUSS?)
    def __init__(self, index):
        self.index = index
    
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
        paths = nx.all_simple_paths(NETWORK, self.index, msg.dst)
        options = [p for p in paths if not msg.has_cycles_in(p)]
    
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
        else:
            self.forward_msg(msg)
    
    # Create a new message to a random destination, and send it off.
    def produce_msg(self):
        # Select a random destination other than ourselves.
        destinations = [i for i in NETWORK.nodes if i != self.index]
        dst = random.choice(destinations)
        src = self.index
    
        # Create a message and send it off into the ethers.
        msg = Message(src, dst, "a")
        self.forward_msg(msg)

# Example of how a network might be set up.
NETWORK.add_node(1, device=Device(1))
NETWORK.add_node(2, device=Device(2))
NETWORK.add_edge(1, 2)

# Example of how a message might be sent.
# Note that we will need a proper benchmark, perhaps by iterating over every
# device, having it produce and send a message, and testing how many packets
# reach their intended recipient.
NETWORK.nodes[1]["device"].produce_msg()
NETWORK.nodes[2]["device"].produce_msg()
