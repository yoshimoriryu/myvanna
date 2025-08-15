from training_data import ddl, docs, sql
from main import vn

# Training section =======================
print("Starting training...")

# Train with DDL statements
if ddl.ddl_statements:
    print("\nAdding DDL statements...")
    for ddl_statement in ddl.ddl_statements:
        vn.add_ddl(ddl_statement)
    print(f"Successfully added {len(ddl.ddl_statements)} DDL statements.")

# Train with documentation
if docs.documentation_texts:
    print("\nAdding documentation...")
    for doc_text in docs.documentation_texts:
        vn.add_documentation(doc_text)
    print(f"Successfully added {len(docs.documentation_texts)} documentation texts.")

# Train with SQL pairs
if sql.training_pairs:
    print("\nAdding SQL training pairs...")
    for pair in sql.training_pairs:
        vn.add_question_sql(question=pair['question'], sql=pair['sql'])
    print(f"Successfully added {len(sql.training_pairs)} SQL training pairs.")

print("\nTraining complete.")

# Verify training data
try:
    training_data = vn.get_training_data()
    print("\n--- Current Training Data ---")
    if not training_data.empty:
        print(training_data)
    else:
        print("No training data found.")
    print("---------------------------\n")
except Exception as e:
    print(f"An error occurred while fetching training data: {e}")
