import csv
with open('products.csv') as f:
    reader = csv.DictReader(f)
    adult = pensioner = child = 0
    for row in reader:
        adult += float(row['adult'])
        pensioner += float(row['pensioner'])
        child += float(row['child'])
print(round(adult, 2), round(pensioner, 2), round(child, 2))