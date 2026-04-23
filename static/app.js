// ── State ────────────────────────────────────────────────────────────────────
let allRecords = [];

// ── Upload ───────────────────────────────────────────────────────────────────
const dropZone  = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); }
});

dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

async function handleFile(file) {
  setLoading(true);
  const form = new FormData();
  form.append('file', file);
  try {
    const res = await fetch('/upload', { method: 'POST', body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Upload failed');
    populateReviewForm(data);
    openModal('review-modal');
  } catch (err) {
    showError('Upload error: ' + err.message);
  } finally {
    setLoading(false);
    fileInput.value = '';
  }
}

function setLoading(on) {
  document.getElementById('upload-idle').classList.toggle('hidden', on);
  document.getElementById('upload-loading').classList.toggle('hidden', !on);
  dropZone.setAttribute('aria-busy', on ? 'true' : 'false');
}

// ── Review Modal ─────────────────────────────────────────────────────────────
function populateReviewForm(data) {
  setVal('f-doc-type',       data.doc_type       || 'Other');
  setVal('f-doc-date',       data.doc_date        || '');
  setVal('f-reference-no',   data.reference_no    || '');
  setVal('f-sender',         data.sender          || '');
  setVal('f-subject',        data.subject         || '');
  setVal('f-summary',        data.summary         || '');
  setVal('f-file-path',      data.file_path       || '');
  setVal('f-original-filename', data.original_filename || '');
}

async function saveRecord() {
  const payload = {
    doc_type:          getVal('f-doc-type'),
    doc_date:          getVal('f-doc-date'),
    reference_no:      getVal('f-reference-no'),
    sender:            getVal('f-sender'),
    subject:           getVal('f-subject'),
    summary:           getVal('f-summary'),
    file_path:         getVal('f-file-path'),
    original_filename: getVal('f-original-filename'),
  };
  const res = await fetch('/records', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) { showError('Failed to save record'); return; }
  closeModal('review-modal');
  await loadRecords();
}

// ── Edit Modal ───────────────────────────────────────────────────────────────
function openEditModal(record) {
  setVal('e-id',          record.id);
  setVal('e-doc-type',    record.doc_type    || 'Other');
  setVal('e-doc-date',    record.doc_date    || '');
  setVal('e-reference-no',record.reference_no|| '');
  setVal('e-sender',      record.sender      || '');
  setVal('e-subject',     record.subject     || '');
  setVal('e-summary',     record.summary     || '');
  openModal('edit-modal');
}

async function updateRecord() {
  const id = getVal('e-id');
  const payload = {
    doc_type:     getVal('e-doc-type'),
    doc_date:     getVal('e-doc-date'),
    reference_no: getVal('e-reference-no'),
    sender:       getVal('e-sender'),
    subject:      getVal('e-subject'),
    summary:      getVal('e-summary'),
  };
  const res = await fetch(`/records/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) { showError('Failed to update record'); return; }
  closeModal('edit-modal');
  await loadRecords();
}

// ── Detail Modal ─────────────────────────────────────────────────────────────
function openDetailModal(record) {
  document.getElementById('detail-control-no').textContent = record.control_no || 'Record Details';
  document.getElementById('detail-content').innerHTML = `
    <dl class="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
      <div>
        <dt class="text-xs text-gray-400 font-semibold uppercase tracking-wide">Control No</dt>
        <dd class="font-bold text-blue-800 font-mono">${esc(record.control_no)}</dd>
      </div>
      <div>
        <dt class="text-xs text-gray-400 font-semibold uppercase tracking-wide">Document Type</dt>
        <dd>${badge(record.doc_type)}</dd>
      </div>
      <div>
        <dt class="text-xs text-gray-400 font-semibold uppercase tracking-wide">Document Date</dt>
        <dd>${esc(record.doc_date) || '&mdash;'}</dd>
      </div>
      <div>
        <dt class="text-xs text-gray-400 font-semibold uppercase tracking-wide">Reference No</dt>
        <dd class="font-mono">${esc(record.reference_no) || '&mdash;'}</dd>
      </div>
      <div class="col-span-2">
        <dt class="text-xs text-gray-400 font-semibold uppercase tracking-wide">Sender</dt>
        <dd>${esc(record.sender) || '&mdash;'}</dd>
      </div>
      <div class="col-span-2">
        <dt class="text-xs text-gray-400 font-semibold uppercase tracking-wide">Subject</dt>
        <dd class="font-semibold">${esc(record.subject) || '&mdash;'}</dd>
      </div>
      <div class="col-span-2">
        <dt class="text-xs text-gray-400 font-semibold uppercase tracking-wide">Summary</dt>
        <dd class="text-gray-600 leading-relaxed">${esc(record.summary) || '&mdash;'}</dd>
      </div>
      <div class="col-span-2 pt-3 border-t border-gray-100">
        <dt class="text-xs text-gray-400 font-semibold uppercase tracking-wide">Original File</dt>
        <dd class="text-xs">${record.file_path
          ? `<a href="/${record.file_path.replace(/\\/g,'/')}" target="_blank" class="text-blue-600 hover:underline">${esc(record.original_filename)}</a>`
          : esc(record.original_filename) || '&mdash;'}</dd>
      </div>
      <div class="col-span-2">
        <dt class="text-xs text-gray-400 font-semibold uppercase tracking-wide">Logged At</dt>
        <dd class="text-gray-400 text-xs">${record.uploaded_at ? record.uploaded_at.slice(0,19).replace('T',' ') : '&mdash;'}</dd>
      </div>
    </dl>
    <div class="mt-5 flex justify-end gap-2">
      <button onclick="closeModal('detail-modal'); openEditModal(${JSON.stringify(record).replace(/"/g,'&quot;')})"
              class="px-4 py-2 rounded-lg bg-gray-100 text-sm text-gray-700 hover:bg-gray-200">Edit</button>
      <button onclick="closeModal('detail-modal')"
              class="px-4 py-2 rounded-lg bg-blue-800 text-white text-sm hover:bg-blue-700">Close</button>
    </div>
  `;
  openModal('detail-modal');
}

// ── Records Table ─────────────────────────────────────────────────────────────
async function loadRecords() {
  const res = await fetch('/records');
  allRecords = await res.json();
  filterRecords();
}

function filterRecords() {
  const q    = document.getElementById('search-input').value.toLowerCase().trim();
  const type = document.getElementById('type-filter').value;

  const filtered = allRecords.filter(r => {
    const matchType = !type || r.doc_type === type;
    const matchQ    = !q || [r.control_no, r.doc_type, r.sender, r.subject, r.reference_no, r.summary]
      .some(v => (v || '').toLowerCase().includes(q));
    return matchType && matchQ;
  });

  document.getElementById('record-count').textContent =
    `${filtered.length} record${filtered.length !== 1 ? 's' : ''}`;

  renderTable(filtered);
}

function renderTable(records) {
  const tbody = document.getElementById('records-tbody');
  if (!records.length) {
    tbody.innerHTML = `<tr>
      <td colspan="8" class="text-center py-12 text-gray-400">No records found.</td>
    </tr>`;
    return;
  }

  tbody.innerHTML = records.map((r, i) => `
    <tr class="${i % 2 === 0 ? 'bg-white' : 'bg-blue-50'} hover:bg-yellow-50 transition-colors">
      <td class="px-3 py-2 font-mono text-xs text-blue-800 whitespace-nowrap">${esc(r.control_no)}</td>
      <td class="px-3 py-2 whitespace-nowrap">${badge(r.doc_type)}</td>
      <td class="px-3 py-2 text-gray-600 whitespace-nowrap">${esc(r.doc_date) || '&mdash;'}</td>
      <td class="px-3 py-2 text-gray-500 text-xs whitespace-nowrap">${esc(r.reference_no) || '&mdash;'}</td>
      <td class="px-3 py-2 max-w-[160px] truncate" title="${esc(r.sender)}">${esc(r.sender) || '&mdash;'}</td>
      <td class="px-3 py-2 max-w-[220px] truncate font-medium" title="${esc(r.subject)}">${esc(r.subject) || '&mdash;'}</td>
      <td class="px-3 py-2 text-gray-400 text-xs whitespace-nowrap">${r.uploaded_at ? r.uploaded_at.slice(0,10) : '&mdash;'}</td>
      <td class="px-3 py-2 whitespace-nowrap">
        <div class="flex gap-1">
          <button onclick='openDetailModal(${safeJson(r)})'
                  class="px-2 py-1 text-xs rounded-md bg-blue-100 text-blue-700 hover:bg-blue-200 font-medium">View</button>
          <button onclick='openEditModal(${safeJson(r)})'
                  class="px-2 py-1 text-xs rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium">Edit</button>
          ${r.file_path ? `<a href="/${r.file_path.replace(/\\\\/g,'/')}" target="_blank"
                  class="px-2 py-1 text-xs rounded-md bg-green-100 text-green-700 hover:bg-green-200 font-medium">File</a>` : ''}
          <button onclick="deleteRecord(${r.id})"
                  class="px-2 py-1 text-xs rounded-md bg-red-100 text-red-700 hover:bg-red-200 font-medium">Del</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function deleteRecord(id) {
  openModal('confirm-modal');
  document.getElementById('confirm-ok').onclick = async () => {
    closeModal('confirm-modal');
    await fetch(`/records/${id}`, { method: 'DELETE' });
    await loadRecords();
  };
}

// ── Export ────────────────────────────────────────────────────────────────────
function exportRecords(format) {
  window.location.href = `/export/${format}`;
}

// ── Utilities ─────────────────────────────────────────────────────────────────
const TYPE_COLORS = {
  Memo:        'bg-blue-100 text-blue-800',
  Letter:      'bg-purple-100 text-purple-800',
  Invitation:  'bg-pink-100 text-pink-800',
  Circular:    'bg-yellow-100 text-yellow-800',
  Endorsement: 'bg-orange-100 text-orange-800',
  Other:       'bg-gray-100 text-gray-600',
};

function badge(type) {
  const cls = TYPE_COLORS[type] || TYPE_COLORS.Other;
  return `<span class="px-2 py-0.5 rounded-full text-xs font-semibold ${cls}">${esc(type) || 'Other'}</span>`;
}

function esc(s) {
  return String(s || '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function safeJson(obj) {
  return JSON.stringify(obj).replace(/</g,'\\u003c').replace(/>/g,'\\u003e').replace(/&/g,'\\u0026');
}

function getVal(id) { return document.getElementById(id).value; }
function setVal(id, v) {
  const el = document.getElementById(id);
  if (el) el.value = v;
}

let _lastFocused = null;

function openModal(id) {
  _lastFocused = document.activeElement;
  const modal = document.getElementById(id);
  modal.classList.remove('hidden');
  const first = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
  if (first) first.focus();
  modal.addEventListener('keydown', _trapFocus);
}

function closeModal(id) {
  const modal = document.getElementById(id);
  modal.classList.add('hidden');
  modal.removeEventListener('keydown', _trapFocus);
  if (_lastFocused) _lastFocused.focus();
}

function _trapFocus(e) {
  if (e.key !== 'Tab') return;
  const focusable = Array.from(this.querySelectorAll(
    'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  )).filter(el => !el.closest('.hidden'));
  if (!focusable.length) return;
  const first = focusable[0], last = focusable[focusable.length - 1];
  if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
}

function showError(msg) {
  const banner = document.getElementById('error-banner');
  document.getElementById('error-banner-msg').textContent = msg;
  banner.classList.remove('hidden');
  setTimeout(() => banner.classList.add('hidden'), 6000);
}

// ── Init ──────────────────────────────────────────────────────────────────────
loadRecords();
