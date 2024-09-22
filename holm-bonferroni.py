alpha = 0.05  # significance level
p_values = [0.7405, 0.4259]  # p-values from the two t-tests
num_tests = len(p_values)

# Step 2: Rank the p-values
sorted_p_values = sorted(p_values)

# Step 4: Adjust the significance level and reject null hypotheses accordingly
for i, p_value in enumerate(sorted_p_values):
    adjusted_alpha = alpha / (num_tests - i)  # Adjust alpha based on remaining tests
    adjusted_p_value = p_value * num_tests  # Adjust p-value
    if adjusted_p_value <= adjusted_alpha:
        print(f"Reject null hypothesis for t-test {i+1} (adjusted p-value: {adjusted_p_value}) "
              f" with adjusted alpha: {adjusted_alpha}")
    else:
        print(f"No significant difference for t-test {i+1} (adjusted p-value: {adjusted_p_value})"
              f" with adjusted alpha: {adjusted_alpha}")