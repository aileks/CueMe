import{c as l,j as e,L as t}from"./index-0oqpAsjj.js";import{S as n}from"./square-pen-Cj1ElNlj.js";/**
 * @license lucide-react v0.509.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const i=[["path",{d:"M15 3h6v6",key:"1q9fwt"}],["path",{d:"M10 14 21 3",key:"gplh6r"}],["path",{d:"M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6",key:"a6xqqp"}]],c=l("external-link",i);/**
 * @license lucide-react v0.509.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const r=[["path",{d:"M3 6h18",key:"d0wm0j"}],["path",{d:"M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6",key:"4alrt4"}],["path",{d:"M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2",key:"v07s0e"}],["line",{x1:"10",x2:"10",y1:"11",y2:"17",key:"1uufr5"}],["line",{x1:"14",x2:"14",y1:"11",y2:"17",key:"xtxkd"}]],d=l("trash-2",r);function h(){const a=[];return e.jsxs("div",{className:"mx-auto max-w-4xl",children:[e.jsxs("div",{className:"mb-6 flex items-center justify-between",children:[e.jsx("h1",{className:"text-3xl font-bold",children:"My Playlists"}),e.jsx(t,{to:"/create",className:"neu-button",children:"Create New Playlist"})]}),a.length===0?e.jsx("div",{className:"neu-card py-10 text-center",children:e.jsx("h3",{className:"text-2xl font-semibold",children:"Coming Soon!"})}):e.jsx("div",{className:"grid gap-4",children:a.map(s=>e.jsx("div",{className:"neu-card",children:e.jsxs("div",{className:"flex items-start justify-between",children:[e.jsxs("div",{children:[e.jsx("h2",{className:"text-xl font-semibold",children:s.name}),e.jsxs("p",{className:"text-muted-foreground",children:[s.trackCount," tracks · Created on"," ",s.createdAt]})]}),e.jsxs("div",{className:"flex gap-2",children:[e.jsx(t,{to:`/playlists/${s.id}`,className:"neu-button","aria-label":"View playlist",children:e.jsx(c,{size:18})}),e.jsx("button",{className:"neu-button","aria-label":"Edit playlist",children:e.jsx(n,{size:18})}),e.jsx("button",{className:"neu-button","aria-label":"Delete playlist",children:e.jsx(d,{size:18})})]})]})},s.id))})]})}export{h as default};
