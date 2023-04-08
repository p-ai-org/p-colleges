import csv

input_file = r"C:\Users\brian\Desktop\p-colleges\p-colleges\Brian\Unigo\AllCampus.csv"
output_file = r"C:\Users\brian\Desktop\p-colleges\p-colleges\Brian\Unigo\FilteredCampus.csv"

unique_rows = set()

with open(input_file, "r") as f:
    reader = csv.reader(f)

    for row in reader:
        if "college" in row[0].lower() or "university" in row[0].lower() or "institute" in row[0].lower():
            school = row[0].lower()
            if " - " in school:
                school.replace(" - ", "-")
            unique_rows.add(school)

filtered_rows = sorted(list(unique_rows))

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    for row in filtered_rows:
        writer.writerow([row])

