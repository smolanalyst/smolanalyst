import os
import pandas as pd
from execution_context import ExecutionContext

df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

df.to_csv("../test.csv")
print("Successfully wrote to ../test.csv outside of secure context")

with ExecutionContext(os.getcwd()).secure_context():
    try:
        df.to_csv("../test.csv")
        print(
            "Test failed: writting outside cwd should not be allowed within secure context"
        )
    except ValueError as e:
        print(f"Successfully blocked write within secure context: {e}")
