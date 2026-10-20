import repository

try:
    order_id = repository.place_order(1, [(11, 1)])
    print("Order placed: ", order_id)
except repository.InsufficientStock as e:
    print("Failed: ",e)