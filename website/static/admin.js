
const statSelect = document.getElementById("statSelect");
const athleteSelect = document.getElementById("athleteSelect");
const teamSelect = document.getElementById("teamSelect");
const athleteList = document.getElementById("athlete_list")

let selectedAthleteData = [];

function loadStatOptions(data) {
    const ignoreKeys = ["id", "athlete_id", "athlete_name", "athlete_teams", "athlete_groups", "athlete_active", "testType_id", "testType_name", "testType_canonicalId", "tag_ids", "tag_names", "segment", "active", "timestamp"];
    let statKeys = Object.keys(data[0]).filter(key => !ignoreKeys.includes(key));
    //ingnore any key that starts with external
    statKeys = statKeys.filter(key => !key.startsWith("external"));

    //keep the stat loaded if one has already been selected
    if(statChart.options.scales.y.title.text != statSelect.value || statChart.options.scales.y.title.text == ""){
    statSelect.innerHTML = '<option value="">Select Stat</option>';
    }
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

function getMinMaxTimestamp(athlete_data) {
    const firstTestDate = new Date(athlete_data[athlete_data.length - 1].timestamp * 1000).toISOString().split("T")[0];
    const lastTestDate = new Date(athlete_data[0].timestamp * 1000).toISOString().split("T")[0];
    startDate.value = lastTestDate;
    endDate.value = firstTestDate;
}

// Set up Chart.js
const ctx = document.getElementById("statChart").getContext("2d");
const statChart = new Chart(ctx, {
    type: "scatter",
    data: {
        datasets: []
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
            statSelect.innerHTML = '<option value="">Select Stat</option>';
            clearChart();
            if (team){
                athleteList.innerHTML=""; //resets the athlete menu when a new team is selected
                for (const athlete of athleteData[team]) {
                    const option = document.createElement("option");
                    option.textContent = athlete;
                    athleteSelect.appendChild(option);

                    //Creating the Team list menu on the side
                    const listElement = document.createElement("li");
                    var check = document.createElement("INPUT");
                    let athlete_string = athlete+'';
                    check.setAttribute("type","checkbox");
                    check.setAttribute("id","checkbox"+athlete_string);
                    check.setAttribute("onclick","updateAthlete(\""+athlete_string+"\")");
                    var checklabel = document.createElement("label");
                    checklabel.setAttribute("for","checkbox"+athlete_string);
                    checklabel.setAttribute("id","label"+athlete_string);
                    checklabel.innerHTML=athlete_string;
                    listElement.appendChild(check);
                    listElement.appendChild(checklabel);
                    athleteList.appendChild(listElement); //appending the checkbox to the list
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
    
    let current_athlete = 0;
    athleteSelect.addEventListener("change", () => {
        let athlete = athleteSelect.value+'';
        if(current_athlete){
            //uncheck previously selected checkbox and selecte new checkbox
            let current_checkbox = document.getElementById("checkbox"+current_athlete);
            if(current_checkbox){
                current_checkbox.checked = false;
            }
            current_athlete = athlete;
            let new_checkbox = document.getElementById("checkbox"+athlete);
            new_checkbox.checked = true;
        }else{
            current_athlete = athlete;
            let new_checkbox = document.getElementById("checkbox"+athlete);
            new_checkbox.checked = true;
        }
        clearChart();
        athlete = athlete.replace(/ /g, "-");
        fetch(`/get_athlete_data/${athlete}`)
            .then(response => response.json())
            .then(data => {
                selectedAthleteData = data;
                updateCheckBoxChart(statSelect.value);
                loadStatOptions(data);
                getMinMaxTimestamp(selectedAthleteData);
            });
    });
} else {
    selectedAthleteData = athleteData;
    loadStatOptions(athleteData);
    getMinMaxTimestamp(selectedAthleteData); // why are their two function calls?
    updateCheckBoxChart("null");
    getMinMaxTimestamp(selectedAthleteData);
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


const currentRegression = {};
function multipleRegression(){            
    console.log("entering multiple regression");
    const checkbox = document.getElementById("toggleRegression");
    if(checkbox.checked == true){

        console.log("checkbox is true");
        //add regression lines
        for(let i = 0; i < statChart.data.datasets.length; i++){
            if(statChart.data.datasets[i].isregression == false){
                console.log("handling a dataset");
                //above conditional: executes for a dataset that isn't a regression and a regression has not been made for it
                let minTimestamp = statChart.data.datasets[i].data[0].x.getTime();
                let maxTimestamp = statChart.data.datasets[i].data[statChart.data.datasets[i].data.length - 1].x.getTime();
                
                //if the regression dataset for this user exists we want to delete it
                console.log("trying to delete athlete");
                let regression_index = statChart.data.datasets.findIndex(ds => ds.associated_athlete == statChart.data.datasets[i].label);
                console.log("MULTIPLE REGRESSON: regression index == "+regression_index);

                if(regression_index > 0){
                    statChart.data.datasets.splice(regression_index,1);
                }
                
                const data = statChart.data.datasets[i].data;
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
                statChart.data.datasets.push({
                    label: `${statChart.data.datasets[i].label} Regression Line`,
                    data: regressionPoints,
                    type: 'line',
                    borderColor: statChart.data.datasets[i].backgroundColor,
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0,
                    isregression: true,
                    associated_athlete: statChart.data.datasets[i].label
                });

            }
            else{
                //this is a regression, so we want to check that its associated dataset still exists
                let assoc_athlete = statChart.data.datasets[i].associated_athlete;
                let not_in_array = true;
                for(let i = 0; i < statChart.data.datasets.length;i++){
                    if(statChart.data.datasets[i].label == assoc_athlete){
                        not_in_array = false;
                    }
                }
                if(not_in_array){
                    statChart.data.datasets.splice(i,1);
                }

            }
        }
    }else{
        //remove regression lines
        console.log("Deleting all regression lines");
        function notRegression(value,index,array){
            console.log("This is a regression dataset: "+value.isregression);
            return value.isregression == false;
        }
        const only_athlete_data = statChart.data.datasets.filter(notRegression);
        statChart.data.datasets = only_athlete_data;
    }
    statChart.update();
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


/**
 * Returns true if the checkbox of the athlete is checked
 * Returns False Otherwise
 */
function isBoxChecked(athlete_name){
    const chbx = document.getElementById("checkbox"+athlete_name);
    let label = document.getElementById("label"+athlete_name);
    if(chbx.checked == true){
        return true;
    }else{
        return false;
    }
}

function updateChartColors(){
    console.log("Update Chart Colors is called");
    const colors = [
    "blue",
    "green",
    "orange",
    "pink",
    "#bb69f5",
    "#88d1a8",
    "#ff0000"
    ];
    let athlete_data_count = 0;
    console.log(statChart.data.datasets.length)
    for(let i = 0; i < statChart.data.datasets.length; i++){
        if(statChart.data.datasets[i].isregression == false){
            statChart.data.datasets[i].backgroundColor = colors[athlete_data_count % colors.length]
            console.log("athlete count % colors.length = "+(athlete_data_count % colors.length));
            athlete_data_count++;
        } 
    }
}
/**
 * Takes in a string, returns the athlete data from HD force
 */
function makeDataset(athlete_data,start,end,dataset_label,dataset_stat){
    let filtered_data = athlete_data
        .filter(test => {
            const testDate = test.timestamp * 1000;
            return (!isNaN(start) ? testDate >= start : true) && 
                (!isNaN(end) ? testDate <= end : true);
        })
        .map(test => ({
            x: new Date(test.timestamp * 1000),
            y: test[dataset_stat]
        }));
    const colors = [
    "blue",
    "green",
    "orange",
    "pink",
    "#bb69f5",
    "#88d1a8",
    "#ff0000"
    ];

    let athlete_data_count = 0;
    for(let i = 0; i < statChart.data.datasets.length; i++){
        if(statChart.data.datasets[i].isregression == false){
            athlete_data_count++;
        } 
    }
    console.log("Athlete_data_count =="+athlete_data_count);
    let color_index = athlete_data_count % colors.length;
    let newdataset = {
        label: dataset_label,
        data: filtered_data,
        borderColor: "white",
        backgroundColor: colors[color_index],
        pointRadius: 4,
        isregression:false
    };
    console.log("dataset made for "+dataset_label);
    return newdataset;
}

const loadedAthleteData = {}; //this Object will hold {athlete_name : athlete_data} in memory to avoid loading it multiple times

function updateAthlete(athlete_name){
    const chbx = document.getElementById("checkbox"+athlete_name);
    let label = document.getElementById("label"+athlete_name);
    if(statSelect.value){
        const startDate = new Date(document.getElementById("startDate").value).getTime();
        const endDate = new Date(document.getElementById("endDate").value).getTime();
        if(chbx.checked == true){
            if((athlete_name in loadedAthleteData) == false){
                console.log(athlete_name+" not in Object");
                //get the data
                let athlete = athlete_name.replace(/ /g, "-");
                fetch(`/get_athlete_data/${athlete}`)
                    .then(response => response.json())
                    .then(data => {
                        loadedAthleteData[athlete_name] = data;
                        let new_data = makeDataset(data,startDate,endDate,athlete_name,statSelect.value);
                        if(new_data.data != ""){
                            //check that data exists in the time range
                            statChart.data.datasets.push(new_data);
                            console.log("dataset pushed for "+athlete_name+" UPDATE AFTER FETCH");
                        }
                        updateChartColors();
                        multipleRegression();
                        statChart.update();
                    });
                }else{
                    //data already loaded in from memory
                    let data_from_memory = loadedAthleteData[athlete_name];
                    let new_data = makeDataset(data_from_memory,startDate,endDate,athlete_name,statSelect.value);
                    if(new_data.data != ""){
                        statChart.data.datasets.push(new_data);
                        console.log("Data pushed from memory")
                    }
                    updateChartColors();
                    statChart.update();
                }
        }else{
            //box was unchecked, try to remove the dataset
            for(let i = 0; i < statChart.data.datasets.length;i++){
                let label = statChart.data.datasets[i].label;
                if(label == athlete_name){
                    statChart.data.datasets.splice(i,1);
                    console.log("removed from stat Chart"+athlete_name);
                }
            }
            updateChartColors();
            statChart.update();
        }
    }
    //loading stat options if none have been loaded by checkbox select
    let current_state = document.getElementById("statSelect");
    if(current_state.options.length < 2){
        if(loadedAthleteData[athlete_name]){
            loadStatOptions(loadedAthleteData[athlete_name]);
        }else{
            let athlete = athlete_name.replace(/ /g, "-");
            fetch(`/get_athlete_data/${athlete}`)
                .then(response => response.json())
                .then(data => {
                    loadedAthleteData[athlete_name] = data;
                    loadStatOptions(data);
                    console.log("Stat options logged for "+athlete_name);
                });

        }
    }
    multipleRegression();
}

/**
 * This function updates the chart, checking the stat against every selected checkbox
 * in the checkbox area
 */
async function updateCheckBoxChart(stat){
    if (stat == "null"){
        stat = statSelect.value;
    }
    statChart.options.scales.y.title.text = stat;
    
    const startDate = new Date(document.getElementById("startDate").value).getTime();
    const endDate = new Date(document.getElementById("endDate").value).getTime();

    if(teamSelect.value){
        for (const athlete of athleteData[teamSelect.value]) {
            let athlete_string = athlete+'';

            //check if the box is checked
            if(isBoxChecked(athlete_string)){
                console.log("Box is checked for"+athlete_string);
                if((athlete_string in loadedAthleteData) == false){
                    console.log(athlete_string+" not in Object");
                    //get the data
                    let athlete = athlete_string.replace(/ /g, "-");
                    fetch(`/get_athlete_data/${athlete}`)
                        .then(response => response.json())
                        .then(data => {
                            console.log("Start Date value is "+startDate.value);
                            if(startDate.value == undefined){
                                console.log("INSIDE CONDITIONAL");
                                getMinMaxTimestamp(data);
                            }
                            loadedAthleteData[athlete_string] = data;
                            let new_data = makeDataset(data,startDate,endDate,athlete_string,stat);
                            statChart.data.datasets.push(new_data);
                            updateChartColors();
                            multipleRegression();
                            statChart.update();
                            console.log("dataset pushed for "+athlete_string+" UPDATE AFTER FETCH");
                        });
                }else{
                    //data already loaded in from memory
                    let data_from_memory = loadedAthleteData[athlete_string];
                    console.log("Start Date value is "+startDate.value);
                    if(startDate.value == undefined){
                        getMinMaxTimestamp(data_from_memory);
                    }
                    let new_data = makeDataset(data_from_memory,startDate,endDate,athlete_string,stat);
                    updateChartColors();
                    statChart.data.datasets.push(new_data);
                    }
            }else{
                //checkbox is unchecked, so look to remove dataset if it exists
            }

        }
        //do a final check after adding every necessary dataset to remove the ones
        //that are in the statChart but had their box unchecked
        console.log("checking to remove athletes");
        for(let i = 0; i < statChart.data.datasets.length;i++){
            let label =statChart.data.datasets[i].label;
            let chbox = document.getElementById("checkbox"+label);
            if(chbox && chbox.checked == false){
                statChart.data.datasets.splice(i,1);
            }
        }
        updateChartColors();
        multipleRegression();
        console.log("all necessary athletes removed");
        statChart.update();
        console.log("END OF FILE stat Chart updates");
    }

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
    if (statSelect.value) { //checks to see if a value is currently selected in the stat form
        statChart.options.scales.y.title.text=statSelect.value; //this sets the y axis label for the chart
        toggleRegression(stat);
    }
}

function clearChart() {
    statChart.data.datasets = [];
    statChart.update();
}

// Event listener for stat selection
statSelect.addEventListener("change", (event) => {
    const selectedStat = event.target.value;
    if (selectedStat) {
        clearChart();
        //updateChart(selectedStat);
        updateCheckBoxChart(selectedStat);
    }
});

startDate.addEventListener("change", () => {
    if (statSelect.value){
    clearChart();
    updateCheckBoxChart(statSelect.value);
    } 
});

endDate.addEventListener("change", () => {
    if (statSelect.value){
    clearChart();
    updateCheckBoxChart(statSelect.value);

    }
});

// Event listener for checkbox
document.getElementById("toggleRegression").addEventListener("change", () => {
    multipleRegression();
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
                let min = 9000000000;
                for(data in loadedAthleteData){
                    if((data[0].timestamp * 1000) < min){
                        min = data[0].timestamp * 1000;
                    }
                }
                startDate = new Date(min);
                break;
        }

        // Set the date inputs (if you want to show them)
        if (startDate) {
            document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
        }
        document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
        clearChart();
        updateCheckBoxChart('null');

    });
});
