# Clear, self-contained, instructive, modular, and reusable code example

class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.grades = []

    def add_grade(self, grade):
        """Adds a grade to the student's list of grades."""
        self.grades.append(grade)

    def calculate_average_grade(self):
        """Calculates the average grade of the student."""
        total = sum(self.grades)
        average = total / len(self.grades)
        return average

# Usage example
student1 = Student("Alice", 18)
student1.add_grade(85)
student1.add_grade(92)
average_grade = student1.calculate_average_grade()
print(f"The average grade for {student1.name} is {average_grade}.")
