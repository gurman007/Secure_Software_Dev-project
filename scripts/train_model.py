import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

# --- 1. Load and Prepare the Data ---

# Define the path to your CSV file
csv_path = 'results/klee_features_rich_gurman.csv'

try:
    # Load the dataset using pandas
    df = pd.read_csv(csv_path)
    print(" Successfully loaded the dataset.")
    print(f"Original shape of the dataset: {df.shape}")
except FileNotFoundError:
    print(f" ERROR: Could not find the file at {csv_path}")
    print("Please make sure the script is in your 'SS PROJECT' directory.")
    exit()

# --- 2. Clean the Data ---

# The model can only learn from clear 'good' (0) and 'bad' (1) examples.
# We must remove the rows where the label is -1 (unknown).
df_cleaned = df[df['label'] != -1].copy()

# If after cleaning no data is left, we can't proceed.
if df_cleaned.empty:
    print(" ERROR: After cleaning, no data with labels 0 or 1 was found.")
    print("Please check your feature extraction script and CSV file.")
    exit()

print(f"Shape after removing unknown labels (-1): {df_cleaned.shape}")
print("\nValue counts of labels:")
print(df_cleaned['label'].value_counts())


# --- 3. Define Features (X) and Target (y) ---

# These are the features we will use to train the model.
# Notice we are using ALL the numeric data KLEE produced.
feature_columns = [
    "Instructions", "FullBranches", "PartialBranches", "NumBranches",
    "SolverQueries", "NumQueryConstructs", "CoveredInstructions",
    "UncoveredInstructions", "UserTime", "Allocations", "ExternalCalls", "warnings"
]

X = df_cleaned[feature_columns] # The features (input)
y = df_cleaned['label']         # The target (what we want to predict)


# --- 4. Split Data into Training and Testing Sets ---

# We train the model on 80% of the data and test its performance on the unseen 20%.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set size: {X_train.shape[0]} samples")
print(f"Testing set size: {X_test.shape[0]} samples")


# --- 5. Train the Decision Tree Model ---

# Initialize the classifier
# random_state makes the result reproducible
model = DecisionTreeClassifier(random_state=42)

# Train the model on the training data
model.fit(X_train, y_train)

print("\n Model training complete.")


# --- 6. Evaluate the Model ---

# Make predictions on the test data
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\n--- MODEL EVALUATION RESULTS ---")
print(f" Accuracy: {accuracy * 100:.2f}%")
print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Class 0 (Good)', 'Class 1 (Bad)']))