import csv

with open("migrate_scripts/data/staff.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get("full_name", "")
        email = row.get("email", "")
        phone = row.get("phone_number", "")
        designation = row.get("designation", "")

        if len(name) > 100:
            print(f"Name ({len(name)} chars): {name}")
        if len(email) > 254:
            print(f"Email ({len(email)} chars): {email} | Name: {name}")
        if len(phone) > 20:
            print(f"Phone ({len(phone)} chars): {phone} | Name: {name}")
        if len(designation) > 100:
            print(
                f"Designation ({len(designation)} chars): {designation} | Name: {name}",
            )
