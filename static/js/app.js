const charts = {};
async function getJSON(url){const r=await fetch(url);const d=await r.json();if(!r.ok)throw new Error(d.error||"Request failed");return d}
function card(label,value){return `<div class="col-6 col-md-3"><div class="stat"><div class="label">${label}</div><div class="value">${value}</div></div></div>`}
function makeChart(id,type,labels,datasets){if(charts[id])charts[id].destroy();charts[id]=new Chart(document.getElementById(id),{type,data:{labels,datasets:datasets.map((d,i)=>({...d,borderWidth:2,tension:.3}))},options:{responsive:true,plugins:{legend:{position:"bottom"}}}})}
async function refresh(){
 const d=await getJSON("/api/dashboard");
 document.getElementById("cards").innerHTML=[
 card("Monitored locations",d.locations_count),card("Average traffic",d.average_traffic.toLocaleString()),
 card("Average AQI",d.average_aqi),card("High-traffic readings",d.high_traffic_readings),
 card("High-AQI readings",d.high_aqi_readings),card("Highest traffic",d.highest_traffic_location),
 card("Highest average AQI",d.highest_aqi_location),card("Dataset",d.sample_data?"Sample":"Uploaded")
 ].join("");
 makeChart("trafficChart","bar",d.locations,[{label:"Average vehicles",data:d.traffic_averages}]);
 makeChart("aqiChart","bar",d.locations,[{label:"Average AQI",data:d.aqi_averages}]);
 const t=await getJSON("/api/traffic"),a=await getJSON("/api/air-quality");
 makeChart("trafficTrend","line",t.days,t.datasets);makeChart("aqiTrend","line",a.days,a.datasets);
 const p=await getJSON("/api/predictions");
 document.getElementById("predictions").textContent="TRAFFIC\\n"+p.traffic.map(x=>`${x.location}: ${x.estimate} (${x.trend})`).join("\\n")+"\\n\\nAQI\\n"+p.aqi.map(x=>`${x.location}: ${x.estimate} (${x.trend})`).join("\\n");
 const m=await getJSON("/api/analytics");
 document.getElementById("analytics").textContent=`Traffic stats: ${JSON.stringify(m.traffic_stats)}\\nAQI stats: ${JSON.stringify(m.aqi_stats)}\\n\\nTraffic ranking:\\n${m.traffic_rank.map(x=>`${x.location}: ${x.average}`).join("\\n")}\\n\\nAQI ranking:\\n${m.aqi_rank.map(x=>`${x.location}: ${x.average}`).join("\\n")}\\n\\nAnomaly flags (${m.anomalies.length}):\\n${m.anomalies.slice(0,20).map(x=>`${x.metric} — ${x.location}, Day ${x.day}: ${x.value} (${x.reason})`).join("\\n")}`;
}
async function loadAI(url,target){const el=document.getElementById(target);el.textContent="Generating…";try{const d=await fetch(url,{method:"POST"}).then(r=>r.json());el.textContent=`${d.mode.toUpperCase()} MODE\\n\\n${d.content}`}catch(e){el.textContent=e.message}}
document.getElementById("askForm").addEventListener("submit",async e=>{e.preventDefault();const el=document.getElementById("answer");el.textContent="Thinking…";try{const r=await fetch("/api/ai/ask",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question:document.getElementById("question").value})});const d=await r.json();if(!r.ok)throw new Error(d.error);el.textContent=`${d.mode.toUpperCase()} MODE\\n\\n${d.content}`}catch(err){el.textContent=err.message}});
document.getElementById("uploadForm").addEventListener("submit",async e=>{e.preventDefault();const msg=document.getElementById("uploadMessage");msg.textContent="Uploading…";try{const r=await fetch("/api/upload-dataset",{method:"POST",body:new FormData(e.target)});const d=await r.json();if(!r.ok)throw new Error(d.error);msg.textContent=d.message;await refresh()}catch(err){msg.textContent=err.message}});
async function restoreSample(){const r=await fetch("/api/restore-sample",{method:"POST"});const d=await r.json();document.getElementById("uploadMessage").textContent=d.message;await refresh()}
async function downloadReport(){const r=await fetch("/api/ai/generate-report",{method:"POST"});if(!r.ok){const d=await r.json();alert(d.error||"Report failed");return}const blob=await r.blob();const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="smart_city_weekly_report.pdf";a.click();URL.revokeObjectURL(a.href)}
refresh().catch(e=>alert(e.message));
