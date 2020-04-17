import random
from functools import wraps

from flask import Flask

app = Flask(__name__)

rangel = lambda l: range(len(l))

roles = {
    'merlin': False,
    'percival': False,
    'merciful': False,
    'morgana': False,
    'mordred': False,
}

alignments = {
    'merlin': 'good',
    'percival': 'good',
    'merciful': 'good',
    'loyal': 'good',
    'morgana': 'bad',
    'mordred': 'bad',
    'oberon': 'bad',
    'minion': 'bad',
}

def active_roles():
    return [role for role in roles if roles[role]]

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

players = []
player_roles = []
player_votes = {}

def player_votes_list():
    return [item[1] for item in sorted(list(player_votes.items()), key=lambda item: item[0])]

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
    }

game_state = new_game_state()

def sees(i, j):
    a, b = player_roles[i], player_roles[j]
    if i == j:
        return player_roles[i]
    if a == 'merlin' and alignments[b] == 'bad' and b != 'mordred':
        return 'bad'
    if a == 'percival' and b in ['merlin', 'percival']:
        return 'merlin?'
    if alignments[a] == 'bad' and a != 'oberon':
        if (alignments[b] == 'bad' and b != 'oberon') or b == 'merciful':
            return 'bad'
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

def modal(*active_modes):
    return requires(lambda: mode in active_modes)

def requires(predicate):
    def wrap(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not predicate():
                return fail
            return {**success, **f(*args, **kwargs)}
        return wrapped
    return wrap

@app.route('/server/auth/<name>/<key>')
def auth(name, key):
    if name not in player_names() and mode == 'lobby':
        players.append((name, key))
    return secure(lambda *args: {})(name, key)

@app.route('/server/get_mode')
@insecure
def get_mode():
    return {'data': mode}

@app.route('/server/lobby/kick/<name>')
@insecure
@modal('lobby')
def kick(name):
    global players
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
    global game_state, player_roles, mode
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
    game_state = new_game_state()
    mode = 'game'
    return {'started': True, 'message': 'Good luck!'}
    
@app.route('/server/game/get_game_state/<name>/<key>')
@secure
@modal('game', 'captain')
def get_game_state(name):
    return game_state

@app.route('/server/game/get_my_state/<name>/<key>')
@secure
@modal('game', 'captain')
def get_my_state(name):
    if name in player_names():
        i = player_names().index(name)
        return {
            'i': i,
            'roles': [sees(i, j) for j in rangel(player_roles)],
            'vote': player_votes[i] if i in player_votes else ''
        }
    return fail

@app.route('/server/game/toggle_proposal/<name>/<key>/<proposal>')
@secure
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
def propose_team(name):
    num = len(game_state['proposal'])
    num_needed = configs[len(players)][2][game_state['round']]
    if num != num_needed:
        return {**fail, 'message': f'Need {num_needed} players, {num} selected'}
    game_state['proposed'] = True
    return success

@app.route('/server/game/vote/<name>/<key>/<vote>')
@secure
@requires(lambda: game_state['proposed'] == True and len(game_state['votes']) < len(players))
def vote(name, vote):
    if name not in player_names():
        return fail
    i = player_names().index(name)
    if name not in game_state['votes']:
        game_state['votes'].append(name)
    player_votes[i] = vote
    if len(game_state['votes']) == len(players):
        game_state['votes'] = player_votes_list()
        if sum([vote for vote in player_votes_list() if vote == 'approve']) > len(players)/2:
            mission_disapproved()
        else:
            mission_approved()
    return success

def mission_disapproved():
    next_captain()
    game_state['skips'] += 1
    if game_state['skips'] > 4:
        evil_win()
    game_state['proposed'] = False
    game_state['approved'] = False

def mission_approved():
    game_state['approved'] = True

def next_captain():
    game_state['captain'] = (game_state['captain'] + 1) % len(players)

def mission_end():
    game_state['round'] += 1
    game_state['skips'] = 0
    next_captain()

def mission_succeed():
    game_state['successes'].append(game_state['round'])
    mission_end()
    if len(game_state['successes']) >= 3:
        assassin_chance()

def mission_fail():
    game_state['fails'].append(game_state['round'])
    mission_end()
    if len(game_state['fails]']) >= 3:
        evil_win()

def evil_win():
    global mode
    mode = 'evil_win'

def assassin_chance():
    global mode
    mode = 'assassin'

def good_win():
    global mode
    mode = 'good_win'