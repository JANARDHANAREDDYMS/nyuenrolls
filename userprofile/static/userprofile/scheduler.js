// Mock Data
const departments = {
    "Computer Science": [
        { name: "CS-GY 1013: Algorithms", day: "Monday", start: 10, end: 12, sections: ["A", "B"] },
        { name: "CS-GY 1023: Artificial Intelligence", day: "Wednesday", start: 14, end: 16, sections: ["A"] },
        { name: "CS-GY 1133: Data Structures", day: "Tuesday", start: 9, end: 11, sections: ["A"] },
        { name: "CS-GY 2013: Software Engineering", day: "Thursday", start: 11, end: 13, sections: ["A", "B"] },
        { name: "CS-GY 3033: Machine Learning", day: "Friday", start: 14, end: 16, sections: ["A"] },
    ],
    "Electrical Engineering": [
        { name: "EE-GY 2013: Circuit Theory", day: "Tuesday", start: 9, end: 11, sections: ["A", "B"] },
        { name: "EE-GY 2023: Digital Systems", day: "Friday", start: 11, end: 13, sections: ["A"] },
    ],
    "Mathematics": [
        { name: "MATH-GY 1013: Calculus I", day: "Monday", start: 9, end: 11, sections: ["A"] },
        { name: "MATH-GY 1023: Linear Algebra", day: "Thursday", start: 11, end: 13, sections: ["A", "B"] },
    ],
};


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
        const selectedDept = departmentsDropdown.value;
        const selectedCourseName = coursesDropdown.value;
        const selectedSection = sectionsDropdown.value;

        const courseIdentifier = `${selectedCourseName} (Section ${selectedSection})`;

        // Check if the maximum number of courses (6) has been reached
        if (addedCourses.size >= 6) {
            alert("You cannot add more than 6 courses at the same time.");
            return; // Exit if the limit is reached
        }

        if (addedCourses.has(courseIdentifier)) {
            alert("This course has already been added.");
            return; // Exit if the course is already added
        }

        const course = departments[selectedDept].find((c) => c.name === selectedCourseName);

        if (course) {
            const li = document.createElement("li");
            li.classList.add("course-entry");
            li.textContent = `${course.name} (Section ${selectedSection}, ${course.day}, ${course.start}:00 - ${course.end}:00)`;

            const removeBtn = document.createElement("button");
            removeBtn.textContent = "Remove";
            removeBtn.addEventListener("click", () => {
                li.remove();
                removeCourseFromSchedule(course);
                addedCourses.delete(courseIdentifier); // Remove from added courses
            });

            li.appendChild(removeBtn);
            selectedCoursesList.appendChild(li);

            addCourseToSchedule(course);
            addedCourses.add(courseIdentifier); // Add to added courses
            closeCourseSelector(); // Close the course selector
        }
    });


    // Close the course selector
    function closeCourseSelector() {
        courseSelector.classList.add("hidden");
        resetCoursesDropdown(); // Reset courses dropdown
        resetSectionsDropdown(); // Reset sections dropdown
        departmentsDropdown.selectedIndex = 0; // Reset department selection
    }

// Display the course on the schedule
function addCourseToSchedule(course) {
    const rows = scheduleBody.querySelectorAll("tr");
    for (let i = course.start; i < course.end; i++) {
        const cell = rows[i - 8].querySelector(`td:nth-child(${getDayIndex(course.day)})`);
        
        // Create a new div for the course block
        const courseBlock = document.createElement("div");
        courseBlock.classList.add("course-block");
        courseBlock.textContent = course.name;
        
        // Append the new course block to the existing content in the cell
        cell.appendChild(courseBlock);
    }
}

// Remove course from schedule
function removeCourseFromSchedule(course) {
    const rows = scheduleBody.querySelectorAll("tr");
    for (let i = course.start; i < course.end; i++) {
        const cell = rows[i - 8].querySelector(`td:nth-child(${getDayIndex(course.day)})`);
        
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

    // Create schedule rows dynamically (8 AM - 8 PM)
    for (let hour = 8; hour <= 20; hour++) {
        const row = document.createElement("tr");

        const timeCell = document.createElement("td");
        timeCell.textContent = `${hour}:00`;
        row.appendChild(timeCell);

        for (let i = 0; i < 6; i++) {
            const cell = document.createElement("td");
            row.appendChild(cell);
        }

        scheduleBody.appendChild(row);
    }

    // Toggle course selector visibility and reset departments dropdown
    addCourseBtn.addEventListener("click", () => {
        courseSelector.classList.toggle("hidden");
        populateDepartments(); // Reset and populate departments
    });
});
