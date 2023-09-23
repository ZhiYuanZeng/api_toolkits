# Unclear, unorganized, and non-modular code example

name = input("Enter student name: ")
age = int(input("Enter student age: "))

grades = []
total = 0

for _ in range(5):
    grade = int(input("Enter grade: "))
    grades.append(grade)
    total += grade
    
average = total / len(grades)

print("Student information:")
print(f"Name: {name}")
print(f"Age: {age}")
print(f"Average grade: {average}")
