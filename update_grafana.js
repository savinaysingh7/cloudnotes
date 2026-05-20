const fs = require('fs');
const file = 'monitoring/grafana/provisioning/dashboards/cloudnotes.json';
let data = JSON.parse(fs.readFileSync(file));

const hasJobVar = data.templating.list.find(v => v.name === 'job');
if (!hasJobVar) {
  data.templating.list.push({
    "allValue": null,
    "current": { "selected": true, "text": "All", "value": "$__all" },
    "datasource": { "type": "prometheus", "uid": "${DS_PROMETHEUS}" },
    "definition": "label_values(up, job)",
    "hide": 0,
    "includeAll": true,
    "multi": true,
    "name": "job",
    "options": [],
    "query": "label_values(up, job)",
    "refresh": 1,
    "regex": "",
    "skipUrlSync": false,
    "sort": 1,
    "type": "query"
  });
}

if(data.panels[0]) data.panels[0].targets[0].expr = 'sum(rate(flask_http_request_total{job=~"$job"}[5m]))';
if(data.panels[1]) data.panels[1].targets[0].expr = 'histogram_quantile(0.95, sum(rate(flask_http_request_duration_seconds_bucket{job=~"$job"}[5m])) by (le))';
if(data.panels[2]) data.panels[2].targets[0].expr = 'sum(notes_created_total{job=~"$job"})';
if(data.panels[3]) data.panels[3].targets[0].expr = 'sum(notes_updated_total{job=~"$job"})';
if(data.panels[4]) data.panels[4].targets[0].expr = 'sum(notes_deleted_total{job=~"$job"})';
if(data.panels[5]) data.panels[5].targets[0].expr = 'up{job=~"$job"}';

fs.writeFileSync(file, JSON.stringify(data, null, 2));
console.log('Grafana Dashboard Updated Successfully!');
