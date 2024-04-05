#In this simulation model, below 2 tasks are also implemented.
# 1. 10-year interval required for re-election attempts for Consuls. 
# 2. Additional penalty for re-electing a Consul within 10 years: -10 PSI.
# My logic was that is that firstly, Consuls are required to take a 10 year break after their term, however, 
# if there are no avaiable candidates for Consuls, they can be elected. If that happens, we reduce 10 points in PSI.
# Since if there were a 10 year break to be applied after you first term as Consul, how can PSI be reduced by 10 ever?
# That logical problem was what kept me confused initially. This is how I tried to handle the case.
# This is the second version.

import numpy as np
import random
# Fixed Parameters
expectancy_mean = 55
expectancy_std = 10
expectancy_min = 25
expectancy_max = 80
new_mean = 15
new_std = 5

#Requirements for age and service
service_req = {
    "Quaestor": {"min_age": 30, "min_service": 0},
    "Aedile": {"min_age": 36, "min_service": 2, "previous_office": "Quaestor"},
    "Praetor": {"min_age": 39, "min_service": 2, "previous_office": "Aedile"},
    "Consul": {"min_age": 42, "min_service": 2, "previous_office": "Praetor"},
}

#Initial Political Stability Index PSI
PSI = 100

#Class for politicians
class Politician:
    id_counter = 1  #ID for naming different politicians
    
    def __init__(self, year_added):
        self.name = f"Politician_{Politician.id_counter}" #Naming politicians based on their ID
        self.age = np.random.randint(expectancy_min, expectancy_max + 1) #I used this formula to generate random ages, since there were no statements about it
        self.life_expectancy = max(self.age + 1, min(np.random.normal(expectancy_mean, expectancy_std), expectancy_max))
        self.years_of_service = 0
        self.position = None  #Starting with no position
        self.year_added = year_added  #Tracking the year the politician was added to our total politicians generated pool
        self.office_history = {}
        Politician.id_counter += 1 #We increase the id after each creation of politician to make them unique

    def elected_to_office(self, office, year):
        if office in self.office_history:
            self.office_history[office].append(year)
        else:
            self.office_history[office] = [year]
        
    def __repr__(self): #This was used during initial testing to see if creation is successful or not
        return f"{self.name}: Age {self.age}, Life Expectancy {self.life_expectancy}, Years of Service {self.years_of_service}, Position {self.position}"

politician_pool = [] #Our empty pool of politicians at start

def initial_politicians():
    initial_year = 1 #We are starting from 1st year

    #Filling the office for first year, fitting the requirements asked for task, they can be adjusted
    office_avaiable_places = {"Quaestor": 20, "Aedile": 10, "Praetor": 8, "Consul": 2}
    for office, count in office_avaiable_places.items(): #Filling the places based on their avaiable number
        for _ in range(count):
            #Passing the initial_year as an argument
            politician = Politician(year_added=initial_year) #Declaring their initial year_added value to 1
            politician.age = service_req[office]['min_age'] #They start at min required age for that place
            politician.position = office #Their current positions are declared
            #Adjusting life expectancy to ensure it's  above the current age
            politician.life_expectancy = np.clip(np.random.normal(expectancy_mean, expectancy_std), politician.age + 1, expectancy_max)
            politician_pool.append(politician) #Finally pushing them into our array of politicians

# Update the annual_influx_of_candidates function to pass the current year
def annual_influx_of_candidates(current_year):
    new_candidates_count = int(np.round(np.random.normal(new_mean, new_std)))
    new_candidates_count = max(new_candidates_count, 0)  # Ensure non-negative
    for _ in range(new_candidates_count):
        new_politician = Politician(current_year)
        politician_pool.append(new_politician)

#We are checking aging and life expectancy here
def age_life():
    global politician_pool
    politician_pool = [p for p in politician_pool if p.age < p.life_expectancy] #Checking if they are still living
    for p in politician_pool: #Incrementing their age and years served if they are in a position
        p.age += 1
        if p.position is not None:
            p.years_of_service += 1
        else:
            p.years_of_service += 0

#We are filling the empty positions here
def fill_empty(current_year):
    global PSI
    ordered_positions = ["Consul", "Praetor", "Aedile", "Quaestor"]
    positions_and_numbers = {"Quaestor": 20, "Aedile": 10, "Praetor": 8, "Consul": 2}

    #We are resetting empty positions here
    for office in positions_and_numbers:
        positions_and_numbers[office] -= sum(1 for p in politician_pool if p.position == office)

    #We are re selecting politicians to empty places here, from highest office first
    for office in ordered_positions:
        if office == "Consul":
            #First, we try to find eligible candidates who have not served as Consul in the last 10 years
            available_politicians = [p for p in politician_pool if p.position is None and eligible_for_consul(p, current_year) and p.age >= service_req[office]['min_age']]
            if not available_politicians:  #If no eligible candidates are found, we continue
                #Here, we consider all candidates, not caring about 10 year rule
                available_politicians = [p for p in politician_pool if p.position is None and p.age >= service_req[office]['min_age']]
                #Since we're not applying the 10-year rule due to a lack of candidates, we decrease PSI by 10
                PSI -= 10
        else:
            #This is for other offices, since they do not have a 10 year rule, similar to first implementation
            available_politicians = [p for p in politician_pool if p.position is None and p.age >= service_req[office]['min_age']]
        
        for _ in range(positions_and_numbers[office]):
            if available_politicians:
                elected = random.choice(available_politicians) #Selecting them randomly as stated
                elected.position = office #Assigning their new place
                elected.elected_to_office(office, current_year)
                available_politicians.remove(elected)
            else:
                PSI -= 5  #We have a -5 penalty if a place is not filled


#New function to check eligibility for Consuls for the 10 year rule
def eligible_for_consul(politician, current_year):
    #We are checking their previous served year if there is any here
    history = politician.office_history.get("Consul", [])
    return all(current_year - year >= 10 for year in history)


initial_politicians()  #I am calling this function to initially fill the office before our simulation starts
fill_rate_tracker = {office: [] for office in service_req} #We are using this to track fill rates

#This function calculates fill rates, we can call it within simulate_year function when we are running the simulation
def calculate_fill_rates():
    for office, requirements in service_req.items():
        filled_positions = sum(p.position == office for p in politician_pool)
        total_positions = {"Quaestor": 20, "Aedile": 10, "Praetor": 8, "Consul": 2}[office]
        fill_rate = filled_positions / total_positions
        fill_rate_tracker[office].append(fill_rate * 100)  #Finally, we are converting them to a percentage rate

def simulate_year(current_year): #Simulating each year with current_year variable as our input, we are calling required functions here to simulate
    global PSI, politician_pool  #Declaring PSI and politician_pool as global so that we can reach/call them with no problem
    age_life()
    annual_influx_of_candidates(current_year)
    fill_empty(current_year)
    calculate_fill_rates()
    #Finally, we are setting the politician pool in the end
    politician_pool = [p for p in politician_pool if p.year_added < current_year or (p.year_added == current_year and p.position == "Quaestor") or p.position is not None]

years_to_simulate = 200  #We can adjust the simulation years here
for year in range(1, years_to_simulate + 1): #We are calling the simulate_year function for each year
    simulate_year(year)

#Below here, we are printing the required information for this task
#Calculating average annual fill rate
average_fill_rates = {office: sum(rates) / len(rates) for office, rates in fill_rate_tracker.items()}

#Age distribution for offices are calculated here
age_distribution = {office: [] for office in service_req}
for p in politician_pool:
    if p.position:
        age_distribution[p.position].append(p.age)

#Printing out all the requested information in project here
print(f"End-of-Simulation PSI: {PSI}")
print("Annual Fill Rate:")
for office, rate in average_fill_rates.items():
    print(f"  {office}: {rate:.2f}%")
print("Age Distribution:")
for office, ages in age_distribution.items():
    if ages:
        print(f"  {office}: Mean Age = {np.mean(ages):.2f}, Std Dev = {np.std(ages):.2f}, Min = {np.min(ages)}, Max = {np.max(ages)}")
    else:
        print(f"  {office}: No politicians")
