import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { ArrowsUpDown } from "lucide-react";

const CourseSwap = ({ enrolledCourses: initialEnrolled, waitlistedCourses: initialWaitlisted }) => {
  const [enrolledCourses, setEnrolledCourses] = useState(initialEnrolled);
  const [waitlistedCourses, setWaitlistedCourses] = useState(initialWaitlisted);
  const [selectedEnrolled, setSelectedEnrolled] = useState('');
  const [selectedWaitlisted, setSelectedWaitlisted] = useState('');
  const [showSwapOptions, setShowSwapOptions] = useState(false);

  const handleSwap = () => {
    if (!showSwapOptions) {
      setShowSwapOptions(true);
      return;
    }

    if (selectedEnrolled && selectedWaitlisted) {
      // Create and submit form for backend processing
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = "{% url 'courseEnroll:swap_courses' %}";
      
      // Add CSRF token
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrfmiddlewaretoken';
      csrfInput.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
      form.appendChild(csrfInput);

      // Add selected courses
      const enrolledInput = document.createElement('input');
      enrolledInput.type = 'hidden';
      enrolledInput.name = 'enrolled_course_id';
      enrolledInput.value = selectedEnrolled;
      form.appendChild(enrolledInput);

      const waitlistedInput = document.createElement('input');
      waitlistedInput.type = 'hidden';
      waitlistedInput.name = 'waitlisted_course_id';
      waitlistedInput.value = selectedWaitlisted;
      form.appendChild(waitlistedInput);

      document.body.appendChild(form);
      form.submit();
    }
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-white shadow-sm">
      <Button 
        onClick={handleSwap}
        className="w-full bg-[#57068c] hover:bg-[#4b007d] text-white flex items-center justify-center"
      >
        <ArrowsUpDown className="mr-2 h-4 w-4" />
        {showSwapOptions ? 'Confirm Swap' : 'Swap Courses'}
      </Button>

      {showSwapOptions && (
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Select Enrolled Course:</label>
            <select
              value={selectedEnrolled}
              onChange={(e) => setSelectedEnrolled(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#57068c]"
            >
              <option value="">Select a course...</option>
              {enrolledCourses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.name} ({course.id}) - {course.credits} credits
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Select Waitlisted Course:</label>
            <select
              value={selectedWaitlisted}
              onChange={(e) => setSelectedWaitlisted(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-[#57068c]"
            >
              <option value="">Select a course...</option>
              {waitlistedCourses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.name} ({course.id}) - {course.credits} credits - {course.points_assigned} points
                </option>
              ))}
            </select>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseSwap;