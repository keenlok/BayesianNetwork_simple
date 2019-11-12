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

    ''' Construct the Bayesian network with custom Node class
    '''
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

    '''Find the probability of something given its parents.
    e.g If A is dependent on B and C, and the values/evidence for B and C are in given
    This function simply looks for that values in the node's probabilities
    
    find:dict, given:dict, target:node, to_find:string - name of the node
    '''
    @staticmethod
    def get_definite_conditional_probability(find, given, target, to_find):
        # print "Finding definite probability"
        # print "What is given???", given, "And what is FIND???", find
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
        # print probability
        return probability

    ''' Calculate / Find the probability of a single variable ie P(A = a)
    target_node:node, value: "True" | "False"
    '''
    def calculate_probability_single(self, target_node, value):
        # not dependent on other nodes
        if not target_node.isConditional:
            return target_node.probabilities[value]
        # Has parents
        else:
            if target_node.isCalculated:
                return target_node.get_single_probability(value)
            # Create a list of possible combinations from the node's parents
            combs = BayesianNetwork.enumerate_vars(target_node.dependencies)
            prob = 0
            # Calculate the probability for P(A | Parents(A)) * P (Parents(A))
            for i in range(0, len(target_node.probabilities)):
                probability_to_add = 0
                p = deepcopy(target_node.probabilities[i])
                possible = p["probability"]
                del p["probability"]
                for j in range(0, len(combs)):
                    combs[j]["own_value"] = value
                    if p.items() == combs[j].items():
                        for dependency in target_node.dependencies:
                            possible *= self.calculate_probability_single(self.nodes[dependency], p[dependency])
                        probability_to_add = possible
                        break
                prob += probability_to_add

            target_node.store_single_probability(value, prob)
            # print "What is the final probability", prob
            return prob

    ''' Enumerates a list of true and false variables:
        So for a list of variables say ["Burglary", "Earthquake"],
        it will return: [
        {'Burglary': 'True',    'Earthquake': 'True'}, 
        {'Burglary': 'False',   'Earthquake': 'True'}, 
        {'Burglary': 'False',   'Earthquake': 'False'}, 
        {'Burglary': 'True',    'Earthquake': 'False'}
        ] '''
    @staticmethod
    def enumerate_vars(list_of_vars):
        # print list_of_vars
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
        if is_conditional:
            self.isCalculated = False
            self.singleProbability = {}

    def get_single_probability(self, value):
        if self.isCalculated:
            return self.singleProbability[value]
        else:
            return 0

    def store_single_probability(self, value, probability):
        if value == "True":
            self.singleProbability[value] = probability
            self.singleProbability["False"] = 1 - probability
        else:
            self.singleProbability[value] = probability
            self.singleProbability["True"] = 1 - probability
        self.isCalculated = True

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
