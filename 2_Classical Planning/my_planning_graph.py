
from itertools import chain, combinations
from aimacode.planning import Action
from aimacode.utils import expr

from layers import BaseActionLayer, BaseLiteralLayer, makeNoOp, make_node


class ActionLayer(BaseActionLayer):

    def _inconsistent_effects(self, actionA, actionB):
        """ Return True if an effect of one action negates an effect of the other

        See Also
        --------
        layers.ActionNode
        """
        # TODO: implement this function
        effectsA = actionA.effects
        effectsB = actionB.effects

        for effectOne in effectsA:
            for effectTwo in effectsB:
                if effectOne == ~effectTwo:
                    return True
        return False


    def _interference(self, actionA, actionB):
        """ Return True if the effects of either action negate the preconditions of the other

        See Also
        --------
        layers.ActionNode
        """
        # TODO: implement this function
        effectsA = actionA.effects
        effectsB = actionB.effects
        preconditionsA = actionA.preconditions
        preconditionsB = actionB.preconditions

        for eB in effectsB:
            if any([~eB in preconditionsA]):
                return True
                break
        for eA in effectsA:
            if any([~eA in preconditionsB]):
                return True
                break
        return False

        #Did not work
        #for eA in effectsA:
        #    for pB in preconditionsB:
        #        if any(pB ==~eA):
        #            return True
        #            break
        #for eB in effectsB:
        #    for pA in preconditionsA:
        #        if (any(pA ==~eB)):
        #            return True
        #            break
        #return False

        #Did not work
        #for eA in effectsA:
        #    for pA in preconditionsA:
        #        if (any(pB ==~eA for pB in preconditionsB) or any(eB ==~pA for eB in effectsB)):
        #            return True
        #            break
        #        else:
        #            return False

        #Did work
        #return any([~e in actionA.preconditions for e in actionB.effects]) \
        #        or any([~e in actionB.preconditions for e in actionA.effects])



    def _competing_needs(self, actionA, actionB):
        """ Return True if any preconditions of the two actions are pairwise mutex in the parent layer

        See Also
        --------
        layers.ActionNode
        layers.BaseLayer.parent_layer
        """
        # TODO: implement this function
        effectsA = actionA.effects
        effectsB = actionB.effects
        preconditionsA = actionA.preconditions
        preconditionsB = actionB.preconditions

        #Did Work
        #return all(self.parent_layer.is_mutex(pA,pB) for pA in preconditionsA for pB in preconditionsB) \
        #        and all(self.parent_layer.is_mutex(pB,pA) for pA in preconditionsA for pB in preconditionsB)

        #Did work
        for pA in preconditionsA:
            for pB in preconditionsB:
                if self.parent_layer.is_mutex(pA,pB):
                    return True
        return False




class LiteralLayer(BaseLiteralLayer):

    def _inconsistent_support(self, literalA, literalB):
        """ Return True if all ways to achieve both literals are pairwise mutex in the parent layer

        See Also
        --------
        layers.BaseLayer.parent_layer
        """
        # TODO: implement this function
        for litA in self.parents[literalA]:
            for litB in self.parents[literalB]:
                if not self.parent_layer.is_mutex(litA,litB):
                    return False
        return True

    def _negation(self, literalA, literalB):
        """ Return True if two literals are negations of each other """
        # TODO: implement this function
        if (literalA ==~ literalB) and (literalB ==~literalA):
            return True
        return False



class PlanningGraph:
    def __init__(self, problem, state, serialize=True, ignore_mutexes=False):
        """
        Parameters
        ----------
        problem : PlanningProblem
            An instance of the PlanningProblem class

        state : tuple(bool)
            An ordered sequence of True/False values indicating the literal value
            of the corresponding fluent in problem.state_map

        serialize : bool
            Flag indicating whether to serialize non-persistence actions. Actions
            should NOT be serialized for regression search (e.g., GraphPlan), and
            _should_ be serialized if the planning graph is being used to estimate
            a heuristic
        """
        self._serialize = serialize
        self._is_leveled = False
        self._ignore_mutexes = ignore_mutexes
        self.goal = set(problem.goal)

        # make no-op actions that persist every literal to the next layer
        no_ops = [make_node(n, no_op=True) for n in chain(*(makeNoOp(s) for s in problem.state_map))]
        self._actionNodes = no_ops + [make_node(a) for a in problem.actions_list]

        # initialize the planning graph by finding the literals that are in the
        # first layer and finding the actions they they should be connected to
        literals = [s if f else ~s for f, s in zip(state, problem.state_map)]
        layer = LiteralLayer(literals, ActionLayer(), self._ignore_mutexes)
        layer.update_mutexes()
        self.literal_layers = [layer]
        self.action_layers = []

    def h_levelsum(self):
        """ Calculate the level sum heuristic for the planning graph

        The level sum is the sum of the level costs of all the goal literals
        combined. The "level cost" to achieve any single goal literal is the
        level at which the literal first appears in the planning graph. Note
        that the level cost is **NOT** the minimum number of actions to
        achieve a single goal literal.

        For example, if Goal1 first appears in level 0 of the graph (i.e.,
        it is satisfied at the root of the planning graph) and Goal2 first
        appears in level 3, then the levelsum is 0 + 3 = 3.

        Hint: expand the graph one level at a time and accumulate the level
        cost of each goal.

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)
        """
        # TODO: implement this function
        #self.fill()
        level_sum = 0
        cost = []
        for goals in self.goal:
            for cost, layer in enumerate(self.literal_layers):
                self._extend()
                if goals in layer:
                    level_sum += cost
                    break
        return level_sum

    def h_maxlevel(self):
        """ Calculate the max level heuristic for the planning graph

        The max level is the largest level cost of any single goal fluent.
        The "level cost" to achieve any single goal literal is the level at
        which the literal first appears in the planning graph. Note that
        the level cost is **NOT** the minimum number of actions to achieve
        a single goal literal.

        For example, if Goal1 first appears in level 1 of the graph and
        Goal2 first appears in level 3, then the levelsum is max(1, 3) = 3.

        Hint: expand the graph one level at a time until all goals are met.

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)

        Notes
        -----
        WARNING: you should expect long runtimes using this heuristic with A*
        """
        # TODO: implement maxlevel heuristic
        level_sum = 0
        cost = []
        for goals in self.goal:
            for cost, layer in enumerate(self.literal_layers):
                self._extend()
                if goals in layer:
                    level_sum = max(cost,level_sum)
                    break
        return level_sum

    def h_setlevel(self):
        """ Calculate the set level heuristic for the planning graph

        The set level of a planning graph is the first level where all goals
        appear such that no pair of goal literals are mutex in the last
        layer of the planning graph.

        Hint: expand the graph one level at a time until you find the set level

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)

        Notes
        -----
        WARNING: you should expect long runtimes using this heuristic on complex problems
        """
        # TODO: implement setlevel heuristic

        """
        #Failed
        def allGoalsMet(layer):
            for goals in self.goal:
                if goals not in layer:
                    return False
            return True

        def goalsAreMutex(layer):
            #if not allGoalsMet(layer):
            #    return False
            for goalA, goalB in combinations(self.goal,2):
                if layer.is_mutex(goalA, goalB):
                    return False
            return True

        level = 0
        for layer in self.literal_layers:
            print(level)
            if allGoalsMet(layer):
                if not goalsAreMutex(layer):
                    return level
            self._extend()
            level += 1


        #Failed
        def AllGoalSeen(layer):
            for g in self.goal:
                if g not in layer:
                    return False
            return True
        def NoMutex(layer):
            # if not AllGoalSeen(layer):
            #     return False
            for g1,g2 in combinations(self.goal,2):
                if layer.is_mutex(g1,g2):
                    return False
            return True
        level = 0
        while not self._is_leveled:
            layer = self.literal_layers[level]
            if AllGoalSeen(layer) and NoMutex(layer):
                return level
            self._extend()
            level += 1
        return print("Did not reach goal")
        """

        #Works!
        def allGoalsMet(layer):
            for goals in self.goal:
                if goals not in layer:
                    return False
            return True
        def goalsAreMutex(layer):
            #if not allGoalsMet(layer):
            #    return False
            for goalA, goalB in combinations(self.goal,2):
                if layer.is_mutex(goalA, goalB):
                    return False
            return True
        level = 0
        while not self._is_leveled:
        ##    print(level)
            layer = self.literal_layers[level]
            if allGoalsMet(layer) and goalsAreMutex(layer):
                return level
            self._extend()
            level += 1
        return print("Did not reach goal")

        #Did not work
        #def AllGoalSeen(layer):
        #    for g in self.goal:
        #        if g not in layer:
        #            return False
        #    return True
        #def NoMutex(layer):
        #    if not AllGoalSeen(layer):
        #        return False
        #    for g1,g2 in combinations(self.goal,2):
        #        if layer.is_mutex(g1,g2):
        #            return False
        #    return True
        #self._extend()
        #level = 1
        #while True:
        #    if AllGoalSeen(self.literal_layers[-1]) and NoMutex(self.literal_layers[-2]):
        #        return level
        #    self._extend()
        #    level += 1

        #did not work
        #self._extend()
        #level = 0
        #while not self._is_leveled:
        #    layer = self.literal_layers[-1]
        #    if allGoalsMet(layer) and goalsAreMutex(layer):
        #        return level
        #    self._extend()
        #    level +=1
        #return -1

        #Did not work
        #while not self._is_leveled:
        #    layer = self.literal_layers[-1]
        #    if self.goal.issubset(layer) and not any(layer.is_mutex(a,b) for a, b in combinations(layer,2)):
        #        return levels
        #    self._extend()
        #    level += 1
        #return "Goals cannot be achieved!"

    ##############################################################################
    #                     DO NOT MODIFY CODE BELOW THIS LINE                     #
    ##############################################################################

    def fill(self, maxlevels=-1):
        """ Extend the planning graph until it is leveled, or until a specified number of
        levels have been added

        Parameters
        ----------
        maxlevels : int
            The maximum number of levels to extend before breaking the loop. (Starting with
            a negative value will never interrupt the loop.)

        Notes
        -----
        YOU SHOULD NOT THIS FUNCTION TO COMPLETE THE PROJECT, BUT IT MAY BE USEFUL FOR TESTING
        """
        while not self._is_leveled:
            if maxlevels == 0: break
            self._extend()
            maxlevels -= 1
        return self

    def _extend(self):
        """ Extend the planning graph by adding both a new action layer and a new literal layer

        The new action layer contains all actions that could be taken given the positive AND
        negative literals in the leaf nodes of the parent literal level.

        The new literal layer contains all literals that could result from taking each possible
        action in the NEW action layer.
        """
        if self._is_leveled: return

        parent_literals = self.literal_layers[-1]
        parent_actions = parent_literals.parent_layer
        action_layer = ActionLayer(parent_actions, parent_literals, self._serialize, self._ignore_mutexes)
        literal_layer = LiteralLayer(parent_literals, action_layer, self._ignore_mutexes)

        for action in self._actionNodes:
            # actions in the parent layer are skipped because are added monotonically to planning graphs,
            # which is performed automatically in the ActionLayer and LiteralLayer constructors
            if action not in parent_actions and action.preconditions <= parent_literals:
                action_layer.add(action)
                literal_layer |= action.effects

                # add two-way edges in the graph connecting the parent layer with the new action
                parent_literals.add_outbound_edges(action, action.preconditions)
                action_layer.add_inbound_edges(action, action.preconditions)

                # # add two-way edges in the graph connecting the new literaly layer with the new action
                action_layer.add_outbound_edges(action, action.effects)
                literal_layer.add_inbound_edges(action, action.effects)

        action_layer.update_mutexes()
        literal_layer.update_mutexes()
        self.action_layers.append(action_layer)
        self.literal_layers.append(literal_layer)
        self._is_leveled = literal_layer == action_layer.parent_layer
