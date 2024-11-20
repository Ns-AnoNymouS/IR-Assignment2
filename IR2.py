import os
import re
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet


# Function to generate precision-recall table and curve
def generate_precision_recall_curve(
    relevant_items, k, file_name="Precision-Recall_Curve.png", rank_list=1
):
    total_relevant = len(relevant_items)
    relevant_retrieved = 0

    # Precision and Recall lists for plotting
    precision = []
    recall = []
    table_content = [["Retrieved", "Relevance", "Precision", "Recall"]]

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
        table_content.append(
            [
                retrieved,
                "Relevant" if is_relevant else "Not Relevant",
                f"{relevant_retrieved}/{retrieved} = {current_precision:.2f}",
                f"{relevant_retrieved}/{total_relevant} = {current_recall:.2f}",
            ]
        )

    # Plot Precision-Recall curve
    plt.figure(figsize=(8, 6))
    plt.plot(
        recall, precision, marker="o", color="blue", label="Precision-Recall Curve"
    )
    plt.xlim(0, 1.01)
    plt.ylim(0, 1.01)
    ticks = np.arange(0.0, 1.1, 0.1)
    plt.xticks(ticks)
    plt.yticks(ticks)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(f"Precision-Recall Curve for Ranked List - {rank_list}")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(file_name)
    plt.close()

    return file_name, table_content


# Function to generate ROC curve
def receiver_operating_characteristic_curve(positive, k, file_name="ROC_Curve.png", rank_list=1):
    total_tp = len(positive)
    total_fp = k - total_tp
    tp = 0
    fp = 0
    x = []
    y = []

    table_content = [["Rank", "True Positive Rate (TPR)", "False Positive Rate (FPR)"]]

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
        table_content.append(
            [i, f"{tp}/{total_tp} = {tp_i:.2f}", f"{fp}/{total_fp} = {fp_i:.2f}"]
        )

    # Plotting the ROC curve
    plt.figure(figsize=(8, 6))
    plt.scatter(
        x, y, color="blue", label="Data Points", s=60, edgecolors="black", alpha=0.7
    )
    plt.plot(x, y, color="red", label="ROC Curve", linewidth=2)
    plt.xlim(0, 1.01)
    plt.ylim(0, 1.01)
    ticks = np.arange(0.0, 1.1, 0.1)
    plt.xticks(ticks)
    plt.yticks(ticks)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.xlabel("False Positive Rate (FPR)", fontsize=12)
    plt.ylabel("True Positive Rate (TPR)", fontsize=12)
    plt.title(f"ROC Curve for Ranked List - {rank_list}", fontsize=14)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(file_name)
    plt.close()
    return file_name, table_content


# Function to create the PDF report
def style_table(table):
    table.setStyle(
        TableStyle(
            [
                # Header row styling
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.darkblue,
                ),  # Dark blue background for header
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke,
                ),  # White text for header
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Center-align all content
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),  # Bold font for header
                ("FONTSIZE", (0, 0), (-1, 0), 12),  # Font size for header
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),  # Padding for header
                # Row background colors (zebra striping effect)
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.beige,
                ),  # Light beige for rows
                ("GRID", (0, 0), (-1, -1), 1, colors.grey),  # Grey grid lines
                (
                    "LINEABOVE",
                    (0, 1),
                    (-1, 1),
                    0.5,
                    colors.black,
                ),  # Thin line above data rows
                (
                    "LINEBELOW",
                    (0, 0),
                    (-1, 0),
                    0.5,
                    colors.black,
                ),  # Thin line below header row
                # Additional cell padding
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),  # Increase cell padding for better readability
                # Row highlight on hover (use in interactive PDFs or when presenting in GUI)
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.whitesmoke,
                ),  # Pale background for rows
                (
                    "TEXTCOLOR",
                    (0, 1),
                    (-1, -1),
                    colors.black,
                ),  # Black text for rows
            ]
        )
    )


def create_pdf(file_name, name, roll_number, images, tables):
    # Create a PDF document
    doc = SimpleDocTemplate(file_name, pagesize=letter)

    # Prepare styles
    styles = getSampleStyleSheet()

    # Create flowables list
    elements = []

    def header(canvas, doc):
        canvas.setFont("Helvetica", 10)
        canvas.drawString(450, 750, f"Name: {name}")
        canvas.drawString(450, 735, f"Roll Number: {roll_number}")
        canvas.drawString(450, 720, f"Page {doc.page}")

    doc.build(elements, onFirstPage=header, onLaterPages=header)

    elements.append(Paragraph("<b>Assignment - 2</b>", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            "a) Generate Two Ranked lists  and compute Precision and Recall for both these lists.",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 12))

    centered_style = styles["Normal"].clone("CenteredStyle")  # Clone the existing style
    centered_style.alignment = 1

    for i in range(2):
        elements.append(Spacer(1, 12))
        table = Table(tables[i])
        style_table(table)
        elements.append(table)
        elements.append(Spacer(1, 12))
        elements.append(
            Paragraph(
                f"Precision and Recall Table for Ranked List - {i+1}", centered_style
            )
        )

        elements.append(PageBreak())

    elements.append(
        Paragraph(
            "b) Draw the Precision-Recall curve for each ranked list.",
            styles["Normal"],
        )
    )
    elements.append(Spacer(1, 12))
    # Add Precision-Recall and ROC images
    for index, image in enumerate(images):
        img = Image(image, width=6 * inch, height=4 * inch)

        elements.append(img)
        elements.append(Spacer(1, 12))
        if index == 1:
            elements.append(PageBreak())
            elements.append(
                Paragraph(
                    "c) Draw the Receiver-Operating-Characteristic for each ranked list.",
                    styles["Normal"],
                )
            )

    # Build the document
    doc.build(elements)


# Inputs from the user
name = input("Enter your name: ")
roll_no = input("Enter your roll number: ")
last_three_digits = roll_no[-3:]
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
print("Generating Precision-Recall Curves and ROC Curves...")
images = []
tables = []

# Generate and save precision-recall curves
print("\tGenerating Precision-Recall Curve for List 1")
image, table = generate_precision_recall_curve(
    list1, topk, "Precision-Recall_Curve_1.png", rank_list=1
)
images.append(image)
tables.append(table)

print("\tGenerating Precision-Recall Curve for List 2")
image, table = generate_precision_recall_curve(
    list2, topk, "Precision-Recall_Curve_2.png", rank_list=2
)
images.append(image)
tables.append(table)

# Generate and save ROC curves
print("\tGenerating ROC Curve for List 1")
image, table = receiver_operating_characteristic_curve(list1, topk, "ROC_Curve_1.png", rank_list=1)
images.append(image)
tables.append(table)

print("\tGenerating ROC Curve for List 2")
image, table = receiver_operating_characteristic_curve(list2, topk, "ROC_Curve_2.png", rank_list=2)
images.append(image)
tables.append(table)

# Create the PDF report
create_pdf(
    "IR-Assign02-{}.pdf".format(roll_no[-4:]),
    name,
    roll_no,
    images,
    tables
)

for image in images:
    try:
        os.remove(image)
    except FileNotFoundError:
        pass