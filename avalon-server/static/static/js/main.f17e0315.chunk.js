(this["webpackJsonpavalon-client"]=this["webpackJsonpavalon-client"]||[]).push([[0],{13:function(e,t,n){},15:function(e,t,n){"use strict";n.r(t);var a=n(0),c=n.n(a),r=n(4),l=n.n(r),o=n(1),s=(n(13),n(17));var u=function(){var e=Object(a.useState)("lobby"),t=Object(o.a)(e,2),n=t[0],r=t[1],l=Object(a.useState)([]),u=Object(o.a)(l,2),i=u[0],m=u[1],p=Object(a.useState)({}),f=Object(o.a)(p,2),h=f[0],v=f[1],d=Object(a.useState)(!1),b=Object(o.a)(d,2),E=b[0],g=b[1],j=Object(a.useState)(""),k=Object(o.a)(j,2),y=k[0],O=k[1],_=Object(a.useState)({round:0,successes:[],fails:[],mission:0,captain:0,skips:0,proposed:!1,approved:!1,proposal:[],votes:[],hypertext:"ReactJS is legendary",assassin_mode:!1}),w=Object(o.a)(_,2),C=w[0],S=w[1],N=Object(a.useState)({i:0,roles:[],vote:"",act:"",assassin:!1}),x=Object(o.a)(N,2),I=x[0],P=x[1],R=window.location.pathname.split("/"),W=R[R.length-1].split("-"),A=Object(o.a)(W,2),B=A[0],F=A[1];Object(a.useEffect)((function(){var e=setInterval((function(){fetch("/server/auth/"+B+"/"+F).then((function(e){return e.json()})).then((function(e){return g(e.success)})),fetch("/server/get_mode").then((function(e){return e.json()})).then((function(e){e.success&&r(e.data)})),fetch("/server/lobby/get_players").then((function(e){return e.json()})).then((function(e){e.success&&m(e.data)})),fetch("/server/lobby/get_roles").then((function(e){return e.json()})).then((function(e){e.success&&v(e.data)})),fetch("/server/game/get_game_state/"+B+"/"+F).then((function(e){return e.json()})).then((function(e){e.success&&S(e)})),fetch("/server/game/get_my_state/"+B+"/"+F).then((function(e){return e.json()})).then((function(e){e.success&&P(e)}))}),250);return function(){clearInterval(e)}}),[i,n,h,B,F]);var G=c.a.createElement("p",null,"[",n,"]"),J=null,V=function(e){fetch("/server/game/vote/"+B+"/"+F+"/"+e)},H=function(e){return"approve"===e?"\u2705":"disapprove"===e?"\ud83d\uded1":"..."},K=null;switch(n){case"lobby":K=i.map((function(e){return c.a.createElement("tr",{key:e},c.a.createElement("td",null,c.a.createElement("button",{onClick:function(){return function(e){fetch("/server/lobby/kick/"+e)}(e)}},"Kick")),c.a.createElement("td",null,e))}));var M=Object.keys(h).map((function(e){return c.a.createElement("tr",{key:e},c.a.createElement("td",null,c.a.createElement("button",{onClick:function(){return function(e){fetch("/server/lobby/toggle/"+e)}(e)}},h[e]?"disable":"enable")),c.a.createElement("td",null,e))}));J=c.a.createElement("div",null,c.a.createElement("h1",null,"Players"),c.a.createElement("table",null,c.a.createElement("tbody",null,K)),c.a.createElement("h1",null,"Roles"),c.a.createElement("table",null,c.a.createElement("tbody",null,M)),c.a.createElement("button",{onClick:function(){fetch("/server/lobby/start_game").then((function(e){return e.json()})).then((function(e){return O(e.message)}))}},"Start Game!"),c.a.createElement("p",null,y));break;case"game":var Q=I.i===C.captain,T=function(e,t){return c.a.createElement("button",{onClick:function(){return function(e){fetch("/server/game/toggle_proposal/"+B+"/"+F+"/"+e)}(e)},className:C.proposal.includes(e)?"active":"inactive"},C.proposal&&C.proposal.includes(e)?"Remove":"Add")};K=i.map((function(e,t){return c.a.createElement("tr",{key:e},c.a.createElement("td",null,Q&&!C.proposed?T(e):function(e,t){return c.a.createElement("p",null,C.proposal.includes(e)?"On team":"")}(e)),c.a.createElement("td",null,t===(C.captain+5-C.skips)%i.length?"Hammer":t===C.captain?"Captain":""),c.a.createElement("td",null,e),c.a.createElement("td",null,I.roles[t]),C.votes.length===i.length?function(e,t){return c.a.createElement("td",null,H(C.votes[t]))}(0,t):function(e,t){return c.a.createElement("td",null,t===I.i?H(I.vote):C.votes.includes(e)?"Voted\ud83d\udce8":"...")}(e,t))}));var L=c.a.createElement("p",null,c.a.createElement("button",{onClick:function(){fetch("/server/game/propose_team/"+B+"/"+F).then((function(e){return e.json()})).then((function(e){return O(e.message)}))}},"Propose the team")),X=c.a.createElement("div",null,c.a.createElement("button",{onClick:function(){return V("approve")},className:"approve"===I.vote?"active":"inactive"},"Approve"),c.a.createElement("button",{onClick:function(){return V("disapprove")},className:"disapprove"===I.vote?"active":"inactive"},"Reject")),$=c.a.createElement("div",null,c.a.createElement("button",{onClick:function(){return fetch("/server/game/act/"+B+"/"+F+"/success")},className:"succeed"},"Succeed"),c.a.createElement("button",{onClick:function(){return fetch("/server/game/act/"+B+"/"+F+"/fail")},className:"fail"},"Fail"));J=c.a.createElement("div",null,c.a.createElement("h3",null,C.hypertext),c.a.createElement("p",null,[0,1,2,3,4].map((function(e){return function(e){return(C.successes.includes(e)?"W":C.fails.includes(e)?"L":"_")+" "}(e)}))),c.a.createElement("p",null,"Rejected teams: ",C.skips),c.a.createElement("h1",null,"Players"),c.a.createElement("table",{className:"table"},c.a.createElement("tbody",null,K)),C.assassin_mode?"":C.approved?C.proposal.includes(B)&&""===I.act?$:"It's time for a vote!":C.proposed?X:Q?L:"",c.a.createElement("p",null,y))}return E||(J=c.a.createElement("p",null,"Authentication failed!")),c.a.createElement(s.a,{className:"justify-content-md-center"},G,J)};Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));n(14);l.a.render(c.a.createElement(c.a.StrictMode,null,c.a.createElement("link",{rel:"stylesheet",href:"https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css",integrity:"sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh",crossOrigin:"anonymous"}),c.a.createElement(u,null)),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}))},8:function(e,t,n){e.exports=n(15)}},[[8,1,2]]]);
//# sourceMappingURL=main.f17e0315.chunk.js.map