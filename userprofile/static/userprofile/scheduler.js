/*console.log(departments);

// Example of how you might display the department names and courses in the console
Object.keys(departments).forEach(department => {
    console.log(department);  // Department name
    departments[department].forEach(course => {
        console.log(course.name);  // Course name
        console.log(course.day);   // Class days
        console.log(course.start); // Start time
        console.log(course.start_mins); // Start time
        console.log(course.end);   // End time
        console.log(course.end_mins); // Start time
        console.log(course.sections);  // Sections
    });
}); */

document.addEventListener("DOMContentLoaded", () => {
const departmentsDropdown = document.getElementById("departments");
const coursesDropdown = document.getElementById("courses");
const sectionsDropdown = document.getElementById("sections");
const selectedCoursesList = document.getElementById("selected-courses");
const scheduleBody = document.getElementById("schedule-body");

const addCourseBtn = document.getElementById("add-course-btn");
const courseSelector = document.getElementById("course-selector");

const addedCourses = new Set(); // To track added courses

// Populate departments dropdown
function populateDepartments() {
    departmentsDropdown.innerHTML = ""; // Clear previous options
    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Select Department";
    departmentsDropdown.appendChild(defaultOption);

    Object.keys(departments).forEach((dept) => {
        const option = document.createElement("option");
        option.value = dept;
        option.textContent = dept;
        departmentsDropdown.appendChild(option);
    });

    resetCoursesDropdown(); // Reset courses dropdown
    resetSectionsDropdown(); // Reset sections dropdown
}

// Reset courses dropdown
function resetCoursesDropdown() {
    coursesDropdown.innerHTML = ""; // Clear previous options
    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Select Course";
    coursesDropdown.appendChild(defaultOption);
    coursesDropdown.disabled = true; // Disable until department is selected
}

// Reset sections dropdown
function resetSectionsDropdown() {
    sectionsDropdown.innerHTML = ""; // Clear previous options
    const defaultOption = document.createElement("option");
    defaultOption.value = "";
    defaultOption.textContent = "Select Section";
    sectionsDropdown.appendChild(defaultOption);
    sectionsDropdown.disabled = true; // Disable until course is selected
}

// When department changes, update courses dropdown
departmentsDropdown.addEventListener("change", () => {
resetCoursesDropdown(); // Reset to placeholder
const selectedDept = departmentsDropdown.value;

if (selectedDept) {
    departments[selectedDept]?.forEach((course) => {
        const option = document.createElement("option");
        option.value = course.name;
        option.textContent = course.name;
        coursesDropdown.appendChild(option);
    });
    coursesDropdown.disabled = false; // Enable courses dropdown

    // Disable already selected courses
    disableSelectedCourses();
}
});

// Function to disable already added courses in the courses dropdown
function disableSelectedCourses() {
const selectedCourseItems = Array.from(selectedCoursesList.children).map(item => {
    return item.textContent.split(" (")[0]; // Extract course name
});

const courseOptions = coursesDropdown.querySelectorAll("option");
courseOptions.forEach(option => {
    if (selectedCourseItems.includes(option.value)) {
        option.disabled = true; // Disable the option if already selected
    } else {
        option.disabled = false; // Enable the option if not selected
    }
});
}


// When course changes, update sections dropdown
coursesDropdown.addEventListener("change", () => {
    resetSectionsDropdown(); // Reset to placeholder
    const selectedDept = departmentsDropdown.value;
    const selectedCourseName = coursesDropdown.value;

    const course = departments[selectedDept].find((c) => c.name === selectedCourseName);

    if (course) {
        course.sections.forEach((section) => {
            const option = document.createElement("option");
            option.value = section;
            option.textContent = section;
            sectionsDropdown.appendChild(option);
        });
        sectionsDropdown.disabled = false; // Enable sections dropdown
    }
});

// Add selected course to the list and display in scheduler
sectionsDropdown.addEventListener("change", () => {
    console.log("Section changed"); // Debug log
    
    const selectedDept = departmentsDropdown.value;
    const selectedCourseName = coursesDropdown.value;
    const selectedSection = sectionsDropdown.value;

    console.log("Selected values:", { selectedDept, selectedCourseName, selectedSection }); // Debug log

    if (!selectedDept || !selectedCourseName || !selectedSection) {
        console.log("Missing selection"); // Debug log
        return;
    }

    const courseIdentifier = `${selectedCourseName} (Section ${selectedSection})`;

    // Check if the maximum number of courses (6) has been reached
    if (addedCourses.size >= 6) {
        alert("You cannot add more than 6 courses at the same time.");
        return;
    }

    if (addedCourses.has(courseIdentifier)) {
        alert("This course has already been added.");
        return;
    }

    // Find the course in the departments data
    const course = departments[selectedDept].find((c) => c.name === selectedCourseName);
    console.log("Found course:", course); // Debug log

    if (course) {
        const sectionIndex = course.sections.indexOf(selectedSection);
        console.log("Section index:", sectionIndex); // Debug log

        // Only proceed if we found a valid section index
        if (sectionIndex === -1) {
            console.log("Invalid section index"); // Debug log
            return;
        }

        // Create list item for selected courses
        const li = document.createElement("li");
        li.classList.add("course-entry");
        li.textContent = `${course.name} (Section ${selectedSection}, ${course.day[sectionIndex]}, ${course.start[sectionIndex]}:${course.start_mins[sectionIndex]} - ${course.end[sectionIndex]}:${course.end_mins[sectionIndex]})`;

        // Create remove button
        const removeBtn = document.createElement("button");
        removeBtn.textContent = "Remove";
        removeBtn.addEventListener("click", () => {
            li.remove();
            removeCourseFromSchedule(course, sectionIndex);
            addedCourses.delete(courseIdentifier);
        });

        // Add the course to the UI
        li.appendChild(removeBtn);
        selectedCoursesList.appendChild(li);

        // Add course to schedule and track it
        addCourseToSchedule(course, sectionIndex);
        addedCourses.add(courseIdentifier);

        // Reset selectors
        closeCourseSelector();
    } else {
        console.log("Course not found"); // Debug log
    }
});


// Close the course selector
function closeCourseSelector() {
    courseSelector.classList.add("hidden");
    resetCoursesDropdown(); // Reset courses dropdown
    resetSectionsDropdown(); // Reset sections dropdown
    departmentsDropdown.selectedIndex = 0; // Reset department selection
}

function addCourseToSchedule(course, sectionIndex) {
    const rows = scheduleBody.querySelectorAll("tr");
    const startHour = course.start[sectionIndex];
    const endHour = course.end[sectionIndex];
    const startMin = course.start_mins[sectionIndex] === "30" ? 1 : 0;
    const endMin = course.end_mins[sectionIndex] === "30" ? 1 : 0;
    
    const startRow = (startHour - 8) * 2 + startMin;
    const endRow = (endHour - 8) * 2 + endMin;
    
    for (let i = startRow; i < endRow; i++) {
        const cell = rows[i].querySelector(`td:nth-child(${getDayIndex(course.day[sectionIndex])})`);
        
        // Check for existing blocks
        const existingBlocks = cell.querySelectorAll('div');
        
        // Create new course block
        const courseBlock = document.createElement("div");
        courseBlock.textContent = course.name;
        
        if (existingBlocks.length > 0) {
            // If there are existing blocks, make everything red
            courseBlock.className = 'time-conflict';
            existingBlocks.forEach(block => {
                block.className = 'time-conflict';
            });
        } else {
            // If no existing blocks, make it yellow
            courseBlock.className = 'course-block';
        }
        
        cell.appendChild(courseBlock);
    }
}

function checkTimeConflict(course, sectionIndex) {
    const rows = scheduleBody.querySelectorAll("tr");
    const startHour = course.start[sectionIndex];
    const endHour = course.end[sectionIndex];
    const startMin = course.start_mins[sectionIndex] === "30" ? 1 : 0;
    const endMin = course.end_mins[sectionIndex] === "30" ? 1 : 0;
    
    const startRow = (startHour - 8) * 2 + startMin;
    const endRow = (endHour - 8) * 2 + endMin;
    
    for (let i = startRow; i < endRow; i++) {
        const cell = rows[i].querySelector(`td:nth-child(${getDayIndex(course.day[sectionIndex])})`);
        if (cell.querySelectorAll('.course-block').length > 0) {
            return true; // Conflict found
        }
    }
    return false; // No conflict
}


function removeCourseFromSchedule(course, sectionIndex) {
    const rows = scheduleBody.querySelectorAll("tr");
    const startHour = course.start[sectionIndex];
    const endHour = course.end[sectionIndex];
    const startMin = course.start_mins[sectionIndex] === "30" ? 1 : 0; // "30" -> 1 for half hour
    const endMin = course.end_mins[sectionIndex] === "30" ? 1 : 0; // "30" -> 1 for half hour
    
    const startRow = (startHour - 8) * 2 + startMin; // Adjust for the 8 AM starting row
    const endRow = (endHour - 8) * 2 + endMin; // Adjust for the 8 AM starting row
    
    for (let i = startRow; i < endRow; i++) {
        const cell = rows[i].querySelector(`td:nth-child(${getDayIndex(course.day[sectionIndex])})`);
        
        // Remove only the specific course block, if needed
        const courseBlocks = cell.querySelectorAll(".course-block");
        courseBlocks.forEach((block) => {
            if (block.textContent === course.name) {
                cell.removeChild(block);
            }
        });
    }
}



// Get index for the day of the week
function getDayIndex(day) {
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    return days.indexOf(day) + 2; // +2 to match table column index
}

// Create schedule rows dynamically (8 AM - 8 PM) with 30-minute intervals
for (let hour = 8; hour <= 20; hour++) {
    // Create rows for 30-minute intervals
    for (let halfHour = 0; halfHour < 2; halfHour++) {
        const row = document.createElement("tr");

        // Display time with 30-minute increments
        const timeCell = document.createElement("td");
        const hourText = `${hour}:${halfHour === 0 ? "00" : "30"}`;
        timeCell.textContent = hourText;
        row.appendChild(timeCell);

        // Create cells for the days (Monday to Saturday)
        for (let i = 0; i < 6; i++) {
            const cell = document.createElement("td");
            row.appendChild(cell);
        }

        scheduleBody.appendChild(row);
    }
}

// Toggle course selector visibility and reset departments dropdown
addCourseBtn.addEventListener("click", () => {
    courseSelector.classList.toggle("hidden");
    populateDepartments(); // Reset and populate departments
});
});
