# Copyright (C) 2003 gocept, http://www.gocept.com/ 
# Christian Zagrodnick, cz@gocept.com
# $Id: search.py,v 1.4 2003/12/12 16:08:57 zagy Exp $

# python
from bisect import insort_right


class Search:
    """base class for search problems
   
    Implementation of blind depth/breadth first search.
   
    """

    def __init__(self, problem_node, depth_first=1, results=1):
        """constructor

            depth_first: if ture: depth firsth search, breadth first otherwise
            
            results: (int or None) if None: search continues until all
                possible nodes are tested. Otherwise search stops if the given
                number of results is in the result set. Defaults to 1, meaning
                return first result.
                
        """
        self.depth_first = depth_first
        self.nodes = [problem_node]
        self.results = []
        self.result_length = results
        self._tested_nodes = 0
        self._max_nodes = 0

    def run(self):
        """performs search

            returns None
        """
        while self.nodes:
            #self._record_stats()
            node = self._get_next_node()
            if self.isTarget(node):
                self.results.append(node)
            if self.result_length is not None:
                if len(self.results) >= self.result_length:
                    return
            child_nodes = self._get_children(node)
            self._extend_nodes(child_nodes)
   
    def getResult(self):
        """return list of resulting nodes"""
        return self.results
   
    def isTarget(self, node):
        """returns True if given node is a target, False otherwise
        """
        raise NotImplementedError, "Implemented in sub classes"
    
    def _get_next_node(self):
        return self.nodes.pop(0)

    def _get_children(self, node):
        """returns list of child nodes for given node
        """
        raise NotImplementedError, "Implemented in sub classes"

    def _extend_nodes(self, new_nodes):
        if self.depth_first:
            self.nodes[0:0] = new_nodes
        else:
            self.nodes.extend(new_nodes)

    def _record_stats(self):
        self._tested_nodes += 1
        nodes = len(self.nodes)
        if nodes > self._max_nodes:
            self._max_nodes = nodes


class HeuristicSearch(Search):
    """perform a heuristical search""" 
    
    def _extend_nodes(self, new_childs):
        for child in new_childs:
            child.hval = self.heuristic(child)
            insort_right(self.nodes, child)

    def heuristic(self, node):
        raise NotImplementedError, "Implemented in sub classes"

