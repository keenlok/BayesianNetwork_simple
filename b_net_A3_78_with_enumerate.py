import itertools
import sys
import json
from copy import deepcopy

class BayesianNetwork(object):
    def __init__(self, structure, values, queries):
        # you may add more attributes if you need
        self.variables = structure["variables"]
        # dict of {"Burglary": ["True","False"], "Earthquake": ["True","False"]...}
        self.dependencies = structure["dependencies"]
        self.conditional_probabilities = values["conditional_probabilities"]
        self.prior_probabilities = values["prior_probabilities"]
        self.calculated_joint_probability = {}
        self.queries = queries
        self.answer = []
        self.nodes = None
        self.is_formula_calculated = False
        self.base_formula = []

    ''' Construct the Bayesian network with custom Node class'''
    def construct(self):
        print "Building Bayesian Network"
        nodes = {}
        for key in self.variables.keys():
            print
            print "What is this key?", key
            # If the var has dependencies
            if key in self.dependencies.keys():
                print key, "is dependent", self.variables[key]
                nodes[key] = Node(key, self.dependencies[key], self.conditional_probabilities[key], self.variables[key], True)
            # Else it is a prior
            else:
                print key, "is independent", self.variables[key]
                nodes[key] = Node(key, None, self.prior_probabilities[key], self.variables[key], False)
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
                        toFind, given = self.bayes_formula(query)
                        top = self.get_conjunction(toFind)
                        bottom = self.get_conjunction(given)
                        print "Top and bottom:", top, ", ", bottom
                        probability = top / bottom
                        print "what is probability? ", probability
                        self.answer.append({"index": index, "answer": probability})
                        continue
            else:
                # find P(A1, A2,..., Ai | B1,..., Bi)
                toFind, given = self.bayes_formula(query)
                # print "Does bayes return correctly", toFind, given
                top = self.get_conjunction(toFind)
                bottom =  self.get_conjunction(given)
                #print "Top and bottom:", top, ", ", bottom
                probability = top / bottom
                # print "what is probability? ", probability
                self.answer.append({"index": index, "answer": probability})
                continue

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
        # print prob_key
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
            if target_node.has_single_probability(value):
                return target_node.get_single_probability(value)
            # Create a list of possible combinations from the node's parents
            combs = BayesianNetwork.enumerate_vars(target_node.dependencies, self.nodes)
            probability = 0
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
                probability += probability_to_add

            target_node.store_single_probability(value, probability)
            # print "What is the final probability", prob
            return probability

    @staticmethod
    def enumerate_vars(list_of_vars, list_nodes):
        length = 1
        for i in range(len(list_of_vars)):
            length *= len(list_nodes[list_of_vars[i]].values)

        list_of_values = list()
        for var in list_of_vars:
            print var
            combs = []
            for value in list_nodes[var].values:
                combs.append({var: value})
            list_of_values.append(combs)
        print list_of_values
        perms = [{} for i in range(length)]

        num_to_loop = 0
        for i in range(len(list_of_values)):
            print i, range(1)
            length_of_values = len(list_of_values[i])
            num_to_repeat = (length / length_of_values) - num_to_loop
            num_to_loop = max(1, num_to_loop)
            count = 0
            for k in range(num_to_loop):
                for j in range(len(list_of_values[i])):
                    for l in range(max(num_to_repeat, 1)):
                        perms[count].update(list_of_values[i][j])
                        count += 1
            num_to_loop *= length_of_values
        print perms
        return perms

    '''Return a list of queries that are able to solve any conjunction of variables
    list in the form of dictionary in the form of { "find": variable, "given": [dependencies]}
    Should only need to compute once
    '''
    def get_base_formula(self):
        if self.is_formula_calculated:
            return self.base_formula
        formulas = []
        # Iterate through the variable names
        for variable in self.variables.keys():
            # Create the base "Queries"
            # If prior
            formula = {}
            if not variable in self.dependencies:
                formula["tofind"] = variable
                formula["given"] = []
            # If got dependencies
            else:
                formula["tofind"] = variable
                formula["given"] = self.dependencies[variable]
            formulas.append(formula)
        self.base_formula = formulas
        self.is_formula_calculated = True
        return formulas

    '''Given a conjunction, use the base formula to find answer
       Conjunction form {variable: value, variable: value}
    '''
    def get_conjunction(self, conjunction):
        # print "get_conjunction", conjunction
        # Initial probablility
        result = 0
        # obtain list of tuples with T/F states
        probabilities = self.gen_probabilities(conjunction)
        # obtain a list of dictionaries with {variable:state}
        probabilities = self.create_dict(probabilities)

        # Iterate through dictionaries, find their probabilities and sum
        for probability in probabilities:
            # print "What is this", probability
            to_add = self.find_probability(probability)
            # print "TO ADD", to_add
            result += to_add
            # print self.find_probability(probability)

        # print result
        return result

    def create_dict(self, probabilities):
        result = []
        all_vars = self.variables.keys()
        num_vars = len(all_vars)

        for tuple_ in probabilities:
            idx = 0
            res = {}
            for idx in range(num_vars):
                res[all_vars[idx]] = tuple_[idx]
                # print tuple_[idx]
            result.append(res)
        return result

    # Given a conjunction, generate the 
    def gen_probabilities(self, conjunction):
        variable_states = []
        # print "inside gen_prob, conjunction:", conjunction
        for variable in self.variables:
            if variable in conjunction["tofind"]:
                temp = [conjunction["tofind"][variable]]
                variable_states.append(temp)
            else:
                variable_states.append(self.variables[variable])
                
        # print 'VARIABLE STATES', variable_states
        probabilities = itertools.product(*variable_states)
        return probabilities

    # Given a dictionary representing a primitive query, find the probability using the base formula
    def find_probability(self, query):
        # if already calculated, don't calculate again
        if str(query) in self.calculated_joint_probability.keys():
            # print "using cached value"
            return self.calculated_joint_probability[str(query)]
        probability = 1
        for formula in self.get_base_formula():
            to_times = self.find_base_probability(query, formula)
            probability *= to_times
        self.calculated_joint_probability[str(query)] = probability
        return probability

    # Given a specific query with the defined variables, find probability
    def find_base_probability(self, query, formula):
        final_query = {"tofind": {formula["tofind"]: query[formula["tofind"]]}}
        # Settle tofind

        if len(formula["given"]) == 0:
            # tofind single probablity
            # print "WHat is in formula?", formula
            # print "query?", query[formula["tofind"]]
            return self.calculate_probability_single(self.nodes[formula["tofind"]], query[formula["tofind"]])
        else:
            final_query["given"] = {}
            # Settle given
            for given in formula["given"]:
                final_query["given"][given] = query[given]
            # return conditional probability
            return self.get_definite_conditional_probability(final_query["tofind"], final_query["given"], self.nodes[formula["tofind"]], formula["tofind"])

        # Result = {"tofind": {var: value}, "given": {var:value,...}}
        # Prior query

        # Simple conditional query

    @staticmethod
    def bayes_formula(conditional_query):
        # if there is a single given
        conditional_query["tofind"].update(conditional_query["given"])
        find_1 = conditional_query
        find_2 = {"tofind": conditional_query["given"]}
        print "BEFORE returning", find_1, ", find 2:", find_2
        return find_1, find_2


class Node(object):
    def __init__(self, name, dependencies, probabilities, values, is_conditional):
        self.name = name
        self.dependencies = dependencies
        self.probabilities = probabilities
        self.isConditional = is_conditional
        self.values = values
        if is_conditional:
            self.isCalculated = False
            self.singleProbability = {}

    def get_single_probability(self, value):
        return self.singleProbability[value]

    def has_single_probability(self, value):
        return value in self.singleProbability.keys()

    def store_single_probability(self, value, probability):
        self.singleProbability[value] = probability

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
