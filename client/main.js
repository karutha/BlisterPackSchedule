const API_URL = '/api';

const addPatientForm = document.getElementById('add-patient-form');
const patientList = document.getElementById('patient-list');
const alertsSection = document.getElementById('alerts-section');
const alertsList = document.getElementById('alerts-list');

const patientSelect = document.getElementById('patient-select');
const newPatientInput = document.getElementById('new-patient-name');

// Fetch and render data
async function loadData() {
    try {
        const [patientsRes, alertsRes] = await Promise.all([
            fetch(`${API_URL}/patients`),
            fetch(`${API_URL}/alerts`)
        ]);

        const patientsData = await patientsRes.json();
        const alertsData = await alertsRes.json();

        renderPatients(patientsData.data);
        renderPatientSelect(patientsData.data);
        renderAlerts(alertsData.data);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function renderPatients(patients) {
    patientList.innerHTML = patients.map(patient => `
    <div class="list-item">
      <div class="patient-info">
        <h3>${patient.name}</h3>
        <div class="patient-meta">
          <div class="meta-item">Billing: <span>${patient.billing_date}</span></div>
          <div class="meta-item">Next Schedule: <span>${patient.next_schedule_date}</span></div>
        </div>
      </div>
    </div>
  `).join('');
}

function renderPatientSelect(patients) {
    // Get unique patient names
    const uniqueNames = [...new Set(patients.map(p => p.name))].sort();

    // Save current selection if any
    const currentSelection = patientSelect.value;

    // Reset options but keep the first two (default and new)
    patientSelect.innerHTML = `
        <option value="" disabled selected>Select a patient</option>
        <option value="new">+ Add New Patient</option>
        ${uniqueNames.map(name => `<option value="${name}">${name}</option>`).join('')}
    `;

    // Restore selection if it wasn't "new" or empty
    if (currentSelection && currentSelection !== 'new') {
        patientSelect.value = currentSelection;
    }
}

function renderAlerts(alerts) {
    if (alerts.length === 0) {
        alertsSection.classList.add('hidden');
        return;
    }

    alertsSection.classList.remove('hidden');
    alertsList.innerHTML = alerts.map(patient => `
    <div class="alert-card">
      <div class="alert-info">
        <strong>${patient.name}</strong> is due for billing today (${patient.billing_date}).
      </div>
      <button class="btn-cycle" onclick="cyclePatient(${patient.id})">Start Next Cycle</button>
    </div>
  `).join('');
}

// Handle Patient Selection Change
patientSelect.addEventListener('change', (e) => {
    if (e.target.value === 'new') {
        newPatientInput.classList.remove('hidden');
        newPatientInput.required = true;
        newPatientInput.focus();
    } else {
        newPatientInput.classList.add('hidden');
        newPatientInput.required = false;
        newPatientInput.value = '';
    }
});

// Add Patient
addPatientForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    let name;
    if (patientSelect.value === 'new') {
        name = newPatientInput.value.trim();
    } else {
        name = patientSelect.value;
    }

    if (!name) {
        alert('Please select or enter a patient name');
        return;
    }

    const billing_date = document.getElementById('billing-date').value;

    try {
        const res = await fetch(`${API_URL}/patients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, billing_date })
        });

        if (res.ok) {
            addPatientForm.reset();
            newPatientInput.classList.add('hidden');
            loadData();
        }
    } catch (error) {
        console.error('Error adding patient:', error);
    }
});

// Cycle Patient (Global function to be accessible from HTML onclick)
window.cyclePatient = async (id) => {
    try {
        const res = await fetch(`${API_URL}/patients/${id}/cycle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });

        if (res.ok) {
            loadData();
        }
    } catch (error) {
        console.error('Error cycling patient:', error);
    }
};

// Initial Load
loadData();
