import React, { useState, useEffect } from 'react'
import './App.css'
import { Container } from 'react-bootstrap'

function App() {
  const [mode, setMode] = useState('lobby')
  const [players, setPlayers] = useState([])
  const [roles, setRoles] = useState({})
  const [auth, setAuth] = useState(false)
  const [message, setMessage] = useState("")
  const [gameState, setGameState] = useState({'round': 0, 'successes': [], 'fails': [], 'mission': 0, 'captain': 0, 'skips': 0, 'proposed': false, 'approved': false, 'proposal': [], 'votes': [], 'hypertext': 'ReactJS is legendary', 'assassin_mode': false, 'rounds': [0, 0, 0, 0, 0], 'actors': []})
  const [myState, setMyState] = useState({'i': 0, 'roles': [], 'vote': '', 'act': '', 'assassin': false, 'good': true});
  const [kicked, setKicked] = useState([]);
  const url_components = window.location.pathname.split('/')
  let [name, key] = url_components[url_components.length - 1].split('-')

  useEffect(() => {
    const interval = setInterval(() => {
      fetch('/server/auth/' + name + '/' + key).then(res => res.json()).then(res => setAuth(res.success))
      fetch('/server/get_mode').then(res => res.json()).then(res => {if (res.success) setMode(res.data)})
      fetch('/server/lobby/get_players').then(res => res.json()).then(res => {if (res.success) setPlayers(res.data)})
      fetch('/server/lobby/get_roles').then(res => res.json()).then(res => {if (res.success) setRoles(res.data)})
      fetch('/server/game/get_game_state/' + name + '/' + key).then(res => res.json()).then(res => {if (res.success) setGameState(res)})
      fetch('/server/game/get_my_state/' + name + '/' + key).then(res => res.json()).then(res => {if (res.success) setMyState(res)})
      fetch('/server/get_kicked').then(res => res.json()).then(res => {if (res.success) setKicked(res.data)})
    }, 500)

    return () => {
      clearInterval(interval)
    }
  })

  let custom_content = null

  const kick = (player) => {
    fetch('/server/lobby/kick/' + player)
  }

  const toggle = (role) => {
    fetch('/server/lobby/toggle/' + role)
  }
  
  const startGame = () => {
    fetch('/server/lobby/start_game').then(res => res.json()).then(res => setMessage(res.message))
  }

  const toggleProposal = (player) => {
    fetch('/server/game/toggle_proposal/' + name + '/' + key + '/' + player)
  }

  const proposeTeam = () => {
    fetch('/server/game/propose_team/' + name + '/' + key).then(res => res.json()).then(res => setMessage(res.message))
  }

  const vote = (vote) => {
    fetch('/server/game/vote/' + name + '/' + key + '/' + vote)
  }

  const render_vote = (vote) => vote === 'approve' ? '✅' : vote === 'disapprove' ? '🛑' : '...'

  const hammer = () => (gameState.captain + 4 - gameState.skips) % players.length;

  let players_html = null;
  // eslint-disable-next-line
  let roles_html = null;

  switch (mode) {
    case 'lobby':
      players_html = players.map(player => (
        <tr key={player}>
          <td><button onClick={() => kick(player)}>Kick</button></td>
          <td>{player}</td>
        </tr>
      ))
      let roles_html = Object.keys(roles).map(role => (
        <tr key={role}>
          <td><button onClick={() => toggle(role)}>{roles[role] ? "disable" : "enable"}</button></td>
          <td className={roles[role] ? 'activeRole' : 'inactiveRole'}>{role}</td>
        </tr>
      ))
      custom_content = (
        <div>
          <h1>Players</h1>
          <table><tbody>{players_html}</tbody></table>
          <h1>Roles</h1>
          <table><tbody>{roles_html}</tbody></table>
          <button onClick={() => startGame()}>Start Game!</button>
          <p>{message}</p>
        </div>
      )
      break
    case 'game':
      const captain = myState.i === gameState.captain
      const player_approve_box = (player, i) => (
        <button onClick={() => toggleProposal(player)} className={gameState.proposal.includes(player) ? 'active' : 'inactive'}>{gameState.proposal && gameState.proposal.includes(player) ? "Remove" : "Add"}</button>
      )
      const player_info_box = (player, i) => (
        <p>{gameState.actors.includes(player) ? 'Acted' : gameState.proposal.includes(player) ? 'On team' : ''}</p>
      )
      const did_vote_box = (player, i) =>  (
        <td>{i === myState.i ? render_vote(myState.vote) : gameState.votes.includes(player) ? "Voted📨" : "..."}</td>
      )
      const vote_details_box = (player, i) => (
        <td>{render_vote(gameState.votes[i])}</td>
      )
      players_html = players.map((player, i) => (
        <tr key={player}>
          <td>{captain && !gameState.proposed ? player_approve_box(player, i) : player_info_box(player, i)}</td>
          <td>{(i === hammer() && i === gameState.captain) ? "🟠🔨" : i === hammer() ? '🔨' : i === gameState.captain ? '🟠' : ''}</td>
          <td>{player}</td>
          <td>{myState.roles[i]}</td>
          {gameState.votes.length === players.length ? vote_details_box(player, i) : did_vote_box(player, i)}
        </tr>
        ))
      const captain_view = <p><button onClick={proposeTeam}>Propose the team</button></p>
      const approve_view = (
        <div>
          <button onClick={() => vote('approve')} className={myState.vote ==='approve' ? 'active' : 'inactive'}>Approve</button>
          <button onClick={() => vote('disapprove')} className={myState.vote ==='disapprove' ? 'active' : 'inactive'}>Reject</button>
        </div>
      )
      const failButton = !myState['good'] ? <button onClick={() => fetch('/server/game/act/' + name + '/' + key + '/fail')} className='fail'>Fail</button> : null
      const act_view = (
        <div>
          <button onClick={() => fetch('/server/game/act/' + name + '/' + key + '/success')} className='succeed'>Succeed</button>
          {failButton}
        </div>
      )
      const render_round = (round) => (
        (gameState.successes.includes(round) ? "W" : gameState.fails.includes(round) ? "L" : "_") + " "
      )
      const render_roundreq = (round) => {
        return gameState.rounds[round] + ", "
      }
      custom_content = (
        <div>
          <p>{[0, 1, 2, 3, 4].map(round => render_round(round))}</p>
          <p>Players required per mission (.1 = 2 fails needed): {[0, 1, 2, 3, 4].map(round => render_roundreq(round))}</p>
          <p>Rejected teams: {gameState.skips}</p> 
          <h1>Players</h1>
          <table className="table"><tbody>{players_html}</tbody></table>
          {gameState.assassin_mode ? '' : gameState.approved ? (gameState.proposal.includes(name) && myState.act === '' ? act_view : "It's time for a vote!") : gameState.proposed ? approve_view : captain ? captain_view : ""}
          <p>{message}</p>
        </div>
      )
      break
    default:
      break
  }

  const login = () => {
    const name = document.getElementById('name').value;
    const password = document.getElementById('password').value;
    window.location.pathname = "/user/" + name + '-' + password
  }

  if (!auth) {
    custom_content = (
      <div>
        <p>Authentication failed!</p>
        <p>Name</p>
        <textarea id="name" rows="1"></textarea>
        <p>Password</p>
        <textarea id="password" rows="1"></textarea>
        <button onClick={login}>Log in</button>
      </div>
    )
  }

  const reset_name = mode === 'lobby' ? 'unreset' : 'reset'
  const reset_button = auth ? <button onClick={() => fetch('/server/' + reset_name)}>{reset_name}</button> : null

  return (
    <Container className="justify-content-md-center">
      <h3>{gameState['hypertext']}</h3>
        {reset_button}
        Mode {mode}, Kicked: {kicked.map(kick => kick + ", ")}
        {custom_content}
    </Container>
  )
}

export default App
