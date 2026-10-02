class Marks:
    """Represents academic evaluation and continuous grading marks for a student in a subject."""

    def __init__(
        self,
        marks_id,
        student_id,
        subject_id,
        faculty_id,
        cca1=0,
        cca2=0,
        cca3=0,
        midterm=0,
        final_exam=0,
        total_marks=None,
        academic_year="2026-2027",
        semester=1,
        created_at=None,
        updated_at=None
    ):
        self.marks_id = marks_id
        self.student_id = student_id
        self.subject_id = subject_id
        self.faculty_id = faculty_id
        self.cca1 = int(cca1 or 0)
        self.cca2 = int(cca2 or 0)
        self.cca3 = int(cca3 or 0)
        self.midterm = int(midterm or 0)
        self.final_exam = int(final_exam or 0)
        self.total_marks = int(total_marks) if total_marks is not None else (self.cca1 + self.cca2 + self.cca3 + self.midterm + self.final_exam)
        self.academic_year = academic_year
        self.semester = int(semester)
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def grade_details(self):
        """Returns (Letter Grade, Grade Point, Performance Description)."""
        tm = self.total_marks
        if tm >= 90:
            return "O", 10, "Outstanding"
        elif tm >= 80:
            return "A+", 9, "Excellent"
        elif tm >= 70:
            return "A", 8, "Very Good"
        elif tm >= 60:
            return "B+", 7, "Good"
        elif tm >= 50:
            return "B", 6, "Above Average"
        elif tm >= 40:
            return "C", 5, "Pass"
        else:
            return "F", 0, "Fail"

    @property
    def letter_grade(self):
        return self.grade_details[0]

    @property
    def grade_point(self):
        return self.grade_details[1]

    @property
    def is_passed(self):
        return self.grade_point >= 5

    def to_dict(self):
        grade, gp, desc = self.grade_details
        return {
            "marks_id": self.marks_id,
            "student_id": self.student_id,
            "subject_id": self.subject_id,
            "faculty_id": self.faculty_id,
            "cca1": self.cca1,
            "cca2": self.cca2,
            "cca3": self.cca3,
            "midterm": self.midterm,
            "final_exam": self.final_exam,
            "total_marks": self.total_marks,
            "letter_grade": grade,
            "grade_point": gp,
            "performance": desc,
            "academic_year": self.academic_year,
            "semester": self.semester
        }
