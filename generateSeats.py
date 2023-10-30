import json

# A utility function to generate the seat data

def generate_seats_for_hall(hall_name, total_seats):
    seats_per_row = 15
    rows = total_seats // seats_per_row
    remaining_seats = total_seats % seats_per_row

    seats = []

    # Generate seat data for complete rows
    for row in range(1, rows + 1):
        for seat_num in range(1, seats_per_row + 1):
            seat = {
                "hallName": hall_name,
                "seatRow": chr(64 + row),  # Converts 1 to A, 2 to B, etc.
                "seatColumn": seat_num,
                "seatType": "Regular",
                "seatPrice": 12.99
            }
            seats.append(seat)

    # Generate seat data for the last row with remaining seats
    if remaining_seats:
        for seat_num in range(1, remaining_seats + 1):
            seat = {
                "hallName": hall_name,
                "seatRow": chr(64 + rows + 1),  # Next row
                "seatColumn": seat_num,
                "seatType": "Regular",
                "seatPrice": 12.99
            }
            seats.append(seat)

    return seats

# Populate cinemaHallSeats in the data
data = {
  "cinemaHalls": [
    {
      "name": "Hall 1",
      "totalSeats": 120
    },
    {
      "name": "Hall 2",
      "totalSeats": 90
    },
    {
      "name": "Hall 3",
      "totalSeats": 110
    },
    {
      "name": "Hall 4",
      "totalSeats": 80
    }
  ],
  "cinemaHallSeats": []
}

for hall in data['cinemaHalls']:
    data['cinemaHallSeats'].extend(generate_seats_for_hall(hall['name'], hall['totalSeats']))

# Save data to JSON
with open('lincoln_cinemas_data.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
