import random

X_MIN, X_MAX = 0, 100  
Y_MIN, Y_MAX = 0, 2000  
TARGET_X = 42
TARGET_Y_THRESHOLD = 1000
NUM_ITERATIONS = 10000  

success_count = 0
total_attempts = 0

# Attack simulation
for _ in range(NUM_ITERATIONS):
    x = random.randint(X_MIN, X_MAX)  
    y = random.randint(Y_MIN, Y_MAX)  
    
    if x == TARGET_X and y > TARGET_Y_THRESHOLD:
        success_count += 1

    total_attempts += 1

# Probability of success
success_probability = success_count / total_attempts

# Display results
print(f"Total attempts: {total_attempts}")
print(f"Successful attacks: {success_count}")
print(f"Probability of success: {success_probability:.6f}")
