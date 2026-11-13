
import csv
import re
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation


# --------------------------------------------------
# 1. LOAD CSV FILES
# --------------------------------------------------

def load_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


system_a = load_csv("app/data/system_a.csv")
system_b = load_csv("app/data/system_b.csv")


# --------------------------------------------------
# 2. NORMALIZE RECORD REFERENCES
# --------------------------------------------------

def normalize_reference(value):
    value = value.strip().upper()
    value = re.sub(r"[\s-]", "", value)

    if value.isdigit():
        value = "REC" + value

    return value


# --------------------------------------------------
# 3. FIND DUPLICATE REFERENCES IN SYSTEM B
# --------------------------------------------------

references = [
    normalize_reference(row["record_ref"])
    for row in system_b
]

counts = Counter(references)

print("\n--- DUPLICATE REFERENCES ---")

for ref, count in counts.items():
    if count > 1:
        print(ref, "appears", count, "times")


# --------------------------------------------------
# 4. FIND UNMATCHED REFERENCES
# --------------------------------------------------

a_ids = {
    normalize_reference(row["record_id"])
    for row in system_a
}

b_refs = {
    normalize_reference(row["record_ref"])
    for row in system_b
}

print("\n--- RECORDS MISSING FROM SYSTEM B ---")

for ref in sorted(a_ids - b_refs):
    print(ref)

print("\n--- EXTRA RECORDS IN SYSTEM B ---")

for ref in sorted(b_refs - a_ids):
    print(ref)


# --------------------------------------------------
# 5. GROUP SYSTEM B RECORDS
# --------------------------------------------------

b_grouped = defaultdict(list)

for row in system_b:
    ref = normalize_reference(row["record_ref"])
    b_grouped[ref].append(row)


a_grouped = {
    normalize_reference(row["record_id"]): row
    for row in system_a
}


# --------------------------------------------------
# 6. INSPECT DUPLICATE RECORD DETAILS
# --------------------------------------------------

print("\n--- DUPLICATE RECORD DETAILS ---")

for ref, records in b_grouped.items():
    if len(records) > 1:
        print(f"\nReference: {ref}")

        for row in records:
            print(row)


# --------------------------------------------------
# 7. COMPARE KNOWN DUPLICATES WITH SYSTEM A
# --------------------------------------------------

print("\n--- COMPARE DUPLICATES WITH SYSTEM A ---")

for ref in ["REC1042", "REC1055"]:

    a_record = a_grouped.get(ref)
    b_records = b_grouped.get(ref, [])

    if not a_record:
        continue

    a_value = Decimal(a_record["total_value"])

    try:
        b_total = sum(
            (Decimal(row["value"]) for row in b_records),
            Decimal("0")
        )

        print(f"\nReference: {ref}")
        print("System A total:", a_value)
        print("System B entry count:", len(b_records))
        print("System B combined total:", b_total)
        print("Difference:", b_total - a_value)

    except InvalidOperation:
        print(f"\nReference: {ref} contains an invalid amount")


# --------------------------------------------------
# 8. CHECK MATCHED RECORDS FOR DIFFERENCES
# --------------------------------------------------

print("\n--- MATCHED RECORDS WITH DIFFERENCES ---")

for ref in sorted(set(a_grouped) & set(b_grouped)):

    a_record = a_grouped[ref]
    b_records = b_grouped[ref]

    a_value = Decimal(a_record["total_value"])

    problems = []

    # Check whether System B amounts are valid
    b_total = Decimal("0")
    invalid_values = []

    for row in b_records:
        try:
            amount = row["value"].strip().replace(",", "")

            if not amount:
                raise InvalidOperation

            b_total += Decimal(amount)
        except InvalidOperation:
            invalid_values.append({
                "entry_id": row["entry_id"],
                "value": row["value"]
            })

    if invalid_values:
        problems.append("INVALID_VALUE")

    # Check location
    if any(
        row["location_id"] != a_record["location_id"]
        for row in b_records
    ):
        problems.append("LOCATION_MISMATCH")

    # Check date
    if any(
        row["recorded_on"] != a_record["event_date"]
        for row in b_records
    ):
        problems.append("DATE_MISMATCH")

    # Check total amount
    if not invalid_values and b_total != a_value:
        problems.append("VALUE_MISMATCH")

    # Identify multiple entries
    if len(b_records) > 1:
        problems.append("MULTIPLE_ENTRIES")

    # Print only records with problems
    if problems:

        print(f"\nReference: {ref}")
        print("Problems:", problems)
        print("System A total:", a_value)
        print("System B total:", b_total)
        print("System B entries:", len(b_records))

        if invalid_values:
            print("Invalid amount records:", invalid_values)


print("\n--- ANALYSIS COMPLETED ---")
