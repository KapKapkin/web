n, m = map(int, input().split())
items = []

for _ in range(m):
    line = input().strip().split()
    name = line[0]
    weight = int(line[1])
    value = int(line[2])
    items.append((name, weight, value, value / weight))

items.sort(key=lambda x: x[3], reverse=True)

total_weight = 0
result = []

for name, weight, value, ratio in items:
    if total_weight + weight <= n:
        result.append((name, weight, value))
        total_weight += weight
    elif total_weight < n:
        remaining_capacity = n - total_weight
        fraction = remaining_capacity / weight
        fractional_weight = remaining_capacity
        fractional_value = value * fraction
        result.append((name, fractional_weight, fractional_value))
        break

result.sort(key=lambda x: x[2], reverse=True)

for name, weight, value in result:
    if weight == int(weight) and value == int(value):
        print(f"{name} {int(weight)} {int(value)}")
    else:
        print(f"{name} {weight:.2f} {value:.2f}")
