# dbt (Data Build Tool) Interview Questions
*Mid to Senior Level*

A comprehensive guide to Analytics Engineering interviews, focusing on dbt Core, modeling strategies, and advanced configurations.

---

## Table of Contents
1. [Core Concepts & Architecture](#core-concepts--architecture)
2. [Materializations](#materializations)
3. [Incremental Models](#incremental-models)
4. [Testing & Documentation](#testing--documentation)
5. [Snapshots (SCD Type 2)](#snapshots-scd-type-2)
6. [Advanced Patterns (Hooks/Macros)](#advanced-patterns)

---

## Core Concepts & Architecture

### 1. What is dbt and how does it differ from traditional ETL?
**Q:** Explain dbt's role in the "Modern Data Stack" (ELT).
**A:**
*   **T in ELT:** dbt only does the **Transformation** step. It assumes data is already loaded (Extract/Load) into the warehouse (Snowflake/BigQuery/Redshift).
*   **Code-First:** It allows writing data transformations in SQL (Select statements), checking them into version control (Git), and testing/documenting them like software code.
*   **Compilation:** dbt compiles Jinja-SQL code into raw SQL and executes it inside the data warehouse.

### 2. File Structure (`dbt_project.yml`)
**Q:** What is the purpose of `dbt_project.yml`?
**A:**
It is the configuration file for the project. It defines:
*   Project Name and Version.
*   Profile to use (connection details).
*   Directory paths (model-paths, seed-paths).
*   **Global Configs:** Setting default materializations (e.g., `+materialized: view`) or tags for specific folders.

---

## Materializations

### 3. Types of Materializations
**Q:** Name and explain the 4 core materializations in dbt.
**A:**
1.  **View (Default):** Creates a database view. Fast to run, but computed at query time (slow for end users).
2.  **Table:** Creates a physical table. Slower to run (rebuilds entire table), but fast query performance.
3.  **Incremental:** Only inserts/updates new rows since the last run. Essential for big data.
4.  **Ephemeral:** No database object created. It acts like a CTE snippet injected into downstream models (good for reusable logic that shouldn't clutter the DB).

### 4. Source vs Ref
**Q:** What is the difference between `{{ source() }}` and `{{ ref() }}`?
**A:**
*   `{{ source('schema', 'table') }}`: References raw data loaded by external tools (Fivetran/Airbyte). Defined in `src_*.yml`.
*   `{{ ref('model_name') }}`: References another dbt model within your project. Critical for building the **DAG** (Dependency Graph) so dbt knows the order of execution.

---

## Incremental Models

### 5. Designing an Incremental Model
**Q:** How do you configure a model to be incremental? What is the `is_incremental()` macro?
**A:**
```sql
{{ config(
    materialized='incremental',
    unique_key='transaction_id'
) }}

SELECT *
FROM {{ source('raw', 'transactions') }}

{% if is_incremental() %}
  -- This filter only runs on subsequent runs, not the first run
  WHERE event_time > (SELECT MAX(event_time) FROM {{ this }})
{% endif %}
```
*   **Logic:** The `if` block allows fetching only new data.
*   **Unique Key:** dbt uses this to `MERGE` (Update existing, Insert new) instead of just appending.

### 6. Full Refresh
**Q:** What happens if you run `dbt run --full-refresh` on an incremental model?
**A:**
It ignores the `is_incremental()` logic, drops the existing table, and rebuilds it entirely from scratch. This is needed if schema changes or logic changes drastically.

---

## Testing & Documentation

### 7. Generic vs Singular Tests
**Q:** What is the difference?
**A:**
*   **Generic Tests:** Reusable tests defined in `schema.yml`. dbt ships with 4 built-in:
    1.  `unique`
    2.  `not_null`
    3.  `accepted_values`
    4.  `relationships` (Foreign Key check)
*   **Singular Tests:** Specific SQL files in the `tests/` folder. If the query returns *any rows*, the test fails. (e.g., `SELECT * FROM orders WHERE total < 0`).

### 8. Freshness
**Q:** How do you ensure your source data isn't stale?
**A:**
Define `freshness` blocks in `src_*.yml`:
```yaml
sources:
  - name: stripe
    tables:
      - name: payments
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}
        loaded_at_field: _etl_loaded_at
```
Run `dbt source freshness` to check.

---

## Snapshots (SCD Type 2)

### 9. Implementing Slowly Changing Dimensions
**Q:** How does dbt handle SCD Type 2 (Tracking history of changes)?
**A:**
Via **Snapshots**.
*   **Strategy:** `timestamp` (updates based on `updated_at` column) or `check` (hashing a list of columns to detect change).
*   dbt manages the columns `dbt_valid_from` and `dbt_valid_to` automatically.
*   Stored in `snapshots/` folder.

```sql
{% snapshot orders_snapshot %}
{{
    config(
      target_schema='snapshots',
      unique_key='id',
      strategy='timestamp',
      updated_at='updated_at',
    )
}}
select * from {{ source('jaffle_shop', 'orders') }}
{% endsnapshot %}
```
Run with `dbt snapshot`.

---

## Advanced Patterns

### 10. Seeds
**Q:** What are Seeds and when to use them?
**A:**
*   CSV files in `seeds/` directory.
*   `dbt seed` loads them into the data warehouse.
*   **Use Case:** Static lookup data like `country_codes` or `mapping_tables`. Not for loading large raw data.

### 11. Custom Macros (DRY)
**Q:** How do you avoid repeating SQL logic (e.g., converting cents to dollars)?
**A:**
Write a Jinja macro in `macros/`.
```sql
{% macro cents_to_dollars(column_name, decimal_places=2) %}
    ROUND( ({{ column_name }} / 100), {{ decimal_places }} )
{% endmacro %}
```
Usage in model:
`SELECT {{ cents_to_dollars('amount_cents') }} FROM payments`

### 12. Deployment Environments
**Q:** How do you handle Dev vs Prod environments?
**A:**
*   **profiles.yml:** Define distinct targets (`dev`, `prod`).
*   **dbt Cloud / CI:**
    *   `dev`: Writes to `dbt_jdoe` schema.
    *   `prod`: Writes to `analytics` schema.
*   **Limit Data in Dev:**
    ```sql
    {% if target.name == 'dev' %}
    LIMIT 100
    {% endif %}
    ```
