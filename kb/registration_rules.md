# Nile Valley University (NVU) — Registration Rules for BSc Computer Science & AI

> **FICTIONAL SAMPLE POLICY.** These rules were written for the KBA assignment demonstration. They are not an official document of any real university.
> Each rule has a machine-readable `Parameters` line (read by the Python rule engine) and a human-readable `Text` line (indexed for retrieval).

## R1 — Standard credit load
- Parameters: min_credits=12; max_credits=18
- Text: A full-time student registers for between 12 and 18 credit hours per semester. Registering for fewer than 12 credit hours makes the student part-time, which must be flagged to the advisor. No student may exceed 18 credit hours unless rule R2 applies.

## R2 — Credit overload
- Parameters: min_gpa=3.5; max_credits_overload=21
- Text: A student with a cumulative GPA of 3.5 or higher may request an overload of up to 21 credit hours in one semester. An overload always requires written advisor approval, so it is flagged and is never approved automatically. No overload above 21 credit hours is allowed for any student.

## R3 — Academic probation load limit
- Parameters: gpa_below=2.0; max_credits=12
- Text: A student whose cumulative GPA is below 2.0 is on academic probation and may register for at most 12 credit hours in a semester, regardless of the requested load.

## R4 — Prerequisites and minimum grade
- Parameters: min_prereq_grade=C
- Text: Every prerequisite listed for a course must have been completed with a grade of C or higher. A grade of C-, D+, D or F does not satisfy a prerequisite, even though a D grade earns credit hours. Grade scale from best to worst: A, A-, B+, B, B-, C+, C, C-, D+, D, F. A prerequisite that is only in progress or planned does not count.

## R5 — Repeating courses
- Parameters: repeat_below=C
- Text: A student may not register again for a course already passed with a grade of C or higher. A course completed with a grade below C (C-, D+, D) or failed (F) may be repeated once more to improve the grade. Credit hours of a repeated course are counted only once toward graduation.

## R6 — Course level restriction
- Parameters: level_step=100
- Text: A student in academic year Y may register for courses numbered up to Y x 100 (for example, a Year 2 student may take 100-level and 200-level courses). A course exactly one level above the student's year requires written advisor approval, so it is flagged and not recommended automatically. Courses two or more levels above the student's year are not allowed.

## R7 — Academic year classification
- Parameters: year2_from=30; year3_from=60; year4_from=90
- Text: Academic year is determined by earned credit hours: Year 1 is below 30, Year 2 is 30 to 59, Year 3 is 60 to 89 and Year 4 is 90 or more. If the year stated by the student does not match the earned credit hours, the mismatch is flagged for the registrar.

## R8 — Course availability by semester
- Parameters: none
- Text: A course can only be registered in a semester in which it is offered, as stated in the course catalog (Fall, Spring or both). A course whose offering is not published cannot be registered.

## R9 — Timetable conflicts
- Parameters: none
- Text: Two courses whose weekly meeting times overlap on the same day cannot be registered together. Each course in the catalog has a single published section.

## R10 — Corequisites
- Parameters: none
- Text: A corequisite must be completed already or registered in the same semester as the course that lists it. If the corequisite cannot be registered, the course cannot be registered either.

## R11 — Minimum earned credit hours for advanced courses
- Parameters: none
- Text: Some courses, such as the capstone Senior Project I, list a minimum number of earned credit hours in the catalog. Earned credit hours include passed NVU courses (grade D or better) and accepted transfer credits. The student must have reached the minimum before registration.

## R12 — Incomplete course information
- Parameters: none
- Text: If the catalog does not publish a required detail of a course (prerequisites, schedule, or semester offering), eligibility cannot be verified. The course must not be recommended automatically and the student is referred to the academic advisor.

## R13 — Heavy workload limit
- Parameters: max_heavy=2; gpa_threshold=2.5; max_heavy_low_gpa=1
- Text: Courses marked Heavy in the catalog have a weekly workload of more than 12 hours. A student may register for at most 2 Heavy courses per semester. A student with a cumulative GPA below 2.5 may register for at most 1 Heavy course per semester.

## R14 — Advisor approval process
- Parameters: none
- Text: Any request flagged as requiring advisor approval (overload, course one level above the student's year, incomplete course information) must be submitted on the NVU registration portal by the end of the first week of registration. Flagged courses are not counted in the recommended schedule until the advisor approves them.
