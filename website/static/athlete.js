console.log(athleteData);

const statSelect = document.getElementById("statSelect");
const athleteSelect = document.getElementById("athleteSelect");
const teamSelect = document.getElementById("teamSelect");

let selectedAthleteData = [];

function loadStatOptions(data) {
    const ignoreKeys = ["id", "athlete_id", "athlete_name", "athlete_teams", "athlete_groups", "athlete_active", "testType_id", "testType_name", "testType_canonicalId", "tag_ids", "tag_names", "segment", "active", "timestamp"];
    let statKeys = Object.keys(data[0]).filter(key => !ignoreKeys.includes(key));
    //ingnore any key that starts with external
    statKeys = statKeys.filter(key => !key.startsWith("external"));
    statSelect.innerHTML = '<option value="">Select Stat</option>';
    statKeys.forEach(stat => {
        const option = document.createElement("option");
        option.value = stat;
        option.textContent = stat;
        statSelect.appendChild(option);
    });
}

const startDate = document.getElementById("startDate");
const endDate = document.getElementById("endDate");

// Set the default start and end dates to the first and last test dates

function getMinMaxTimestamp() {
    const firstTestDate = new Date(selectedAthleteData[selectedAthleteData.length - 1].timestamp * 1000).toISOString().split("T")[0];
    const lastTestDate = new Date(selectedAthleteData[0].timestamp * 1000).toISOString().split("T")[0];
    startDate.value = lastTestDate;
    endDate.value = firstTestDate;
}

// Set up Chart.js
const ctx = document.getElementById("statChart").getContext("2d");
const statChart = new Chart(ctx, {
    type: "scatter",
    data: {
        datasets: [{
            label: "Stat over Time",
            data: [],
            borderColor: "blue",
            backgroundColor: "rgba(0,0,255,0.1)"
        }]
    },
    options: {
        scales: {
            x: {
                type: "time",
                time: {
                    unit: "day"
                },
                title: {
                    display: true,
                    text: "Time"
                }
            },
            y: {
                title: {
                    display: true,
                    text: "Stat Value"
                }
            }
        }
    }
});


if (userType !== "athlete") {
    // Populate the team dropdown on page load
    if (userType !== "coach") {
        const teamDropdown = document.getElementById("teamSelect");
        for (const [key, value] of Object.entries(athleteData)) {
            const option = document.createElement("option");
            option.value = key;
            option.textContent = key;
            teamDropdown.appendChild(option);
        }

        // Event handler when team is selected
        teamDropdown.addEventListener("change", () => {
            const team = teamDropdown.value;
            athleteSelect.innerHTML = '<option value="">Select Athlete</option>';
            athleteSelect.value = "";
            statSelect.value = "";
            clearChart();
            if (team) {
                for (const athlete of athleteData[team]) {
                    const option = document.createElement("option");
                    option.textContent = athlete;
                    athleteSelect.appendChild(option);
                }
            }
        });
    } else {
        //add an option to view the entire team
        const option = document.createElement("option");
        option.textContent = "All Athletes";
        athleteSelect.appendChild(option);

        // Populate the athlete dropdown on page load
        for (const athlete of athleteData) {
            //check if an option already exists
            if (!athleteSelect.innerHTML.includes(athlete)) {
                const option = document.createElement("option");
                option.textContent = athlete;
                athleteSelect.appendChild(option);
            }
        }
    }

    athleteSelect.addEventListener("change", () => {
        let athlete = athleteSelect.value;
        statSelect.value = "";
        clearChart();
        athlete = athlete.replace(/ /g, "-");
        fetch(`/get_athlete_data/${athlete}`)
            .then(response => response.json())
            .then(data => {
                selectedAthleteData = data;
                loadStatOptions(data);
                getMinMaxTimestamp();
                updateChart("null");
                getMinMaxTimestamp();
            });
    });
} else {
    selectedAthleteData = athleteData;
    loadStatOptions(athleteData);
    getMinMaxTimestamp();
    updateChart("null");
    getMinMaxTimestamp();
}

// Function to calculate polynomial regression
function polynomialRegression(x, y, order) {
    // Create the X matrix
    const xMatrix = [];
    for (let i = 0; i < x.length; i++) {
        const row = [];
        for (let j = 0; j <= order; j++) {
            row.push(Math.pow(x[i], j));
        }
        xMatrix.push(row);
    }

    // Convert arrays to math.js matrices
    const X = math.matrix(xMatrix);
    const Y = math.matrix(y.map(v => [v]));

    // Compute (Xt * X)⁻¹ * Xt * Y to get the coefficients
    const Xt = math.transpose(X);
    const XtX = math.multiply(Xt, X);
    const XtX_inv = math.inv(XtX);
    const XtY = math.multiply(Xt, Y);
    const coefficients = math.multiply(XtX_inv, XtY);

    // Convert to an array for easier access
    const coefficientsArray = coefficients.toArray();

    // Create a predict function based on the calculated coefficients
    return {
        predict: (xVal) => {
            let yVal = 0;
            for (let i = 0; i < coefficientsArray.length; i++) {
                yVal += coefficientsArray[i][0] * Math.pow(xVal, i);
            }
            return yVal;
        }
    };
}

function generatePolynomialRegression(data, order, minTimestamp, maxTimestamp) {
    const x = data.map(point => point.x);
    const y = data.map(point => point.y);

    // Calculate the polynomial regression
    const regression = polynomialRegression(x, y, order);

    const regressionPoints = [];
    for (let timestamp = minTimestamp; timestamp <= maxTimestamp; timestamp += 86400000) {
        const xValue = (timestamp - minTimestamp) / 86400000; // Normalize x value to range [0, 1]
        const yValue = regression.predict(xValue);
        regressionPoints.push({
            x: new Date(timestamp),
            y: yValue
        });
    }
    return regressionPoints;
}

// Function to add or remove the regression line based on checkbox
function toggleRegression(stat) {
    const checkbox = document.getElementById("toggleRegression");
    const regressionDatasetIndex = statChart.data.datasets.findIndex(ds => ds.label.includes("Regression Line"));
    const minTimestamp = statChart.data.datasets[0].data[0].x.getTime();
    const maxTimestamp = statChart.data.datasets[0].data[statChart.data.datasets[0].data.length - 1].x.getTime();

    if (checkbox.checked) {
        //check if regression line already exists then remove it
        if (regressionDatasetIndex !== -1) {
            statChart.data.datasets.splice(regressionDatasetIndex, 1);
        }

        const data = statChart.data.datasets[0].data;
        const cleanedData = [];
        for (let i = 0; i < data.length; i++) {
            if (data[i].y !== null) {
                cleanedData.push({
                    x: (data[i].x.getTime() - minTimestamp) / 86400000, // Normalize x value to range [0, 1]
                    y: data[i].y
                });
            }
        }
        
        const regressionPoints = generatePolynomialRegression(cleanedData, 4, minTimestamp, maxTimestamp);
        
        // Add regression line as a new dataset
        statChart.data.datasets.push({
            label: `${stat} Regression Line`,
            data: regressionPoints,
            type: 'line',
            borderColor: 'red',
            borderWidth: 2,
            fill: false,
            pointRadius: 0
        });
    } else if (!checkbox.checked && regressionDatasetIndex !== -1) {
        // Remove the regression line dataset if it exists
        statChart.data.datasets.splice(regressionDatasetIndex, 1);
    }

    statChart.update();
}

// Modify updateChart to call toggleRegression
function updateChart(stat) {
    const startDate = new Date(document.getElementById("startDate").value).getTime();
    const endDate = new Date(document.getElementById("endDate").value).getTime();

    if (stat === "null") {
        stat = statChart.data.datasets[0].label;
    }

    const data = selectedAthleteData
        .filter(test => {
            const testDate = test.timestamp * 1000;
            return (!isNaN(startDate) ? testDate >= startDate : true) && 
                (!isNaN(endDate) ? testDate <= endDate : true);
        })
        .map(test => ({
            x: new Date(test.timestamp * 1000),
            y: test[stat]
        }));

    if (data.length === 0) {
        alert("No data available for the selected date range.");
        return;
    }

    statChart.data.datasets[0].data = data;
    statChart.data.datasets[0].label = stat;
    statChart.update();

    // Toggle regression line based on checkbox state
    if (statSelect.value) {
        toggleRegression(stat);
    }
}

function clearChart() {
    statChart.data.datasets[0].data = [];
    statChart.data.datasets[0].label = "";
    statChart.data.datasets.splice(1);
    statChart.update();
}

// Event listener for stat selection
statSelect.addEventListener("change", (event) => {
    const selectedStat = event.target.value;
    if (selectedStat) {
        updateChart(selectedStat);
    }
});

startDate.addEventListener("change", () => {
    if (statSelect.value) updateChart(statSelect.value);
});

endDate.addEventListener("change", () => {
    if (statSelect.value) updateChart(statSelect.value);
});

// Event listener for checkbox
document.getElementById("toggleRegression").addEventListener("change", () => {
    if (statSelect.value) toggleRegression(statSelect.value);
});

document.querySelectorAll('.time-filter-buttons .btn').forEach(button => {
    button.addEventListener('click', () => {
        const timeRange = button.getAttribute('data-time');
        const endDate = new Date();
        let startDate;

        switch (timeRange) {
            case 'week':
                startDate = new Date();
                startDate.setDate(endDate.getDate() - 7);
                break;
            case 'month':
                startDate = new Date();
                startDate.setMonth(endDate.getMonth() - 1);
                break;
            case 'year':
                startDate = new Date();
                startDate.setFullYear(endDate.getFullYear() - 1);
                break;
            case 'all':
                startDate = new Date(selectedAthleteData[0].timestamp * 1000);
                break;
        }

        // Set the date inputs (if you want to show them)
        if (startDate) {
            document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
        }
        document.getElementById('endDate').value = endDate.toISOString().split('T')[0];

        updateChart('null');
    });
});
