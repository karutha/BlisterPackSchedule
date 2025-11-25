const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const db = require('./database');

const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'public')));

// Helper to calculate next schedule (28 days cycle)
const calculateNextSchedule = (billingDate) => {
    const date = new Date(billingDate);
    date.setDate(date.getDate() + 28);
    return date.toISOString().split('T')[0];
};

// GET all patients
app.get('/api/patients', (req, res) => {
    const sql = "SELECT * FROM patients ORDER BY next_schedule_date ASC";
    db.all(sql, [], (err, rows) => {
        if (err) {
            res.status(400).json({ "error": err.message });
            return;
        }
        res.json({
            "message": "success",
            "data": rows
        });
    });
});

// POST new patient
app.post('/api/patients', (req, res) => {
    const { name, billing_date } = req.body;
    if (!name || !billing_date) {
        res.status(400).json({ "error": "Name and billing_date are required" });
        return;
    }

    const next_schedule_date = calculateNextSchedule(billing_date);

    const sql = 'INSERT INTO patients (name, billing_date, next_schedule_date) VALUES (?,?,?)';
    const params = [name, billing_date, next_schedule_date];
    db.run(sql, params, function (err) {
        if (err) {
            res.status(400).json({ "error": err.message });
            return;
        }
        res.json({
            "message": "success",
            "data": {
                id: this.lastID,
                name,
                billing_date,
                next_schedule_date
            }
        });
    });
});

// GET alerts (patients due for billing today or past due)
app.get('/api/alerts', (req, res) => {
    const today = new Date().toISOString().split('T')[0];
    const sql = "SELECT * FROM patients WHERE billing_date <= ? ORDER BY billing_date ASC";
    db.all(sql, [today], (err, rows) => {
        if (err) {
            res.status(400).json({ "error": err.message });
            return;
        }
        res.json({
            "message": "success",
            "data": rows
        });
    });
});

// POST update schedule (move to next cycle)
app.post('/api/patients/:id/cycle', (req, res) => {
    const { id } = req.params;
    const { current_billing_date } = req.body; // Optional: verify current date

    // Logic: Update billing_date to next_schedule_date, and calculate new next_schedule_date
    // First get the patient
    db.get("SELECT * FROM patients WHERE id = ?", [id], (err, row) => {
        if (err) {
            res.status(400).json({ "error": err.message });
            return;
        }
        if (!row) {
            res.status(404).json({ "error": "Patient not found" });
            return;
        }

        const new_billing_date = row.next_schedule_date;
        const new_next_schedule_date = calculateNextSchedule(new_billing_date);

        const updateSql = "UPDATE patients SET billing_date = ?, next_schedule_date = ? WHERE id = ?";
        db.run(updateSql, [new_billing_date, new_next_schedule_date, id], function (err) {
            if (err) {
                res.status(400).json({ "error": err.message });
                return;
            }
            res.json({
                "message": "success",
                "data": {
                    id,
                    billing_date: new_billing_date,
                    next_schedule_date: new_next_schedule_date
                }
            });
        });
    });
});


// The "catchall" handler: for any request that doesn't
// match one above, send back React's index.html file.
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
