import csv
with open('products.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    adult = pensioner = child = 0
    for row in reader:
        adult += float(row['Взрослый'])
        pensioner += float(row['Пенсионер'])
        child += float(row['Ребенок'])
print(round(adult, 2), round(pensioner, 2), round(child, 2))
