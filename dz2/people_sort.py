def people_sort(people):
    return sorted(people, key=lambda x: x['age'])

if __name__ == '__main__':
    n = int(input())
    people = []
    for _ in range(n):
        name, surname, age, gender = input().split()
        people.append({
            'name': f"{name} {surname}",
            'age': int(age),
            'gender': gender
        })

    sorted_people = people_sort(people)
    for person in sorted_people:
        title = "Mr." if person['gender'] == 'M' else "Ms."
        print(f"{title} {person['name']}")
