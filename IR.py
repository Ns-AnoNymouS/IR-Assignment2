import re
import subprocess
import numpy as np
import matplotlib.pyplot as plt


# Function to generate precision-recall table and curve
def generate_precision_recall_curve(
    relevant_items, k, file_name="Precision-Recall_Curve.png"
):
    total_relevant = len(relevant_items)
    relevant_retrieved = 0

    # Precision and Recall lists for plotting
    precision = []
    recall = []

    # Print table header
    header = f"\t| {'Retrieved':^10} | {'Relevance':^12} | {'Precision':^13} | {'Recall':^13} |"
    separator = "\t" + "-" * (len(header) - 1)
    print(separator)
    print(header)
    print(separator)

    # Calculate precision and recall for each retrieval step
    for retrieved in range(1, k + 1):
        is_relevant = retrieved in relevant_items
        if is_relevant:
            relevant_retrieved += 1

        # Calculate precision and recall
        current_precision = relevant_retrieved / retrieved
        current_recall = relevant_retrieved / total_relevant

        # Store values for plotting
        precision.append(current_precision)
        recall.append(current_recall)

        # Determine relevance description
        relevance_description = "Relevant" if is_relevant else "Not Relevant"

        # Print row in table format
        row = f"\t| {retrieved:^10} | {relevance_description:^12} | {relevant_retrieved}/{retrieved:^2} = {current_precision:>6.2f} | {relevant_retrieved}/{total_relevant:^2} = {current_recall:>6.2f} |"
        print(row)

    # Print table footer
    print(separator)

    # Plot Precision-Recall curve
    plt.figure(figsize=(8, 6))
    plt.plot(
        recall, precision, marker="o", color="blue", label="Precision-Recall Curve"
    )

    # Set axis limits and ticks
    plt.xlim(0, 1.01)
    plt.ylim(0, 1.01)
    ticks = np.arange(0.0, 1.1, 0.1)
    plt.xticks(ticks)
    plt.yticks(ticks)

    # Add labels, title, and legend
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()

    # Save the plot
    plt.tight_layout()  # Ensure everything fits without overlap
    plt.savefig(file_name)
    plt.close()


def receiver_operating_characteristic_curve(positive, k, file_name="ROC_Curve.png"):
    total_tp = len(positive)
    total_fp = k - total_tp
    tp = 0
    fp = 0
    x = []
    y = []

    # Output header
    header = f"\t| {'Rank':^9} | {'TP':^15} | {'FP':^14} |"
    separator = "\t" + "-" * (len(header) - 1)
    print(separator)
    print(header)
    print(separator)

    # Calculate True Positive and False Positive rates
    for i in range(1, k + 1):
        if i in positive:
            tp += 1
        else:
            fp += 1
        tp_i = tp / total_tp
        fp_i = fp / total_fp
        x.append(fp_i)
        y.append(tp_i)

        # Print results
        print(
            f"\t|{i:<10} | {tp:>2}/{total_tp:<2} = {round(tp_i, 2):<5}   |   {fp:>2}/{total_fp:<2} = {round(fp_i, 2):<5}|"
        )

    # Output footer
    print(separator)
    
    # Plotting the Precision-Recall curve
    plt.figure(figsize=(8, 6))

    # Plot the scatter points and the connecting line
    plt.scatter(
        x, y, color="blue", label="Data Points", s=60, edgecolors="black", alpha=0.7
    )
    plt.plot(x, y, color="red", label="Precision-Recall Curve", linewidth=2)

    # Set axis limits and ticks
    plt.xlim(0, 1.01)
    plt.ylim(0, 1.01)

    # Set custom ticks for both axes
    ticks = np.arange(0.0, 1.1, 0.1)
    plt.xticks(ticks)
    plt.yticks(ticks)

    # Add grid for better visibility
    plt.grid(True, linestyle="--", alpha=0.7)

    # Add labels, title, and legend
    plt.xlabel("False Positive Rate (FPR)", fontsize=12)
    plt.ylabel("True Positive Rate (TPR)", fontsize=12)
    plt.title("Precision-Recall Curve", fontsize=14)
    plt.legend(loc="lower right")

    # Show the plot
    plt.tight_layout()  # Ensure everything fits without overlap
    plt.savefig(file_name)
    plt.close()


# Inputs from the user
last_three_digits = input("Enter the last 3 digits of your roll number: ")
file_path = input(
    "Enter the file path of the InfoRetireval.jar file (press Enter if in the current directory): "
)

if not file_path:
    file_path = "InfoRetireval.jar"

try:
    # Run the Java program and capture its output
    result = subprocess.run(
        [
            "java",
            "-cp",
            file_path,
            "in.ac.iiits.ir.data.GenerateRankedList",
            last_three_digits,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    # Get the output from the Java program
    data = result.stdout

    # Parse lists and TopK from the output
    list1_match = re.search(r"List 1: \[([0-9, ]+)\]", data)
    list2_match = re.search(r"List 2: \[([0-9, ]+)\]", data)
    topk_match = re.search(r"Your TopK = (\d+)", data)

    if list1_match and list2_match and topk_match:
        list1 = [int(x) for x in list1_match.group(1).split(",")]
        list2 = [int(x) for x in list2_match.group(1).split(",")]
        topk = int(topk_match.group(1))
    else:
        raise ValueError("Failed to extract lists or TopK from output.")

except Exception as e:
    print(f"Error: {e}")
    # Manual input in case of failure
    topk = int(input("Enter TopK: "))
    list1 = [
        int(x)
        for x in re.sub(
            r"[^\d,]", "", input("Enter relevance List 1 (comma-separated): ")
        ).split(",")
    ]
    list2 = [
        int(x)
        for x in re.sub(
            r"[^\d,]", "", input("Enter relevance List 2 (comma-separated): ")
        ).split(",")
    ]

# Generate precision-recall tables and plots
print()
print(data)
print()
print(
    "a) Generate Two Ranked lists  and compute Precision and Recall for both these lists."
)
print()
print("\tPrecision-Recall Table for Ranked List 1:")
generate_precision_recall_curve(list1, topk, "Precision-Recall_Curve_1.png")

print()
print("\tPrecision-Recall Table for Ranked List 2:")
generate_precision_recall_curve(list2, topk, "Precision-Recall_Curve_2.png")

print()
print(
    "b) Draw the Precision-Recall curve for each ranked list"
)
print(
    "\tPrecision-Recall curves saved as 'Precision-Recall_Curve_1.png' and 'Precision-Recall_Curve_2.png'."
)

print()
print(
    "c) Draw the Receiver-Operating-Characteristic for each ranked list"
)
print()
print("\tReceiver-Operating-Characteristic for Ranked List 1:")
receiver_operating_characteristic_curve(list1, topk, "ROC_Curve_1.png")

print()
print("\tReceiver-Operating-Characteristic for Ranked List 2:")
receiver_operating_characteristic_curve(list2, topk, "ROC_Curve_2.png")