# Copyright (C) 2003 gocept, http://www.gocept.com/ 
# Christian Zagrodnick, cz@gocept.com
# $Id: search.py,v 1.3 2003/12/10 13:11:10 zagy Exp $

# python
from bisect import insort_right


class Decorator:
    """base class for decorator like things"""
    
    def __getattr__(self, key):
        return getattr(self.base, key)

    def __setattr__(self, key, value):
        setattr(self.base, key, value)

    def __delattr__(self, key):
        delattr(self.base, key)
    
    def __repr__(self):
        return repr(self.base)

    def __str__(self):
        return str(self.base)


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


class HeuristicsDecorator(Decorator):
    """Decorator for adding heuristics to an object"""
    
    def __init__(self, base, hval):
        self.__dict__['base'] = base
        self.__dict__['hval'] = hval

    def __cmp__(self, other):
        if isinstance(other, HeuristicsDecorator):
            return cmp(self.hval, other.hval)
        return cmp(self.base, other)


class HeuristicSearch(Search):
    """perform a heuristical search""" 
    
    def _extend_nodes(self, new_childs):
        for child in new_childs:
            child = HeuristicsDecorator(child, self.heuristic(child))
            insort_right(self.nodes, child)

    def heuristic(self, node):
        raise NotImplementedError, "Implemented in sub classes"

