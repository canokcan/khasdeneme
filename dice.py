import random
import heapq

priorityQ = []
rolls = [random.randint(1, 6) for i in range(10)]

for i in rolls:
    heapq.heappush(priorityQ, i)

removedQ = [heapq.heappop(priorityQ) for i in range(5)] #I removed the min ones, I looked it up to double check,
                                                        #heapq.heappop is min-heap, it removes low value elements

print("İnitial Rolls:", rolls)
print("Final Priority Queue:", priorityQ)
print("Removed items:", removedQ)
