import csv
from datetime import datetime


class ExportHelper:
    """Helper utility to export ERP reports, grade transcripts, and attendance logs to CSV format."""

    @staticmethod
    def export_student_transcript_to_csv(student_info, marks_list, filepath="transcript.csv"):
        """Exports a student's grade sheet / academic transcript to a CSV file."""
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["CAMPUSHUB ERP - OFFICIAL ACADEMIC TRANSCRIPT"])
            writer.writerow(["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])
            writer.writerow(["Student ID", student_info.get("student_id", "")])
            writer.writerow(["Name", student_info.get("full_name", "")])
            writer.writerow(["Email", student_info.get("email", "")])
            writer.writerow(["Department", student_info.get("department_name", "")])
            writer.writerow([])
            writer.writerow(["Subject Code", "Subject Name", "Credits", "CCA (Total 30)", "Midterm (20)", "Final Exam (50)", "Total Marks", "Grade", "Status"])

            total_credits = 0
            weighted_gp = 0

            for m in marks_list:
                credits = m.get("credits", 3)
                total_m = m.get("total_marks", 0)
                cca = m.get("cca1", 0) + m.get("cca2", 0) + m.get("cca3", 0)
                grade = m.get("letter_grade", "F")
                gp = m.get("grade_point", 0)
                status = "PASS" if gp >= 5 else "FAIL"

                total_credits += credits
                weighted_gp += (gp * credits)

                writer.writerow([
                    m.get("subject_code", ""),
                    m.get("subject_name", ""),
                    credits,
                    cca,
                    m.get("midterm", 0),
                    m.get("final_exam", 0),
                    total_m,
                    grade,
                    status
                ])

            sgpa = (weighted_gp / total_credits) if total_credits > 0 else 0.0
            writer.writerow([])
            writer.writerow(["Total Credits Earned", total_credits])
            writer.writerow(["Cumulative SGPA", f"{sgpa:.2f}"])

        return filepath

    @staticmethod
    def export_attendance_report_to_csv(records, filepath="attendance_report.csv"):
        """Exports attendance records to a CSV file."""
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["CAMPUSHUB ERP - ATTENDANCE SUMMARY REPORT"])
            writer.writerow(["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])
            writer.writerow(["Subject Code", "Subject Name", "Total Sessions", "Present", "Absent", "Attendance %", "Exam Eligibility"])

            for r in records:
                total = r.get("total_sessions", 0)
                present = r.get("present_count", 0) or 0
                absent = r.get("absent_count", 0) or 0
                pct = (present / total * 100) if total > 0 else 0.0
                status = "ELIGIBLE" if pct >= 75.0 else "SHORTAGE (<75%)"

                writer.writerow([
                    r.get("subject_code", ""),
                    r.get("subject_name", ""),
                    total,
                    present,
                    absent,
                    f"{pct:.2f}%",
                    status
                ])

        return filepath
