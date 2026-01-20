# Beginner Python & PySpark Interview Questions
*Entry Level*

A guide for beginners focusing on core DataFrame concepts in Pandas and PySpark, illustrating the transition from single-machine to distributed data processing.

---

## Table of Contents
1. [Pandas Basics (Single Machine)](#pandas-basics)
2. [PySpark Basics (Distributed)](#pyspark-basics)
3. [Key Concepts & Differences](#key-concepts--differences)
4. [Common Coding Scenarios](#common-coding-scenarios)
5. [Additional PySpark Questions](#additional-pyspark-questions)

---

## Pandas Basics

### 1. Reading and Inspecting Data
**Q:** How do you read a CSV file in Pandas and check the first 5 rows?
**A:**
```python
import pandas as pd

# Read CSV
df = pd.read_csv('data.csv')

# View first 5 rows
print(df.head())

# Check data types and non-null counts
print(df.info())
```

### 2. Selecting and Filtering
**Q:** How do you select specific columns and filter rows based on a condition?
**A:**
```python
# Select single column (returns Series)
names = df['Name']

# Select multiple columns (returns DataFrame)
subset = df[['Name', 'Age']]

# Filter: People older than 25
adults = df[df['Age'] > 25]

# Filter: Multiple conditions (AND=&, OR=|)
# Note: Parentheses are mandatory!
target = df[(df['Age'] > 25) & (df['Department'] == 'IT')]
```

### 3. Handling Missing Data
**Q:** How do you handle null/missing values in Pandas?
**A:**
1.  **Check for nulls:** `df.isnull().sum()`
2.  **Drop rows with nulls:** `df.dropna()`
3.  **Fill nulls:** `df.fillna(0)` or `df['Age'].fillna(df['Age'].mean())`

### 4. GroupBy and Aggregation
**Q:** Calculate the average salary per department.
**A:**
```python
# Group by 'Department' and calculate mean of 'Salary'
avg_salary = df.groupby('Department')['Salary'].mean()

# Multiple aggregations
summary = df.groupby('Department').agg({
    'Salary': ['min', 'max', 'mean'],
    'Age': 'mean'
})
```

---

## PySpark Basics

### 5. SparkSession
**Q:** What is a `SparkSession`?
**A:**
It is the entry point to programming Spark with the Dataset and DataFrame API. You need it to create DataFrames.
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("BeginnerApp").getOrCreate()
```

### 6. PySpark DataFrame Operations
**Q:** How do you perform basic selection and filtering in PySpark?
**A:**
In PySpark, operations are methods chained together.
```python
# Read
df = spark.read.csv("data.csv", header=True, inferSchema=True)

# Select
df_subset = df.select("Name", "Age")

# Filter (can use SQL-like string or Column conditions)
df_adults = df.filter("Age > 25")
# OR
from pyspark.sql.functions import col
df_adults = df.filter(col("Age") > 25)

# Adding a new column (Transformation)
df_new = df.withColumn("Age_in_10_Years", col("Age") + 10)

# Renaming a column
df_renamed = df.withColumnRenamed("Name", "Full_Name")
```

### 7. Actions vs Transformations
**Q:** What is the difference between `df.select()` and `df.count()`?
**A:**
*   **Transformation (`select`, `filter`, `withColumn`):** Lazy. It just builds a "recipe" (execution plan) but executes nothing. Returns a new DataFrame.
*   **Action (`count`, `show`, `collect`, `write`):** Triggers the actual computation. Spark looks at the recipe, optimizes it, and runs it.

---

## Key Concepts & Differences

### 8. Pandas vs PySpark
**Q:** When should you use PySpark over Pandas?
**A:**
| Feature | Pandas | PySpark |
|---------|--------|---------|
| **Data Size** | Small/Medium (Must fit in RAM) | Huge (Terabytes/Petabytes) |
| **Architecture** | Single Machine | Distributed (Cluster of machines) |
| **Execution** | Eager (Runs immediately) | Lazy (Runs only when triggered) |
| **Memory** | Can error with "Out of Memory" | Spills to disk if RAM is full |

### 9. Lazy Evaluation
**Q:** Why is Lazy Evaluation useful?
**A:**
It allows Spark to **optimize** the query before running it.
*Example:* If you load a 1TB file, filter it to 10 rows, and then select columns, Spark notices this. It pushes the filter down to the read source (CSV/Parquet) and only reads the relevant rows instead of loading the whole 1TB into memory first.

---

## Common Coding Scenarios

### 10. Distinct Counts
**Q:** Count the number of unique departments.
**Pandas:**
```python
count = df['Department'].nunique()
```
**PySpark:**
```python
from pyspark.sql.functions import countDistinct
df.select(countDistinct("Department")).show()
```

### 11. Sorting
**Q:** Sort data by Age in descending order.
**Pandas:**
```python
df.sort_values(by='Age', ascending=False)
```
**PySpark:**
```python
from pyspark.sql.functions import desc
df.orderBy(desc("Age")).show()
```

---

## Additional PySpark Questions

### 12. Schema Definitions (StructType)
**Q:** How do you strictly define a schema instead of using `inferSchema`?
**A:**
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("Name", StringType(), True),
    StructField("Age", IntegerType(), True)
])

df = spark.read.schema(schema).csv("data.csv")
```
*Why?* It is faster (no reading file to guess types) and safer (prevents type errors).

### 13. Data Types Check
**Q:** How do you check column types in PySpark?
**A:**
*   `df.printSchema()`: Prints a tree structure.
*   `df.dtypes`: Returns a list of tuples `[('Name', 'string'), ('Age', 'int')]`.

### 14. Dropping Columns
**Q:** How do you remove a column?
**A:**
```python
df_dropped = df.drop("ColumnName")
```

### 15. Handling Duplicates
**Q:** How do you remove duplicate rows?
**A:**
```python
# Remove fully duplicate rows
df_unique = df.dropDuplicates()

# Remove duplicates based on specific columns (keep first occurrence)
df_unique_names = df.dropDuplicates(["Name"])
```

### 16. Filling Nulls
**Q:** How do you replace null values?
**A:**
```python
# Replace all nulls with 0
df.na.fill(0)

# Replace nulls in specific columns
df.na.fill({"Name": "Unknown", "Age": 0})
```

### 17. Dropping Rows with Nulls
**Q:** How do you drop rows containing null values?
**A:**
```python
# Drop row if ANY column is null
df.na.drop(how="any")

# Drop row if ALL columns are null
df.na.drop(how="all")
```

### 18. Literal Values
**Q:** How do you add a static value column (e.g., Country="USA")?
**A:**
You must use the `lit` function. pure strings are interpreted as column names.
```python
from pyspark.sql.functions import lit
df = df.withColumn("Country", lit("USA"))
```

### 19. Column Aliasing
**Q:** How do you rename a column during selection?
**A:**
```python
df.select(col("Name").alias("Full_Name"))
```

### 20. Type Casting
**Q:** How do you convert a String column to Integer?
**A:**
```python
df = df.withColumn("Age", col("Age").cast("integer"))
```

### 21. String Filtering
**Q:** Filter for names starting with "A".
**A:**
```python
df.filter(col("Name").startswith("A"))
# OR
df.filter(col("Name").like("A%"))
```

### 22. List Filtering (IS IN)
**Q:** Filter for Department in IT or HR.
**A:**
```python
df.filter(col("Department").isin(["IT", "HR"]))
```

### 23. Substring
**Q:** Extract the first 3 characters of a Name.
**A:**
```python
from pyspark.sql.functions import substring
df.select(substring(col("Name"), 0, 3))
```

### 24. Conditional Logic (Case When)
**Q:** Create a column "Status": "Adult" if Age > 18, else "Minor".
**A:**
```python
from pyspark.sql.functions import when

df = df.withColumn("Status", 
    when(col("Age") > 18, "Adult")
    .otherwise("Minor")
)
```

### 25. Date Addition
**Q:** Add 5 days to a date column.
**A:**
```python
from pyspark.sql.functions import date_add
df.withColumn("Next_Week_Date", date_add(col("DateColumn"), 7))
```

### 26. Current Date & Time
**Q:** How do you get the current date and timestamp?
**A:**
```python
from pyspark.sql.functions import current_date, current_timestamp
df.select(current_date(), current_timestamp())
```

### 27. Union vs UnionByName
**Q:** What is the difference?
**A:**
*   `union()`: Merges by **position**. Column 1 matches Column 1. Dangerous if schemas differ order.
*   `unionByName()`: Merges by **column name**. Safer.

### 28. Joins
**Q:** Syntax for joining two DataFrames.
**A:**
```python
# Inner join (default)
df1.join(df2, "id")

# Left join
df1.join(df2, df1["id"] == df2["u_id"], "left")
```

### 29. SQL Temp Views
**Q:** How do you run SQL queries on a DataFrame?
**A:**
You must register it as a view first.
```python
df.createOrReplaceTempView("people")
spark.sql("SELECT * FROM people WHERE age > 20").show()
```

### 30. Writing to Parquet (Modes)
**Q:** How do you write a DataFrame overwriting existing files?
**A:**
```python
df.write.mode("overwrite").parquet("output_path")
```

### 31. Coalesce vs Repartition
**Q:** How do you reduce the number of output files to 1?
**A:**
```python
# coalesce is more efficient than repartition for reducing counts
df.coalesce(1).write.csv("output")
```
