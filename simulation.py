import simpy
import random

# Parameters
M = 5  # Number of consumers
N = 3  # Number of producers
SIMULATION_TIME = 50  # Simulation time in time units

# Market parameters
MAX_PRICE = 100  # Maximum price for the product
INITIAL_PRICE = random.randint(1, MAX_PRICE)  # Initial price for the product

# Economic parameters
PRICE_CHANGE_FACTOR = 1  # Factor controlling price change rate
DEMAND_SLOPE = 1  # Slope of demand function (negative for decreasing)
SUPPLY_SLOPE = 0.5 # Slope of supply function (positive for increasing)
TOTAL_SUPPLY = 0  # Initial supply of the product


class Consumer:
    def __init__(self, env, consumer_id, demand_slope):
        self.env = env
        self.consumer_id = consumer_id
        self.demand_slope = demand_slope

    def demand_function(self, price):
        return max(0, int(MAX_PRICE - self.demand_slope * price + random.randint(-MAX_PRICE/10, MAX_PRICE/10)))  # Linearly decreasing demand

    def buy_product(self):
        global TOTAL_SUPPLY
        while True:
            if TOTAL_SUPPLY > 0 and random.random() < 0.1:  # Randomly decide to buy the product when supply is available
                demand = self.demand_function(self.env.price)  # Ensure demand is an integer
                if demand > 0:
                    quantity_to_buy = min(demand, TOTAL_SUPPLY)  # Ensure not to buy more than available supply
                    TOTAL_SUPPLY -= quantity_to_buy  # Deduct the bought quantity from total supply
                    print(f"{self.env.now}: Consumer-{self.consumer_id} buys {quantity_to_buy} units of the product at price {self.env.price}", end=". ")
                    print(f"Total supply: {TOTAL_SUPPLY + quantity_to_buy} - {quantity_to_buy} = {TOTAL_SUPPLY}")
            yield self.env.timeout(1)  # Wait for next action


class Producer:
    def __init__(self, env, producer_id, supply_slope):
        self.env = env
        self.producer_id = producer_id
        self.supply_slope = supply_slope

    def supply_function(self, price):
        return max(0, int(self.supply_slope * price + random.randint(-MAX_PRICE/10, MAX_PRICE/10)))  # Linearly increasing supply

    def produce_product(self):
        global TOTAL_SUPPLY
        while True:
            supply = self.supply_function(self.env.price)  # Ensure supply is an integer
            TOTAL_SUPPLY += supply  # Increase total supply
            if supply > 0:
                print(f"{self.env.now}: Producer-{self.producer_id} supplies {supply} units of the product at price {self.env.price}", end=". ")
                print(f"Total supply: {TOTAL_SUPPLY - supply} + {supply} = {TOTAL_SUPPLY}")
            yield self.env.timeout(1)  # Time taken to produce


class Market(simpy.Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = INITIAL_PRICE

    def update_price(self):
        while True:
            if TOTAL_SUPPLY > 100:
                self.price -= PRICE_CHANGE_FACTOR
            elif TOTAL_SUPPLY < 25:
                self.price += PRICE_CHANGE_FACTOR
            if self.price < 1:
                self.price = 1
            print(f"{self.now}: Price = {self.price}")
            yield self.timeout(1)


def main():
    env = Market()

    # Create consumers
    consumers = []
    for i in range(1, M+1):
        consumer = Consumer(env, i, DEMAND_SLOPE)
        consumers.append(consumer)
        env.process(consumer.buy_product())

    # Create producers
    producers = []
    for i in range(1, N+1):
        producer = Producer(env, i, SUPPLY_SLOPE)
        producers.append(producer)
        env.process(producer.produce_product())

    # Run simulation
    env.process(env.update_price())
    env.run(until=SIMULATION_TIME)


if __name__ == '__main__':
    main()
