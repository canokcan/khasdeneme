import heapq
import random
import pandas as pd
from collections import deque

class Event: #Required attributes defined here
    def __init__(self, time, event_type, product, machine=None, operator=None):
        self.time = time
        self.event_type = event_type
        self.product = product
        self.machine = machine
        self.operator = operator
    
    def __lt__(self, other):
        return self.time < other.time

class Machine: #Machines have ID's process times and random failures assigned, also their status as busy or not
    def __init__(self, id, process_time, failure_rate):
        self.id = id
        self.process_time = process_time
        self.failure_rate = failure_rate
        self.is_busy = False
        self.maintenance_time = random.uniform(10, 30) #I assigned a random maintenance here for 10-30 mins

class Operator: #Workers assigned, busy or not
    def __init__(self, id):
        self.id = id
        self.is_busy = False

class Product: #Products initially raw materials
    def __init__(self, id):
        self.id = id
        self.state = 'raw_material'
        self.current_stage = 0

class Simulation:
    def __init__(self, num_machines, num_operators, shift_length, end_time):
        #Initializing the simulation here
        self.clock = 0
        self.event_queue = []
        #I used random times to complete a task, assuming that we are working on different model of car, skill of operator etc.
        self.machines = [Machine(i, random.uniform(5, 15), random.uniform(0.01, 0.05)) for i in range(num_machines)]
        self.operators = [Operator(i) for i in range(num_operators)]
        self.shift_length = shift_length
        self.product_queue = deque()
        self.processed_products = []
        self.end_time = end_time
        self.data = []
        self.waiting_products = deque()

    def schedule_event(self, event):
        #We are making a new event and adding it to the event queue
        heapq.heappush(self.event_queue, event)

    def run(self):
        #We are checking if we pass the total runtime, since we have a schedule 
        while self.clock < self.end_time:
            if self.event_queue:
                event = heapq.heappop(self.event_queue)
                self.clock = event.time
                self.process_event(event)
            else:
                break

    def process_event(self, event):
        #Events are here, start-end, and machine failures handled here
        if event.event_type == 'start_process':
            self.start_process(event.product)
        elif event.event_type == 'end_process':
            self.end_process(event.product, event.machine, event.operator)
        elif event.event_type == 'machine_failure':
            self.handle_machine_failure(event.machine)
        elif event.event_type == 'maintenance':
            self.perform_maintenance(event.machine)

    def start_process(self, product):
        #We can start processing a product if a machine and operator are available
        available_machine = next((m for m in self.machines if not m.is_busy), None)
        available_operator = next((o for o in self.operators if not o.is_busy), None)
        if available_machine and available_operator: #If we have both avaiable operator and machine we can start
            print(f"Starting process for Product {product.id} at time {self.clock} on Machine {available_machine.id} with Operator {available_operator.id}")
            available_machine.is_busy = True #Setting the used machine and operator taking the job as busy
            available_operator.is_busy = True
            product.state = 'processing'
            self.schedule_event(Event(self.clock + available_machine.process_time, 'end_process', product, available_machine, available_operator))
        else: #If requirements not met, we wait
            print(f"No available machine or operator for Product {product.id} at time {self.clock}")
            self.waiting_products.append(product)

    def end_process(self, product, machine, operator):
        #Here we end processing a product and check for next stage or completion
        print(f"Ending process for Product {product.id} at time {self.clock} on Machine {machine.id} with Operator {operator.id}")
        machine.is_busy = False
        operator.is_busy = False
        product.current_stage += 1
        if product.current_stage < 4: #Assuming we have 4 stages: machining, assembly, QC, packaging
            self.start_process(product) #Instead of writing each stage 1by1, I just did 4 seperate stages, when I tried otherwise, I printed several lines.
        else:
            product.state = 'finished'
            self.processed_products.append(product)
            self.data.append({'ProductID': product.id, 'CompletionTime': self.clock})
        
        #Checking if there are any waiting products
        if self.waiting_products:
            next_product = self.waiting_products.popleft()
            self.start_process(next_product)
        #Making random events here such as machine failures by rolling a dice basically
        if random.random() < machine.failure_rate:
            print(f"Machine {machine.id} failed at time {self.clock}")
            self.schedule_event(Event(self.clock, 'machine_failure', None, machine))

    def handle_machine_failure(self, machine):
        #Handling a machine failure event by scheduling maintenance
        print(f"Handling failure for Machine {machine.id} at time {self.clock}")
        machine.is_busy = True #Machine is stated as under maintenance
        self.schedule_event(Event(self.clock + machine.maintenance_time, 'maintenance', None, machine))

    def perform_maintenance(self, machine):
        #Performing maintenance on a machine and checking for waiting products
        print(f"Performing maintenance on Machine {machine.id} at time {self.clock}")
        machine.is_busy = False

        if self.waiting_products:
            next_product = self.waiting_products.popleft()
            self.start_process(next_product)

    def collect_data(self):
        #Collecting the information here
        return self.data

    def add_product(self, product):
        #Adding a product to the simulation and scheduling it
        self.product_queue.append(product)
        self.schedule_event(Event(self.clock, 'start_process', product))

#Parameters
num_machines = 3
num_operators = 10
shift_length = 8 * 60 #8 hours per shift
end_time = 24 * 60 #24 hours simulation, we end after 1440 minutes, no extra task taken after that minute

#Initializing Simulation
sim = Simulation(num_machines, num_operators, shift_length, end_time)

#Adding Products
for i in range(10): #Products to be included in a day, 1440 minutes. I assumed like we got "x" orders and try to complete that order
    sim.add_product(Product(i))

sim.run()

#Results
data = sim.collect_data()
df = pd.DataFrame(data)
print(df)
