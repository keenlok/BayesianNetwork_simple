import itertools
import sys
import json
from copy import deepcopy


class BayesianNetwork(object):
    def __init__(self, structure, values, queries):
        # you may add more attributes if you need
        self.variables = structure[
            "variables"]  # dict of {"Burglary": ["True","False"], "Earthquake": ["True","False"]...}
        self.dependencies = structure["dependencies"]
        self.conditional_probabilities = values["conditional_probabilities"]
        self.prior_probabilities = values["prior_probabilities"]
        self.queries = queries
        self.answer = []
        self.nodes = None

    # Construct a DAG with Nodes
    def construct(self):
        print "Building Bayesian Network"
        nodes = {}
        for key in self.variables:
            print
            print "What is this key?", key
            # If the var has dependencies
            if key in self.dependencies.keys():
                print key, "is dependent"
                nodes[key] = Node(key, self.dependencies[key], self.conditional_probabilities[key], True)
            # Else it is a prior
            else:
                print key, "is independent"
                nodes[key] = Node(key, None, self.prior_probabilities[key], False)
        self.nodes = nodes

    def infer(self):
        # TODO: Your code here to answer the queries given using the Bayesian
        # network built in the construct() method.
        print "\n"
        for query in self.queries:
            index = query["index"]
            find = query["tofind"]
            given = query["given"]

            # if 'find' is empty
            if len(find) == 0:
                self.answer.append({"index": index, "answer": 0})
                continue

            # if 'find' contains 1 element
            if len(find) == 1:
                to_find = find.keys()[0]
                print "To find is", to_find, ": ", find[to_find]
                print "Given is  ", given

                # if no given variable => calculate probability for single variable the P(A)
                if len(given.keys()) == 0:
                    value = self.calculate_probability_single(self.nodes[to_find], find[to_find])
                    print value
                    self.answer.append({"index": index, "answer": value})
                    continue
                else:
                    target = self.nodes[to_find]
                    if given.keys() == target.dependencies:
                        # Find definite P ( A | Parents(A))
                        probability = self.get_definite_conditional_probability(find, given, target, to_find)
                        self.answer.append({"index": index, "answer": probability})
                        continue
                    else:
                        # Find P ( A | rand(...))
                        # TODO: Add here
                        print 0
            else:
                # find P(A1, A2,..., Ai | B1,..., Bi)
                #TODO: ADD here
                print 0

                # 'find' is prior, return prior probability

            # 'given' is empty, find total probability
            if len(given) == 0:
                x = 0
            # 'given' are direct parents of find (we can just look up the table)

        # Check if there are independent variables (from find) in 'given' (means we can remove them from 'given')
        # If find > 1
        # TO BE CONFIRMED
        print self.answer
        # for the given example:
        # self.answer = [{"index": 1, "answer": 0.01}, {"index": 2, "answer": 0.71}]
        # the format of the answer returned SHOULD be as shown above.
        return self.answer

    @staticmethod
    def get_definite_conditional_probability(find, given, target, to_find):
        print "Finding definite probability"
        prob_key = given
        prob_key["own_value"] = find[to_find]
        print prob_key
        probability = 0
        for p in target.probabilities:
            possible = p["probability"]
            to_check_with = deepcopy(p)
            del to_check_with["probability"]
            if prob_key.items() == to_check_with.items():
                probability = possible
                break
        print probability
        return probability

    # Calculate / Find the probability of a single variable ie P(A = a)
    def calculate_probability_single(self, target_node, value):
        # print "What is this target", target_node.name
        # print "What is the value", value

        # not dependent on other nodes
        if not target_node.isConditional:
            return target_node.probabilities[value]
        else:
            combs = BayesianNetwork.enumerate_vars(target_node.dependencies)
            # print len(combs)
            prob = 0
            # print target_node.probabilities[0]
            for i in range(0, len(target_node.probabilities)):
                # print
                # print "iteration i: ", i
                probToAdd = 0
                p = deepcopy(target_node.probabilities[i])
                possible = p["probability"]
                del p["probability"]
                # print "What is this p ", p
                # print possible
                for j in range(0, len(combs)):
                    # print "iteration j", j
                    combs[j]["own_value"] = value
                    # print combs[j]
                    if p.items() == combs[j].items():
                        # print "These 2 are equal", p, combs[j]
                        for dependency in target_node.dependencies:
                            possible *= self.calculate_probability_single(self.nodes[dependency], p[dependency])
                        probToAdd = possible
                        # print probToAdd
                        break
                # print probToAdd
                prob += probToAdd

            print "What is the final probability", prob
            return prob



    @staticmethod
    def calculate_find_given(find, find_value, given, given_value):
        print find.probabilities["find"]

    ''' Enumerates a list of true and false variables'''
    @staticmethod
    def enumerate_vars(list_of_vars):
        print list_of_vars
        length = pow(2, len(list_of_vars) - 1)
        combs = list()
        perms = set()
        for comb in itertools.combinations_with_replacement(["False", "True"], length):
            for perm in itertools.permutations(comb):
                # print perm
                perms.add(perm)

        for perm in perms:
            # print perm
            comb = {}
            i = 0
            for var in list_of_vars:
                comb[var] = perm[i]
                i += 1
            combs.append(comb)
        # print combs
        return combs


class Node(object):
    def __init__(self, name, dependencies, probabilities, is_conditional):
        self.name = name
        self.dependencies = dependencies
        self.probabilities = probabilities
        self.isConditional = is_conditional

    # You may add more classes/functions if you think is useful. However, ensure
    # all the classes/functions are in this file ONLY and used within the
    # BayesianNetwork class.


def main():
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 4:
        print ("\nUsage: python b_net_A3_xx.py structure.json values.json queries.json \n")
        raise ValueError("Wrong number of arguments!")

    structure_filename = sys.argv[1]
    values_filename = sys.argv[2]
    queries_filename = sys.argv[3]

    try:
        with open(structure_filename, 'r') as f:
            structure = json.load(f)
        with open(values_filename, 'r') as f:
            values = json.load(f)
        with open(queries_filename, 'r') as f:
            queries = json.load(f)

    except IOError:
        raise IOError("Input file not found or not a json file")

    # testing if the code works
    b_network = BayesianNetwork(structure, values, queries)
    b_network.construct()
    answers = b_network.infer()


if __name__ == "__main__":
    main()
