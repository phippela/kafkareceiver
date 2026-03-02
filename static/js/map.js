(async function(){
  const map = L.map('map').setView([0,0], 2);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
  try {
    const res = await fetch('/api/messages');
    const msgs = await res.json();
    let bounds = [];
// Replace marker creation with this: map markers use simple SVG symbols per category.
function categoryFromType(t){
  t = (t||'').toLowerCase();
  if (t.includes('tank') || t.includes('armor') || t.includes('arm')) return 'armor';
  if (t.includes('infantry') || t.includes('inf')) return 'infantry';
  if (t.includes('uas') || t.includes('uav') || t.includes('air') || t.includes('a-')) return 'aircraft';
  if (t.includes('arty') || t.includes('art') || t.includes('gun')) return 'artillery';
  return 'unknown';
}

function svgDataUri(letter, color){
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='36' height='36' viewBox='0 0 36 36'>
    <circle cx='18' cy='18' r='16' fill='${color}' stroke='black' stroke-width='1'/>
    <text x='18' y='23' font-family='Arial' font-size='14' font-weight='bold' text-anchor='middle' fill='white'>${letter}</text>
  </svg>`;
  return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
}

function iconForCategory(cat){
  switch(cat){
    case 'infantry': return L.icon({iconUrl: svgDataUri('I','#2b8cbe'), iconSize:[36,36], iconAnchor:[18,18]});
    case 'armor':    return L.icon({iconUrl: svgDataUri('T','#e34a33'), iconSize:[36,36], iconAnchor:[18,18]});
    case 'aircraft': return L.icon({iconUrl: svgDataUri('A','#31a354'), iconSize:[36,36], iconAnchor:[18,18]});
    case 'artillery':return L.icon({iconUrl: svgDataUri('R','#ffb400'), iconSize:[36,36], iconAnchor:[18,18]});
    default:         return L.icon({iconUrl: svgDataUri('?', '#6c757d'), iconSize:[36,36], iconAnchor:[18,18]});
  }
}

// inside your fetch -> msgs.forEach loop:
msgs.forEach(m=>{
  if (m.lat && m.lon){
    const cat = categoryFromType(m.type);
    const icon = iconForCategory(cat);
    const marker = L.marker([m.lat,m.lon], {icon}).addTo(map);
    marker.bindPopup(`<a href="/message/${m.id}">${m.uid || m.id}</a><br>${m.type || ''}`);
    bounds.push([m.lat,m.lon]);
  }
});
    if (bounds.length) map.fitBounds(bounds);
  } catch(e){
    console.error(e);
  }
})();