form_div = document.getElementById('form-div');
result_div = document.getElementById('result-div');
result_div.style.display = "none";
var inputData = null;

document.getElementById('back-btn').addEventListener('click', function(e) {
  form_div.style.display = "";
  result_div.style.display = "none";
  document.getElementById('input-form').reset();
  inputData = null
});

document.getElementById('input-form').addEventListener('submit', function(e) {
  e.preventDefault();
  form_div.style.display = "none";
  result_div.style.display = "";

  const formData = new FormData(e.target);
  inputData = Object.fromEntries(formData.entries());
  const idTemplate = document.getElementById('id-template');
  idTemplate.innerHTML = '';
  var i = 1;
  var ents = new Array();
  for(const key in inputData){
    console.log(key);
    text = document.createElement('p');
    text.textContent = key.toUpperCase() + ': ' + inputData[key];
    text.style.width = '25%'
    text.style.padding = '10px'
    ents.push(text);
    if(i%4 == 0){
      const div = document.createElement('div');
      div.style.display = 'flex';
      ents.forEach((ent) => div.appendChild(ent));
      ents = new Array();
      idTemplate.appendChild(div);
    }
    i+=1
  }
  fetch('/analyze', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    displayGraphs(data.graph_data);

  })
  .catch(error => console.error(error));
});


function displayGraphs(graphData) {
  const graphContainer = document.getElementById('graph-container');
  graphContainer.innerHTML = '';
  graphData.forEach((trace, index) => {
    const div = document.createElement('div');
    div.id = `graph-${index + 1}`;
    graphContainer.appendChild(div);

    const layout = {
      plot_bgcolor: '#070F2B',
      paper_bgcolor: '#282A4F',
      font: { color: '#f5f5f5' },
      title: trace.name,
      xaxis: { title: 'X-axis' },
      yaxis: { title: 'Y-axis' },
      hovermode: 'closest'
    };

    Plotly.newPlot(`graph-${index + 1}`, [trace], layout);
  });
}

function displayMetrics(metrics) {
  const metricsContainer = document.getElementById('metrics-container');
  metricsContainer.innerHTML = '';

  const metricsList = document.createElement('ul');
  for (const [key, value] of Object.entries(metrics)) {
    const metricItem = document.createElement('li');
    metricItem.textContent = `${key}: ${value}`;
    metricsList.appendChild(metricItem);
  }

  metricsContainer.appendChild(metricsList);
}

document.getElementById('volatility').addEventListener('input', updateVolatilityValue);

function updateVolatilityValue() {
  const volatilityValue = document.getElementById('volatility-value');
  volatilityValue.textContent = this.value;
}

function updateMeanVolatilityValue() {
  const meanVolatilityValue = document.getElementById('mean-volatility-value');
  meanVolatilityValue.textContent = this.value;
}