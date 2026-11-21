(() => {
  'use strict';

  const data = JSON.parse(document.getElementById('graph-data').textContent);
  const run = JSON.parse(document.getElementById('run-data').textContent);
  const nodes = new Map(data.nodes.map(node => [node.id, node]));
  const edges = new Map(data.edges.map(edge => [edge.id, edge]));
  const layers = new Map(data.layers.map(layer => [layer.id, layer]));
  const relationLabels = new Map(data.relationTypes.map(relation => [relation.id, relation.label]));
  const colours = {objectives: '#23786e', stakeholders: '#a6503d', scope: '#8b6d28'};
  const namespace = 'http://www.w3.org/2000/svg';
  const svg = document.getElementById('network');
  const inspector = document.getElementById('inspector');
  const state = {layout: 'layered', tab: 'graph', node: 'sustain_carbon', edge: null, guide: 'carbon', layer: 'all', relation: 'all', search: '', neighbourhood: false};
  const guides = [
    {id: 'carbon', label: 'Carbon', node: 'sustain_carbon', question: 'Who and what connects to carbon?', text: 'The notebook places carbon alongside proposed choices. Its links reach stakeholders and track work. Read which records sit on each side of the arrows before interpreting the relationship.'},
    {id: 'faster', label: 'Faster trains', node: 'faster_trains', question: 'Where does a faster service meet delivery?', text: 'The faster-trains objective connects to a station, two stakeholders and new trains. The layer boundaries make those different kinds of record visible.'},
    {id: 'station', label: 'A new station', node: 'new_station', question: 'What kind of record is a new station?', text: 'The notebook places the station in objectives, beside carbon and speed. Its connection to civil works raises a useful modelling question about the boundary between an objective and a proposed solution.'}
  ];
  const nodeOrder = {
    objectives: ['sustain_carbon', 'faster_trains', 'new_station', 'New_construction_method'],
    stakeholders: ['Town_council', 'Train_manufacturer', 'Safety_Board', 'Train_Operator'],
    scope: ['new_track', 'new_trains', 'civil_works', 'in_cab_signalling', 'telecoms']
  };

  function element(tag, className, text) {
    const result = document.createElement(tag);
    if (className) result.className = className;
    if (text !== undefined) result.textContent = text;
    return result;
  }

  function svgElement(tag, attributes, text) {
    const result = document.createElementNS(namespace, tag);
    for (const [key, value] of Object.entries(attributes)) result.setAttribute(key, value);
    if (text !== undefined) result.textContent = text;
    return result;
  }

  function linksFor(id) {
    return data.edges.filter(edge => edge.source === id || edge.target === id);
  }

  function adjacentIds(id) {
    const connected = new Set([id]);
    for (const edge of linksFor(id)) {
      connected.add(edge.source);
      connected.add(edge.target);
    }
    return connected;
  }

  function visibleModel() {
    const neighbourhood = state.neighbourhood && state.node ? adjacentIds(state.node) : null;
    const term = state.search.trim().toLowerCase();
    let visibleNodes = data.nodes.filter(node =>
      (state.layer === 'all' || node.layer === state.layer) &&
      (!neighbourhood || neighbourhood.has(node.id)) &&
      (!term || [node.label, node.sourceName, ...node.originalNames].join(' ').toLowerCase().includes(term))
    );
    let ids = new Set(visibleNodes.map(node => node.id));
    const visibleEdges = data.edges.filter(edge => ids.has(edge.source) && ids.has(edge.target) && (state.relation === 'all' || edge.relation === state.relation));
    if (state.relation !== 'all') {
      ids = new Set(visibleEdges.flatMap(edge => [edge.source, edge.target]));
      visibleNodes = visibleNodes.filter(node => ids.has(node.id));
    }
    return {nodes: visibleNodes, edges: visibleEdges};
  }

  function positions() {
    const result = new Map();
    for (const [layerIndex, layer] of data.layers.entries()) {
      const order = nodeOrder[layer.id] || data.nodes.filter(node => node.layer === layer.id).map(node => node.id);
      for (const [index, id] of order.entries()) result.set(id, {x: 150 + 300 * layerIndex, y: 143 + index * 112, column: layerIndex});
    }
    if (state.layout === 'flat') {
      const sequence = [...data.nodes].sort((a, b) => a.label.localeCompare(b.label));
      for (const [index, node] of sequence.entries()) {
        const angle = -Math.PI / 2 + index * 2 * Math.PI / sequence.length;
        result.set(node.id, {x: 450 + Math.cos(angle) * 334, y: 352 + Math.sin(angle) * 258, column: null});
      }
    }
    return result;
  }

  function edgePath(edge, points) {
    const source = points.get(edge.source);
    const target = points.get(edge.target);
    const boxWidth = state.layout === 'flat' ? 150 : 174;
    const halfHeight = 33;
    if (state.layout === 'flat') {
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const ratio = Math.min(boxWidth / 2 / Math.max(Math.abs(dx), 1), halfHeight / Math.max(Math.abs(dy), 1));
      const sx = source.x + dx * ratio;
      const sy = source.y + dy * ratio;
      const tx = target.x - dx * ratio;
      const ty = target.y - dy * ratio;
      return `M ${sx} ${sy} L ${tx} ${ty}`;
    }
    if (source.column === target.column) {
      const side = source.column === 2 ? 1 : -1;
      const x = source.x + side * boxWidth / 2;
      const curveX = x + side * (27 + Math.abs(target.y - source.y) * .12);
      return `M ${x} ${source.y} C ${curveX} ${source.y}, ${curveX} ${target.y}, ${x} ${target.y}`;
    }
    const direction = Math.sign(target.x - source.x);
    const sx = source.x + direction * boxWidth / 2;
    const tx = target.x - direction * boxWidth / 2;
    if (Math.abs(source.column - target.column) === 2) {
      const railY = (source.y + target.y) / 2 < 310 ? 25 : 670;
      return `M ${sx} ${source.y} C ${sx + direction * 160} ${railY}, ${tx - direction * 160} ${railY}, ${tx} ${target.y}`;
    }
    const middle = (sx + tx) / 2;
    return `M ${sx} ${source.y} C ${middle} ${source.y}, ${middle} ${target.y}, ${tx} ${target.y}`;
  }

  function wrapLabel(label, maxLength) {
    const lines = [''];
    for (const word of label.split(' ')) {
      const last = lines.length - 1;
      if ((lines[last] + ' ' + word).trim().length > maxLength && lines[last]) lines.push(word);
      else lines[last] = (lines[last] + ' ' + word).trim();
    }
    return lines;
  }

  function selectNode(id, guide = null) {
    state.node = id;
    state.edge = null;
    state.guide = guide;
    updateHash(guide ? 'guide' : 'node', guide || id);
    render();
  }

  function selectEdge(id) {
    state.edge = id;
    state.guide = null;
    updateHash('edge', id);
    render();
  }

  function updateHash(key, value) {
    const hash = value ? '#' + key + '=' + encodeURIComponent(value) : '';
    history.replaceState(null, '', location.pathname + location.search + hash);
  }

  function keyboardClick(event, action) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      action();
    }
  }

  function renderGraph(model) {
    svg.replaceChildren();
    const defs = svgElement('defs', {});
    for (const [id, colour] of [['normal', '#78958a'], ['active', '#347c6c'], ['selected', '#a6503d']]) {
      const marker = svgElement('marker', {id: 'arrow-' + id, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 6, markerHeight: 6, orient: 'auto-start-reverse'});
      marker.append(svgElement('path', {d: 'M 1 1 L 9 5 L 1 9 z', fill: colour}));
      defs.append(marker);
    }
    svg.append(defs);
    if (state.layout === 'layered') {
      for (const [index, layer] of data.layers.entries()) {
        const x = 30 + index * 300;
        svg.append(svgElement('rect', {x, y: 82, width: 240, height: 563, rx: 9, class: 'layer-background'}));
        svg.append(svgElement('text', {x: x + 120, y: 43, 'text-anchor': 'middle', class: 'layer-heading'}, layer.label));
        const total = data.nodes.filter(node => node.layer === layer.id).length;
        svg.append(svgElement('text', {x: x + 120, y: 65, 'text-anchor': 'middle', class: 'layer-subheading'}, total + ' records'));
      }
    } else {
      svg.append(svgElement('ellipse', {cx: 450, cy: 352, rx: 428, ry: 323, class: 'flat-background'}));
      svg.append(svgElement('text', {x: 450, y: 355, 'text-anchor': 'middle', class: 'flat-caption'}, 'The same model'));
      svg.append(svgElement('text', {x: 450, y: 379, 'text-anchor': 'middle', class: 'layer-subheading'}, 'Layer grouping removed'));
    }
    const points = positions();
    const focused = state.edge ? new Set([edges.get(state.edge).source, edges.get(state.edge).target]) : state.node ? adjacentIds(state.node) : null;
    const drawnEdges = [...model.edges].sort((a, b) => Number(a.id === state.edge || a.source === state.node || a.target === state.node) - Number(b.id === state.edge || b.source === state.node || b.target === state.node));
    for (const edge of drawnEdges) {
      const emphasis = state.edge ? edge.id === state.edge : edge.source === state.node || edge.target === state.node;
      const selected = state.edge === edge.id;
      const style = ['network-edge', emphasis ? 'is-emphasis' : '', focused && !emphasis ? 'is-muted' : '', selected ? 'is-selected' : '', edge.weight === null ? 'is-uncertain' : ''].filter(Boolean).join(' ');
      const path = edgePath(edge, points);
      svg.append(svgElement('path', {d: path, class: style, 'marker-end': edge.directed ? `url(#arrow-${selected ? 'selected' : emphasis ? 'active' : 'normal'})` : '', 'data-edge': edge.id}));
      const hit = svgElement('path', {d: path, class: 'edge-hit', tabindex: 0, role: 'button', 'aria-label': `${nodes.get(edge.source).label} to ${nodes.get(edge.target).label}. ${edge.label}. Inspect source records.`, 'aria-pressed': selected, 'data-edge-control': edge.id});
      hit.append(svgElement('title', {}, `${nodes.get(edge.source).label} → ${nodes.get(edge.target).label}`));
      hit.addEventListener('click', () => selectEdge(edge.id));
      hit.addEventListener('keydown', event => keyboardClick(event, () => selectEdge(edge.id)));
      svg.append(hit);
    }
    for (const node of model.nodes) {
      const position = points.get(node.id);
      const width = state.layout === 'flat' ? 150 : 174;
      const active = state.node === node.id && !state.edge;
      const group = svgElement('g', {transform: `translate(${position.x}, ${position.y})`, class: `graph-node${active ? ' is-selected' : ''}${focused && !focused.has(node.id) ? ' is-muted' : ''}`, tabindex: 0, role: 'button', 'aria-label': `${node.label}. ${layers.get(node.layer).label}. ${linksFor(node.id).length} connections.`, 'aria-pressed': active, 'data-node': node.id});
      group.append(svgElement('title', {}, node.label + ' · ' + layers.get(node.layer).label));
      group.append(svgElement('rect', {x: -width / 2, y: -33, width, height: 66, rx: 6}));
      group.append(svgElement('line', {x1: -width / 2 + 1, x2: -width / 2 + 1, y1: -24, y2: 24, stroke: state.layout === 'flat' ? '#86968b' : colours[node.layer], class: 'node-rule'}));
      const lines = wrapLabel(node.label, state.layout === 'flat' ? 18 : 21);
      for (const [index, line] of lines.entries()) group.append(svgElement('text', {x: 0, y: -4 - (lines.length - 1) * 8 + index * 17, 'text-anchor': 'middle', class: 'node-label'}, line));
      group.append(svgElement('text', {x: 0, y: 23, 'text-anchor': 'middle', class: 'node-detail'}, linksFor(node.id).length + ' connections'));
      group.addEventListener('click', () => selectNode(node.id));
      group.addEventListener('keydown', event => keyboardClick(event, () => selectNode(node.id)));
      svg.append(group);
    }
    if (!model.nodes.length) svg.append(svgElement('text', {x: 450, y: 350, 'text-anchor': 'middle', class: 'empty-message'}, 'No records match these filters.'));
  }

  function renderIndex(model) {
    const index = document.getElementById('node-index');
    index.replaceChildren();
    for (const node of model.nodes) {
      const card = element('button', 'index-card' + (state.node === node.id && !state.edge ? ' is-selected' : ''));
      card.dataset.cardNode = node.id;
      card.style.setProperty('--layer-color', colours[node.layer]);
      card.setAttribute('aria-pressed', String(state.node === node.id && !state.edge));
      card.append(element('span', 'card-layer', layers.get(node.layer).label), element('strong', '', node.label), element('span', 'card-count', linksFor(node.id).length + ' connections · ' + node.crossLayerDegree + ' across layers'));
      card.addEventListener('click', () => selectNode(node.id));
      index.append(card);
    }
    if (!model.nodes.length) index.append(element('p', 'inspection-copy', 'No records match these filters. Use Show whole model to reset.'));
  }

  function sourceLink(text, path) {
    const link = element('a', 'read-source', text);
    link.href = '../' + path;
    return link;
  }

  function renderInspector() {
    inspector.replaceChildren();
    if (state.edge) {
      const edge = edges.get(state.edge);
      inspector.append(element('p', 'eyebrow', edge.label), element('h2', '', nodes.get(edge.source).label + ' → ' + nodes.get(edge.target).label), element('p', 'inspection-copy', 'This arrow preserves the notebook’s source and target order. Its project meaning is undocumented.'));
      const records = data.edgeRecords.filter(record => record.edgeId === edge.id);
      if (edge.weight === null) inspector.append(element('p', 'weight-notice', 'Two recorded weights, 0.7 and 0.9, remain unresolved. Both records are retained in the Python graph.'));
      inspector.append(element('h3', '', records.length === 1 ? 'Recorded weight' : 'Recorded weights'));
      for (const record of records) {
        const row = element('div', 'source-row');
        row.append(element('strong', '', String(record.weight)), element('p', '', record.sourceRows.join(' · ')));
        inspector.append(row);
      }
      inspector.append(element('p', 'inspection-copy', 'Units and scale were not specified. These values are available for inspection and are excluded from the displayed connection counts.'));
      const relation = element('div', 'source-row');
      relation.append(element('p', '', 'Original source names'), element('code', '', nodes.get(edge.source).sourceName + ' → ' + nodes.get(edge.target).sourceName));
      inspector.append(relation);
      inspector.append(element('h3', '', 'Original rows'));
      inspector.append(element('p', 'inspection-copy', edge.sourceRows.join(' · ')));
      inspector.append(sourceLink('Inspect the original row data ↗', 'data/original-extract.json'));
      const endpoints = element('div', 'neighbour-list');
      for (const id of [edge.source, edge.target]) {
        const button = element('button', '', 'Open ' + nodes.get(id).label);
        button.addEventListener('click', () => selectNode(id));
        endpoints.append(button);
      }
      inspector.append(element('h3', '', 'Follow a record'), endpoints);
      return;
    }
    if (!state.node) {
      inspector.append(element('p', 'eyebrow', 'Whole model'), element('h2', '', 'Three kinds of record'), element('p', 'inspection-copy', data.meta.scopeNote));
      inspector.append(element('p', 'guide-question', 'Which boundary matters for your question?'), element('p', 'guide-copy', 'Choose a record to see its incoming and outgoing links. Switch to one plane to compare the same connections without layer grouping.'));
      inspector.append(element('h3', '', 'A definition to keep in view'), element('p', 'inspection-copy', data.meta.nodeIdentity));
      return;
    }
    const node = nodes.get(state.node);
    const adjacent = linksFor(node.id);
    inspector.append(element('p', 'eyebrow', layers.get(node.layer).label), element('h2', '', node.label), element('p', 'inspection-copy', node.summary));
    const guide = guides.find(item => item.id === state.guide);
    if (guide) inspector.append(element('p', 'guide-question', guide.question), element('p', 'guide-copy', guide.text));
    const metrics = element('div', 'node-metrics');
    for (const [number, label] of [[adjacent.length, 'connections'], [adjacent.filter(edge => nodes.get(edge.source).layer !== nodes.get(edge.target).layer).length, 'across layers']]) {
      const item = element('div');
      item.append(element('strong', '', number), element('span', '', label));
      metrics.append(item);
    }
    inspector.append(metrics);
    for (const [direction, description] of [['outgoing', 'Recorded from this record'], ['incoming', 'Recorded towards this record']]) {
      const matches = adjacent.filter(edge => (direction === 'outgoing' ? edge.source : edge.target) === node.id);
      if (!matches.length) continue;
      inspector.append(element('h3', '', description));
      const list = element('div', 'neighbour-list');
      for (const edge of matches) {
        const other = nodes.get(direction === 'outgoing' ? edge.target : edge.source);
        const button = element('button');
        button.dataset.inspectEdge = edge.id;
        const text = element('span', '', other.label);
        text.append(element('small', '', layers.get(other.layer).label + (edge.weight === null ? ' · unresolved weights' : '')));
        button.append(text, element('span', 'link-direction', direction === 'outgoing' ? '→' : '←'));
        button.setAttribute('aria-label', 'Inspect ' + nodes.get(edge.source).label + ' to ' + nodes.get(edge.target).label);
        button.addEventListener('click', () => selectEdge(edge.id));
        list.append(button);
      }
      inspector.append(list);
    }
    const source = element('details');
    source.append(element('summary', '', 'Original name and source'));
    source.append(element('p', 'source-id', node.sourceName));
    if (node.originalNames.length > 1) source.append(element('p', 'inspection-copy', 'Original names brought together here: ' + node.originalNames.join(', ') + '.'));
    const rowIds = [...new Set(adjacent.flatMap(edge => edge.sourceRows))];
    source.append(element('p', 'inspection-copy', rowIds.join(' · ')), sourceLink('Read all original rows ↗', 'data/original-extract.json'));
    inspector.append(source);
  }

  function render() {
    const active = document.activeElement;
    const focusAttribute = ['data-node', 'data-edge-control', 'data-card-node', 'data-inspect-edge'].find(attribute => active.hasAttribute(attribute));
    const focusId = focusAttribute ? active.getAttribute(focusAttribute) : null;
    const model = visibleModel();
    renderGraph(model);
    renderIndex(model);
    renderInspector();
    document.getElementById('visible-count').textContent = `${model.nodes.length} of ${data.nodes.length} records · ${model.edges.length} of ${data.edges.length} connections`;
    document.getElementById('layout-caption').textContent = state.neighbourhood ? 'Adjacent records in either direction. The recorded arrows remain visible.' : state.layout === 'layered' ? 'Each record belongs to one layer. Links can stay within a layer or cross its boundary.' : 'The same records and directed links, placed in one plane. Select a record to recover its layer.';
    for (const button of document.querySelectorAll('[data-layout]')) button.setAttribute('aria-pressed', String(button.dataset.layout === state.layout));
    for (const button of document.querySelectorAll('[data-guide]')) button.setAttribute('aria-pressed', String(button.dataset.guide === state.guide));
    for (const button of document.querySelectorAll('[data-tab]')) button.setAttribute('aria-selected', String(button.dataset.tab === state.tab));
    document.getElementById('graph-view').hidden = state.tab !== 'graph';
    document.getElementById('index-view').hidden = state.tab !== 'index';
    const neighbourhood = document.getElementById('neighbourhood');
    neighbourhood.setAttribute('aria-pressed', String(state.neighbourhood));
    neighbourhood.disabled = !state.node || Boolean(state.edge);
    neighbourhood.textContent = state.neighbourhood ? 'Show wider model' : 'Only connected records';
    neighbourhood.title = 'Show records adjacent in either direction. Recorded arrows are preserved.';
    if (focusAttribute) {
      const replacement = [...document.querySelectorAll('[' + focusAttribute + ']')].find(node => node.getAttribute(focusAttribute) === focusId);
      if (replacement) replacement.focus({preventScroll: true});
    }
  }

  function renderMethod() {
    const statistics = document.getElementById('model-statistics');
    for (const [value, label] of [[data.nodes.length, 'records in three layers'], [data.edges.length, 'distinct connections'], [data.edgeRecords.length, 'weighted edge records']]) {
      const stat = element('div', 'stat');
      stat.append(element('strong', '', value), element('span', '', label));
      statistics.append(stat);
    }
    const corrections = document.getElementById('corrections');
    for (const correction of data.corrections) {
      corrections.append(element('h3', '', correction.title), element('p', '', correction.detail));
      if (correction.sourceRows) corrections.append(element('p', 'source-id', correction.sourceRows.join(' · ')));
    }
    const results = document.getElementById('run-results');
    results.append(element('p', '', `The reconstruction ran with Python ${run.python} and py3plex ${run.packages.py3plex} on ${run.verifiedDate}.`));
    const table = element('table', 'data-table');
    const body = element('tbody');
    const rows = [
      ['Runtime graph', run.runtimeGraphClass + ' · recorded direction preserved'],
      ['Original reconstruction', run.originalReconstruction.nodeCount + ' nodes · ' + run.originalReconstruction.edgeCount + ' edge records'],
      ['Curated reconstruction', run.nodeCount + ' nodes · ' + run.edgeCount + ' edge records'],
      ['Display', run.displayConnectionCount + ' connections · parallel weights inspectable'],
      ['Automatic coupling links', String(run.automaticCouplingEdges)],
      ['Source comparison', run.sourceNodeAndEdgeSetsVerified ? 'Node and edge sets verified by the run' : 'Verification pending']
    ];
    for (const [name, value] of rows) {
      const row = element('tr');
      row.append(element('th', '', name), element('td', '', value));
      body.append(row);
    }
    table.append(body);
    results.append(table, sourceLink('Read the runtime receipt ↗', 'outputs/runtime-receipt.json'));
    const schema = document.getElementById('schema-details');
    schema.append(element('h3', '', 'Inspectable structure'), element('p', '', 'Nodes contain an ID, original name and one layer. Display links contain source, target, direction, a layer-based relation label and original row references. Separate edge records retain distinct source weights.'));
    schema.append(element('p', '', data.metrics.analysisPolicy));
    const sources = document.getElementById('sources');
    const list = element('ul');
    for (const source of data.sources) {
      const item = element('li');
      item.append(sourceLink(source.title, source.path));
      list.append(item);
    }
    sources.append(list);
  }

  function download(filename, content, mimeType) {
    const url = URL.createObjectURL(new Blob([content], {type: mimeType}));
    const link = element('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  for (const layer of data.layers) {
    const option = element('option', '', layer.label);
    option.value = layer.id;
    document.getElementById('layer-filter').append(option);
  }
  for (const relation of data.relationTypes) {
    const option = element('option', '', relation.label);
    option.value = relation.id;
    document.getElementById('relation-filter').append(option);
  }
  for (const guide of guides) {
    const button = element('button', '', guide.label);
    button.dataset.guide = guide.id;
    button.setAttribute('aria-pressed', String(guide.id === state.guide));
    button.addEventListener('click', () => {
      state.layer = 'all';
      state.relation = 'all';
      state.search = '';
      state.neighbourhood = false;
      document.getElementById('search').value = '';
      document.getElementById('layer-filter').value = 'all';
      document.getElementById('relation-filter').value = 'all';
      selectNode(guide.node, guide.id);
    });
    document.getElementById('guides').append(button);
  }
  function changeFilter(key, value) {
    Object.assign(state, {node: null, edge: null, guide: null, neighbourhood: false, [key]: value});
    updateHash('', '');
    render();
  }
  document.getElementById('search').addEventListener('input', event => changeFilter('search', event.target.value));
  document.getElementById('layer-filter').addEventListener('change', event => changeFilter('layer', event.target.value));
  document.getElementById('relation-filter').addEventListener('change', event => changeFilter('relation', event.target.value));
  document.getElementById('neighbourhood').addEventListener('click', () => {state.neighbourhood = !state.neighbourhood; render();});
  document.getElementById('reset').addEventListener('click', () => {
    Object.assign(state, {node: null, edge: null, guide: null, layer: 'all', relation: 'all', search: '', neighbourhood: false});
    document.getElementById('search').value = '';
    document.getElementById('layer-filter').value = 'all';
    document.getElementById('relation-filter').value = 'all';
    updateHash('', '');
    render();
  });
  for (const button of document.querySelectorAll('[data-layout]')) button.addEventListener('click', () => {state.layout = button.dataset.layout; state.tab = 'graph'; render();});
  for (const button of document.querySelectorAll('[data-tab]')) button.addEventListener('click', () => {state.tab = button.dataset.tab; render();});
  document.getElementById('download-data').addEventListener('click', () => download('railway-three-layers.json', JSON.stringify(data, null, 2), 'application/json'));
  document.getElementById('download-svg').addEventListener('click', () => {
    const copy = svg.cloneNode(true);
    const styled = [...copy.querySelectorAll('*')];
    const originals = [...svg.querySelectorAll('*')];
    const properties = ['fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'opacity', 'font-family', 'font-size', 'font-weight'];
    for (const [index, node] of styled.entries()) {
      const computed = getComputedStyle(originals[index]);
      for (const property of properties) node.style.setProperty(property, computed.getPropertyValue(property));
    }
    copy.setAttribute('xmlns', namespace);
    download('railway-' + state.layout + '.svg', new XMLSerializer().serializeToString(copy), 'image/svg+xml');
  });
  const hash = new URLSearchParams(location.hash.slice(1));
  if (hash.has('node') && nodes.has(hash.get('node'))) Object.assign(state, {node: hash.get('node'), guide: null});
  if (hash.has('edge') && edges.has(hash.get('edge'))) Object.assign(state, {edge: hash.get('edge'), guide: null});
  if (hash.has('guide')) {
    const guide = guides.find(item => item.id === hash.get('guide'));
    if (guide) Object.assign(state, {node: guide.node, guide: guide.id});
  }
  renderMethod();
  render();
})();
