import random
from functools import wraps

from flask import Flask

# from https://blog.miguelgrinberg.com/post/how-to-deploy-a-react--flask-project
app = Flask(__name__)
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/user/<params>')
def parametrized_index(params):
    return app.send_static_file('index.html')

rangel = lambda l: range(len(l))

roles = {
    'merlin': True,
    'percival': True,
    'merciful': False,
    'gawain': False,
    'arthur': False,
    'morgana': True,
    'mordred': True,
    'oberon': False
}

alignments = {
    'merlin': 'good',
    'percival': 'good',
    'merciful': 'good',
    'gawain': 'good',
    'arthur': 'good',
    'loyal': 'good',
    'morgana': 'bad',
    'mordred': 'bad',
    'oberon': 'bad',
    'minion': 'bad',
}

def active_roles():
    return [role for role in roles if roles[role]]

prev_mode = 'lobby'
mode = 'lobby'

configs = {
    # Num players: [Good, Evil, [#players.twofail]]
    2: [1, 1, [1, 1, 1, 1, 1]],
    5: [3, 2, [2, 3, 2, 3, 3]],
    6: [4, 2, [2, 3, 4, 3, 4]],
    7: [4, 3, [2, 3, 3, 4.1, 4]],
    8: [5, 3, [3, 4, 4, 5.1, 5]],
    9: [6, 3, [3, 4, 4, 5.1, 5]],
    10: [6, 4, [3, 4, 4, 5.1, 5]]
}

kicked = []
players = []
player_roles = []
player_votes = {}
player_acts = {}
assassin = 0

def to_player_list(x):
    return [x[i] if i in x else None for i in range(len(players))]

def new_game_state():
    return {
        'round': 0,
        'successes': [],
        'fails': [],
        'captain': 0,
        'skips': 0,
        'proposed': False,
        'approved': False,
        'proposal': [],
        'votes': [],
        'hypertext': 'Trust no one',
        'assassin_mode': False,
        'rounds': configs[len(players)][2] if len(players) in configs else ['ERROR']
    }

game_state = new_game_state()

def sees(i, j):
    a, b = player_roles[i], player_roles[j]
    if i == j:
        return player_roles[i] + ('+assassin' if i == assassin else '')
    if a == 'merlin' and alignments[b] == 'bad' and b != 'mordred':
        return 'bad'
    if a == 'percival' and b in ['merlin', 'morgana']:
        return 'merlin' + ('?' if 'morgana' in player_roles else '')
    if alignments[a] == 'bad' and a != 'oberon':
        if (alignments[b] == 'bad' and b != 'oberon') or b == 'merciful':
            return 'bad' + ('?' if 'merciful' in player_roles else '')
    if a == 'loyal' and b == 'arthur':
        return 'arthur'
    return '?'

def player_names():
    return [player[0] for player in players]

def player_keys():
    return [player[1] for player in players]

def authenticate(name, key):
    return (name, key) in players # thanks rahul

fail = {'success': False}
success = {'success': True}

def secure(f):
    @wraps(f)
    def wrapped(name, key, *args, **kwargs):
        if not authenticate(name, key):
            return {'success': False}
        return {'success': True, **f(name, *args, **kwargs)}
    return wrapped

def insecure(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        res = f(*args, **kwargs)
        if 'success' in res:
            return res
        return {'success': True, **res}
    return wrapped

def modal(*active_modes, gameplay=False):
    gameplay_check = lambda: (not gameplay) or (not game_state['assassin_mode'])
    return requires(lambda: mode in active_modes and gameplay_check())

def requires(predicate):
    def wrap(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not predicate():
                return fail
            return {**success, **f(*args, **kwargs)}
        return wrapped
    return wrap

@app.route('/server/get_kicked')
@insecure
def get_kicked():
    return {'data': kicked}

@app.route('/server/auth/<name>/<key>')
def auth(name, key):
    if name not in player_names() and name not in kicked and mode == 'lobby':
        players.append((name, key))
    return secure(lambda *args: {})(name, key)

@app.route('/server/reset')
@insecure
def reset():
    global mode, prev_mode
    if mode != 'lobby':
        prev_mode = mode
    mode = 'lobby'
    return {}

@app.route('/server/unreset')
@insecure
def unreset():
    global mode
    mode = prev_mode
    return {}

@app.route('/server/get_mode')
@insecure
def get_mode():
    return {'data': mode}

@app.route('/server/lobby/kick/<name>')
@insecure
@modal('lobby')
def kick(name):
    global players
    kicked.append(name)
    players = [(name_, key) for (name_, key) in players if name_ != name]
    return {}

@app.route('/server/lobby/toggle/<role>')
@insecure
@modal('lobby')
def toggle(role):
    if role in roles:
        roles[role] = not roles[role]
    return {}

@app.route('/server/lobby/get_players')
@insecure
def get_players():
    return {'data': player_names()}

@app.route('/server/lobby/get_roles')
@insecure
@modal('lobby')
def get_roles():
    return {'data': roles}

@app.route('/server/lobby/start_game')
@insecure
@modal('lobby')
def start_game():
    global game_state, player_roles, mode, assassin, kicked
    def fail(message):
        return {'started': False, 'message': message}
    if len(players) not in configs:
        return fail(f"Can't start a game with {len(players)} players")
    num_good, num_bad, _ = configs[len(players)]
    good_roles = [role for role in active_roles() if alignments[role] == 'good']
    bad_roles = [role for role in active_roles() if alignments[role] == 'bad']
    num_loyal =  num_good - len(good_roles)
    num_minion = num_bad - len(bad_roles)
    if num_loyal < 0:
        return fail('Too many good roles')
    if num_minion < 0:
        return fail('Too many bad roles')
    player_roles = good_roles + bad_roles + ['loyal'] * num_loyal + ['minion'] * num_minion
    random.shuffle(player_roles)
    while True:
        assassin = random.randrange(len(players))
        if (alignments[player_roles[assassin]] != 'good'
            and (num_minion == 0 or player_roles[assassin] == 'minion')):
            break
    game_state = new_game_state()
    mode = 'game'
    kicked = []
    return {'started': True, 'message': 'Good luck!'}
    
@app.route('/server/game/get_game_state/<name>/<key>')
@secure
@modal('game', 'captain')
def get_game_state(name):
    return {**game_state, 'actors': list(player_acts.keys())}

@app.route('/server/game/get_my_state/<name>/<key>')
@secure
@modal('game')
def get_my_state(name):
    if name in player_names():
        i = player_names().index(name)
        return {
            'i': i,
            'roles': [sees(i, j) for j in rangel(player_roles)],
            'vote': player_votes[i] if i in player_votes else '',
            'act': player_acts[i] if i in player_acts else '',
            'assassin': i == assassin,
            'good': alignments[player_roles[i]] == 'good'
        }
    return fail

@app.route('/server/game/toggle_proposal/<name>/<key>/<proposal>')
@secure
@modal('game', gameplay=True)
@requires(lambda: not game_state['proposed'])
def toggle_proposal(name, proposal):
    if proposal not in player_names():
        return fail
    if proposal in game_state['proposal']:
        game_state['proposal'].remove(proposal)
    else:
        game_state['proposal'].append(proposal)
    return success

@app.route('/server/game/propose_team/<name>/<key>')
@secure
@modal('game', gameplay=True)
def propose_team(name):
    global player_votes
    num = len(game_state['proposal'])
    num_needed = int(configs[len(players)][2][game_state['round']])
    if num != num_needed:
        return {**fail, 'message': f'Need {num_needed} players, {num} selected'}
    player_votes = {}
    game_state['votes'] = []
    game_state['proposed'] = True
    return success

@app.route('/server/game/vote/<name>/<key>/<vote>')
@secure
@modal('game', gameplay=True)
@requires(lambda: game_state['proposed'] == True and len(game_state['votes']) < len(players))
def vote(name, vote):
    if name not in player_names() or vote not in ['approve', 'disapprove']:
        return fail
    i = player_names().index(name)
    if name not in game_state['votes']:
        game_state['votes'].append(name)
    player_votes[i] = vote
    if len(game_state['votes']) == len(players):
        game_state['votes'] = to_player_list(player_votes)
        if sum([vote == 'approve' for vote in game_state['votes']]) > len(players)/2:
            mission_approved()
        else:
            mission_disapproved()
    return success

@app.route('/server/game/act/<name>/<key>/<act>')
@secure
@modal('game', gameplay=True)
@requires(lambda: game_state['approved'] == True)
def act(name, act):
    if (name not in player_names()
        or name not in game_state['proposal']
        or name in player_acts
        or act not in ['success', 'fail']):
        print("FAIL", name, player_names(), game_state['proposal'], player_acts, act)
        return fail
    i = player_names().index(name)
    if alignments[player_roles[i]] == 'good' and act == 'fail':
        return fail # bwahaha
    player_acts[name] = act
    num_actors = configs[len(players)][2][game_state['round']]
    fails_needed = 2 if num_actors % 1 != 0 else 1
    num_actors = int(num_actors)
    if len(player_acts) == num_actors:
        num_fails = sum([act == 'fail' for act in player_acts.values()])
        if num_fails >= fails_needed:
            mission_fail(num_fails)
        else:
            mission_succeed(num_fails)
    return success

def broadcast(message):
    game_state['hypertext'] = message

def mission_disapproved():
    broadcast("The mission was rejected")
    next_captain()
    game_state['skips'] += 1
    if game_state['skips'] > 4:
        evil_win()
    game_state['proposed'] = False
    game_state['approved'] = False

def mission_approved():
    broadcast("The mission was approved")
    game_state['approved'] = True

def next_captain():
    game_state['captain'] = (game_state['captain'] + 1) % len(players)

def mission_end():
    global player_acts
    game_state['round'] += 1
    game_state['skips'] = 0
    game_state['proposed'] = False
    game_state['approved'] = False
    player_acts = {}
    next_captain()

def mission_succeed(num_fails):
    broadcast(f"The mission succeeded with {num_fails} fails")
    game_state['successes'].append(game_state['round'])
    mission_end()
    if len(game_state['successes']) >= 3:
        assassin_chance()

def mission_fail(num_fails):
    broadcast(f"Mission failed with {num_fails} fail{'s' if num_fails > 1 else ''}")
    game_state['fails'].append(game_state['round'])
    mission_end()
    if len(game_state['fails]']) >= 3:
        evil_win()

def evil_win():
    # global mode
    # mode = 'evil_win'
    broadcast("Evil wins!")
    game_state['assassin_mode'] = True

def assassin_chance():
    broadcast(f"{player_names()[assassin]}, choose someone to assassinate. There isn't software support for this right now, so just tell the group once you've decided.")
    game_state['assassin_mode'] = True
    
def good_win():
    # global mode
    # mode = 'good_win'
    broadcast("Good wins!")
    game_state['assassin_mode'] = True
