const express = require('express');
const app = express();
const PORT = 8080;

app.get('/', (req, res) => {
    res.send('API is running and connected to Apache!');
});

function calcMoyenne() {

    function getInput(name) {
        return parseFloat(form.elements[name].value)
    }

    bda = getInput("bda_exam") * 0.6 + ((getInput("bda_td") + getInput("bda_td")) / 2) * 0.4;
    ra = getInput("ra_exam") * 0.6 + ((getInput("ra_td") + getInput("ra_td")) / 2) * 0.4;
    aa = getInput("aa_exam") * 0.6 + getInput("aa_tp") * 0.4;
    tai = getInput("tai_exam") * 0.6 + getInput("tai_tp") * 0.4;
    pasd = getInput("pasd_exam") * 0.6 + getInput("pasd_tp") * 0.4;
    ccbd = getInput("ccbd_exam") * 0.6 + getInput("ccbd_tp") * 0.4;

    sum = bda * 3 + ra * 3 + aa * 3 + tai * 3 + pasd * 2 + ccbd * 2 + getInput("sw_exam");
    return sum / 17;
}

app.get('/calcMoyenne', (req, res) => {

    res.json({ status: 'success', message: 'Backend is reachable' });
});

app.listen(PORT, () => {
    console.log(`Backend server running on http://localhost:${PORT}`);
});
