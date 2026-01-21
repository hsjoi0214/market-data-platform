# market-data-platform
Cloud data engineering project: streaming + batch pipelines for market stock data.

# ROUGH NOTES

## Core Components of Great Expectations used in quality.py for a dummy quality check for local testing

### Component: What It Does
- Data Context: The central controller. Manages config, connections, expectations, results.
- Data Source: Connects to the place where your data lives (CSV, SQL, S3, Pandas, etc.).
- Data Asset: A specific dataset (e.g., a CSV file or SQL table).
- Batch: A slice or unit of data to validate (e.g., one month's data, or all at once).
- Batch Request: The object that tells GE: "get me this batch from this source."
- Expectation: A single rule or test (e.g., "no nulls in column A").
- Validator: The object that applies your expectations to your batch of data.

### local testing with ge for streaming pipeline
- pipeline is: curated list → DataFrame → Batch → Validator → Expectations → PASS/FAIL
- made intensional change in app.py to break the logic to see if the quarantine logic is working . 