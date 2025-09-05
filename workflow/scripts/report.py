from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import pandas as pd

HTML_TMPL = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<script src="https://cdn.plot.ly/plotly-2.29.1.min.js"></script>
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css" />
<link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.1/css/buttons.dataTables.min.css" />
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.1/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.1/js/buttons.html5.min.js"></script>
</head>
<body>
<h1>{title}</h1>
<p>Analyzed {n_mag} MAGs from {input_dir}</p>
<div id="cards"></div>
<div id="quality_pie" style="width:900px;height:400px;"></div>
<div id="scatter" style="width:900px;height:500px;"></div>
<div id="taxa_bar" style="width:900px;height:500px;"></div>
<div id="dists" style="width:900px;height:500px;"></div>
<table id="summary" class="display" style="width:100%"></table>
<script>
const data = {data_json};
$(document).ready(function() {{
  const cols = Object.keys(data[0] || {{}}).map(k => ({{title:k, data:k}}));
  const colIndex = Object.fromEntries(cols.map((c,i)=>[c.title,i]));
  const table = $('#summary').DataTable({{
    data: data,
    columns: cols,
    dom: 'Bfrtip',
    buttons: ['copyHtml5','csvHtml5','excelHtml5']
  }});

  // Quality pie
  if (colIndex['MIMAG_Quality'] !== undefined) {{
    const qCounts = {{}};
    data.forEach(r=>{{ const q=r['MIMAG_Quality']||'NA'; qCounts[q]=(qCounts[q]||0)+1; }});
    const labels = Object.keys(qCounts); const values = labels.map(k=>qCounts[k]);
    Plotly.newPlot('quality_pie', [{{type:'pie', labels, values, hole:0.3}}], {{title:'MIMAG Quality Distribution'}});
    const pie = document.getElementById('quality_pie');
    pie.on('plotly_click', ev=>{{
      const lab = ev.points?.[0]?.label; if(!lab) return; 
      table.column(colIndex['MIMAG_Quality']).search('^'+lab+'$', true, false).draw();
    }});
  }}

  // Completeness vs Contamination scatter
  if (['Completeness','Contamination'].every(k=>colIndex[k]!==undefined)) {{
    const xs = data.map(r=>parseFloat(r['Contamination'])||0);
    const ys = data.map(r=>parseFloat(r['Completeness'])||0);
    const text = data.map(r=>r['MAG_ID']||'');
    const size = data.map(r=>Math.max(4, Math.min(40, (parseFloat(r['Genome_Size'])||0)/1e6 )));
    const color = data.map(r=>r['Phylum']||'');
    Plotly.newPlot('scatter', [{{x:xs,y:ys,text,mode:'markers',marker:{{size, color}}, type:'scattergl'}}], {{
      title:'Completeness vs Contamination', xaxis:{{title:'Contamination (%)'}}, yaxis:{{title:'Completeness (%)'}}
    }});
    const sc = document.getElementById('scatter');
    sc.on('plotly_selected', ev=>{{
      if(!ev || !ev.points) return; const ids = new Set(ev.points.map(p=>text[p.pointIndex]));
      $.fn.dataTable.ext.search = [function(settings, rowData, dataIndex) {{ return ids.size===0 || ids.has(rowData[colIndex['MAG_ID']]); }}];
      table.draw();
    }});
  }}

  // Taxonomic composition bar (by Phylum)
  if (colIndex['Phylum'] !== undefined) {{
    const pCounts = {{}}; data.forEach(r=>{{ const p=r['Phylum']||'Unassigned'; pCounts[p]=(pCounts[p]||0)+1; }});
    const taxa = Object.keys(pCounts).sort((a,b)=>pCounts[b]-pCounts[a]).slice(0,20);
    const vals = taxa.map(k=>pCounts[k]);
    Plotly.newPlot('taxa_bar', [{{type:'bar', x:vals, y:taxa, orientation:'h'}}], {{title:'Top Phyla'}});
    const bar = document.getElementById('taxa_bar');
    bar.on('plotly_click', ev=>{{
      const ph = ev.points?.[0]?.y; if(!ph) return;
      table.column(colIndex['Phylum']).search('^'+ph+'$', true, false).draw();
    }});
  }}

  // Distributions (Genome Size, N50)
  const distFields = ['Genome_Size','N50','GC_Content'];
  const traces = distFields.filter(f=>colIndex[f]!==undefined).map(f=>({{x: data.map(r=>parseFloat(r[f])||0), type:'histogram', name:f, opacity:0.6}}));
  if (traces.length) {{ Plotly.newPlot('dists', traces, {{barmode:'overlay', title:'Distributions'}}); }}
}});
</script>
</body>
</html>
"""


def main(summary_tsv: Path, out_html: Path, title: str, input_dir: str):
  df = pd.read_csv(summary_tsv, sep='\t') if summary_tsv.exists() else pd.DataFrame()
  data_json = df.to_dict(orient='records') if not df.empty else []
  html = HTML_TMPL.format(title=title, n_mag=len(df), input_dir=input_dir, data_json=json.dumps(data_json))
  out_html.write_text(html, encoding='utf-8')

if __name__ == "__main__":
    summary, outp, title, input_dir = sys.argv[1:5]
    main(Path(summary), Path(outp), title, input_dir)
