# Example 1.
text = """
Pregnant persons with gestational diabetes are at increased risk for maternal and fetal complications, including preeclampsia, fetal macrosomia (which can cause shoulder dystocia and birth injury), and neonatal hypoglycemia .
"""

labels = "C C C C C O O E E E E E E E E E E E E E E E E E E E E E E O"


# Example 2.
text = """
Gestational diabetes has also been associated with an increased risk of several long-term health outcomes in pregnant persons and intermediate outcomes in their offspring .
"""

labels = "C C O O O O O O E E E E E E E E E E E E E E E E O"


# Example 3.
text = """
EVIDENCE ASSESSMENT The USPSTF concludes with moderate certainty that there is a moderate net benefit to screening for gestational diabetes at 24 weeks of gestation or after to improve maternal and fetal outcomes .
"""

labels = "O O O O O O O O O O O O S S S O C C C C C C C C C C C O E E E E E O"

text = text.split(" ")
labels = labels.split(" ")

print(text)
print(len(text))
print(labels)
print(len(labels))

for i in range(len(text)):
    print(text[i] + " - " + labels[i])