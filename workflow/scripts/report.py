# MAGport Interactive HTML Report Generator
import sys
import json
from pathlib import Path
import pandas as pd

# Usge: python report.py summary.tsv out.html "MAGport Report" /path/to/input_dir

HTML_TMPL = """
<!doctype html>
<html>
<head>
<meta charset='utf-8'/>
<title>{title}</title>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<script src='https://cdn.plot.ly/plotly-2.29.1.min.js'></script>
<link rel='stylesheet' href='https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css'/>
<link rel='stylesheet' href='https://cdn.datatables.net/buttons/2.4.1/css/buttons.dataTables.min.css'/>
<script src='https://code.jquery.com/jquery-3.7.0.min.js'></script>
<script src='https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js'></script>
<script src='https://cdn.datatables.net/buttons/2.4.1/js/dataTables.buttons.min.js'></script>
<script src='https://cdn.datatables.net/buttons/2.4.1/js/buttons.html5.min.js'></script>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f8f9fa; }}
h1 {{ margin: 1em 0 0.5em 0; text-align: center; }}
.container {{ max-width: 1200px; margin: auto; padding: 1em; }}
.viz-block {{ background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001; margin-bottom: 2em; padding: 1em; }}
@media (max-width: 900px) {{ .viz-block, #summary {{ width: 100% !important; }} }}
</style>
</head>
<body>
<div class='container'>
<h1>{title}</h1>
<p>Analyzed <b>{n_mag}</b> MAGs from <code>{input_dir}</code></p>

<div class='viz-block'>
  <div id='quality_pie' style='width:100%;height:400px;'></div>
</div>
<div class='viz-block'>
  <div id='scatter' style='width:100%;height:500px;'></div>
</div>
<div class='viz-block'>
  <div id='taxa_bar' style='width:100%;height:500px;'></div>
</div>
<div class='viz-block'>
  <div id='dists' style='width:100%;height:500px;'></div>
</div>
<div class='viz-block'>
  <div id='radar' style='width:100%;height:500px;'></div>
</div>
<div class='viz-block'>
  <table id='summary' class='display' style='width:100%'></table>
</div>
</div>
<script>
const data = {data_json};
$(document).ready(function() {{
  // DataTable
  const cols = Object.keys(data[0] || {{}}).map(k => ({{title:k, data:k}}));
  const colIndex = Object.fromEntries(cols.map((c,i)=>[c.title,i]));
  const table = $('#summary').DataTable({{
    data: data,
    columns: cols,
    dom: 'Bfrtip',
    buttons: ['copyHtml5','csvHtml5','excelHtml5'],
    responsive: true
  }});

  // MIMAG Quality Pie
  let qCol = colIndex['MIMAG_level'] || colIndex['MIMAG_Quality'];
  if (qCol !== undefined) {{
    const qCounts = {{}};
    data.forEach(r=>{{ const q=r[cols[qCol].title]||'NA'; qCounts[q]=(qCounts[q]||0)+1; }});
    const labels = Object.keys(qCounts); const values = labels.map(k=>qCounts[k]);
    Plotly.newPlot('quality_pie', [{{type:'pie', labels, values, hole:0.3}}], {{title:'MIMAG Quality Distribution'}});
    document.getElementById('quality_pie').on('plotly_click', ev=>{{
      const lab = ev.points?.[0]?.label; if(!lab) return;
      table.column(qCol).search('^'+lab+'$', true, false).draw();
    }});
  }}

  // Completeness vs Contamination Scatter
  let compCol = colIndex['Completeness'], contCol = colIndex['Contamination'], magCol = colIndex['MAG'] || colIndex['MAG_ID'];
  if (compCol !== undefined && contCol !== undefined) {{
    const xs = data.map(r=>parseFloat(r[cols[contCol].title])||0);
    const ys = data.map(r=>parseFloat(r[cols[compCol].title])||0);
    const text = data.map(r=>r[cols[magCol]?.title]||'');
    const size = data.map(r=>Math.max(10, Math.min(80, (parseFloat(r['genome_size_bp']||r['Genome_Size'])||0)/5e5 )));
    const color = data.map(r=>r['GTDB_taxonomy']?.split(';')[1]?.replace('p__','')||'');
    Plotly.newPlot('scatter', [{
      x:xs,
      y:ys,
      text,
      mode:'markers',
      marker:{size, color, opacity:0.8},
      type:'scattergl',
  hovertemplate: 'MAG: %{{text}}<br>Contamination: %{{x}}<br>Completeness: %{{y}}<extra></extra>'
    }], {
      title:'Completeness vs Contamination', xaxis:{title:'Contamination (%)'}, yaxis:{title:'Completeness (%)'}
    });
    document.getElementById('scatter').on('plotly_selected', ev=>{{
      if(!ev || !ev.points) return; const ids = new Set(ev.points.map(p=>text[p.pointIndex]));
      $.fn.dataTable.ext.search = [function(settings, rowData, dataIndex) {{ return ids.size===0 || ids.has(rowData[magCol]); }}];
      table.draw();
    }});
  }}

  // GTDB Taxonomy Bar (Phylum)
  let gtdbCol = colIndex['GTDB_taxonomy'];
  if (gtdbCol !== undefined) {{
    const pCounts = {{}};
    data.forEach(r=>{{
      let phylum = (r['GTDB_taxonomy']||'').split(';')[1]||'Unassigned';
      phylum = phylum.replace('p__','')||'Unassigned';
      pCounts[phylum]=(pCounts[phylum]||0)+1;
    }});
    const taxa = Object.keys(pCounts).sort((a,b)=>pCounts[b]-pCounts[a]).slice(0,20);
    const vals = taxa.map(k=>pCounts[k]);
    Plotly.newPlot('taxa_bar', [{{type:'bar', x:vals, y:taxa, orientation:'h'}}], {{title:'Top Phyla (GTDB)'}});
    document.getElementById('taxa_bar').on('plotly_click', ev=>{{
      const ph = ev.points?.[0]?.y; if(!ph) return;
      table.column(gtdbCol).search(ph, true, false).draw();
    }});
  }}

  // Distributions: Genome Size, N50, GC
  const distFields = ['genome_size_bp','N50','GC'];
  const traces = distFields.filter(f=>colIndex[f]!==undefined).map(f=>({{x: data.map(r=>parseFloat(r[f])||0), type:'histogram', name:f, opacity:0.6}}));
  if (traces.length) {{ Plotly.newPlot('dists', traces, {{barmode:'overlay', title:'Distributions'}}); }}

  // Radargram for key traits
  let radarFields = ['Completeness','Contamination','GC','num_16S_rRNAs','num_ORFs'];
  let radarData = data.map(r=>radarFields.map(f=>parseFloat(r[f])||0));
  if (radarData.length) {{
    let means = radarFields.map((f,i)=>radarData.map(row=>row[i]).reduce((a,b)=>a+b,0)/radarData.length);
    Plotly.newPlot('radar', [{{type:'scatterpolar', r:means, theta:radarFields, fill:'toself', name:'Mean'}}], {{title:'Mean Traits Radargram'}});
  }}
}});
</script>
</body>
</html>
"""

def main(summary_tsv: Path, out_html: Path, title: str, input_dir: str):
    df = pd.read_csv(summary_tsv, sep='\t') if summary_tsv.exists() else pd.DataFrame()
    data_json = df.to_dict(orient='records') if not df.empty else []
    html = HTML_TMPL.format(title=title, n_mag=len(df), input_dir=input_dir, data_json=json.dumps(data_json))
    print(f"Writing report to {out_html} ...")
    out_html.write_text(html, encoding='utf-8')

if __name__ == "__main__":
    summary, outp, title, input_dir = sys.argv[1:5]
    main(Path(summary), Path(outp), title, input_dir)
