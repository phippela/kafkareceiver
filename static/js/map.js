(async function(){
  const map = L.map('map').setView([0,0], 2);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);
  try {
    const res = await fetch('/api/messages');
    const msgs = await res.json();
    let bounds = [];
    msgs.forEach(m=>{
      if (m.lat && m.lon){
        const marker = L.marker([m.lat,m.lon]).addTo(map);
        marker.bindPopup(`<a href="/message/${m.id}">${m.uid || m.id}</a><br>${m.type || ''}`);
        bounds.push([m.lat,m.lon]);
      }
    });
    if (bounds.length) map.fitBounds(bounds);
  } catch(e){
    console.error(e);
  }
})();