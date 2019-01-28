## Monte Carlo Tree Search
import random, math, copy


class MCTS_Node():
    def __init__(self, state, parent=None):
        self.visits = 1
        self.reward = 0.0
        self.state = state
        self.children = []
        self.children_actions = []
        self.parent = parent

    def add_child(self, child_state, action):
        child = MCTS_Node(child_state, self)
        self.children.append(child)
        self.children_actions.append(action)

    def update(self, reward):
        self.reward += reward
        self.visits += 1

    def fully_explored(self):
        return len(self.children_actions) == len(self.state.actions())


FACTOR = 0.30
iter_limit = 200

def tree_policy(node):
    while not node.state.terminal_test():
        if not node.fully_explored():
            return expand(node)
        node = best_child(node)
    return node


def expand(node):
    tried_actions = node.children_actions
    legal_actions = node.state.actions()
    for action in legal_actions:
        if action not in tried_actions:
            new_state = node.state.result(action)
            node.add_child(new_state, action)
            return node.children[-1]


def best_child(node):
    best_score = float("-inf")
    best_children = []
    for child in node.children:
        exploit = child.reward / child.visits
        explore = math.sqrt(2.0 * math.log(node.visits) / child.visits)
        score = exploit + FACTOR * explore
        if score == best_score:
            best_children.append(child)
        elif score > best_score:
            best_children = [child]
            best_score = score
    if len(best_children) == 0:
        print("WARNING - There is no best child")
        return None
    return random.choice(best_children)


def default_policy(state):
    init_state = copy.deepcopy(state)
    while not state.terminal_test():
        action = random.choice(state.actions())
        state = state.result(action)

    # let the reward to be 1 for the winner, -1 for the loser
    return 1 if state._has_liberties(init_state.player()) else -1


def backup(node, reward):
    while node != None:
        node.update(reward)
        node = node.parent
        reward *= -1
