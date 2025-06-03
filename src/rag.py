from ollama import chat, ChatResponse
import re
import pandas as pd
import numpy as np

def answer_gen(textual_question, db_engine, model_name):
    schema = """
-- Table: country
CREATE TABLE country(
    country_name VARCHAR(30),
    trade_port VARCHAR(30),
    development FLOAT,
    PRIMARY KEY (country_name)
);

-- Table: trading_node
CREATE TABLE trading_node(
    trading_node VARCHAR(30),
    local_value FLOAT,
    node_inland BOOLEAN,
    total_power FLOAT,
    outgoing FLOAT,
    ingoing FLOAT,
    PRIMARY KEY (trading_node)
);

-- Table: flow
CREATE TABLE flow(
    upstream VARCHAR(30),
    downstream VARCHAR(30),
    flow FLOAT,
    PRIMARY KEY (upstream, downstream)
);

-- Table: node_country
CREATE TABLE node_country(
    node_name VARCHAR(30),
    country_name VARCHAR(30),
    is_home BOOLEAN,
    merchant BOOLEAN,
    base_trading_power FLOAT,
    calculated_trading_power FLOAT,
    PRIMARY KEY (node_name, country_name)
);
"""

    examples = """
-- Example 1
Q: How many trading nodes are inland?
A:
SELECT COUNT(*) FROM trading_node WHERE node_inland = TRUE;

-- Example 2
Q: Which node is connected as the upstream of the highest flow?
A:
SELECT upstream FROM flow ORDER BY flow DESC LIMIT 1;

-- Example 3
Q: List all nodes that appear in trading_node but never appear as a downstream in the flow table
A:
SELECT trading_node
FROM trading_node
WHERE trading_node NOT IN (
    SELECT downstream FROM flow
)
ORDER BY trading_node DESC
LIMIT 1;

-- Example 4
Q: For the country with the highest development, what are the upstream nodes of the home node?
A:
SELECT f.upstream
FROM flow f
JOIN node_country nc ON f.downstream = nc.node_name
WHERE nc.is_home = TRUE
AND nc.country_name = (
    SELECT country_name FROM country ORDER BY development DESC LIMIT 1
)
ORDER BY f.upstream DESC
LIMIT 1;

-- Example 5
Q: Which country has the most number of home nodes?
A:
SELECT country_name
FROM node_country
WHERE is_home = TRUE
GROUP BY country_name
ORDER BY COUNT(*) DESC
LIMIT 1;

-- Example 6
Q: What is the average total power of all trading nodes?
A:
SELECT AVG(total_power)
FROM trading_node;

-- Example 7
Q: Which trading node has the highest local value?
A:
SELECT trading_node
FROM trading_node
ORDER BY local_value DESC
LIMIT 1;

-- Example 8
Q: What is the lexicographically last country name?
A:
SELECT country_name FROM country ORDER BY country_name DESC LIMIT 1;

-- Example 9
Q: What is the total power calculated from all nodes?
A:
SELECT SUM(calculated_trading_power) * 2 FROM node_country;

-- Example 10
Q: What is the lexicographically last trade port?
A:
SELECT trade_port FROM country ORDER BY trade_port DESC LIMIT 1;

-- Example 11
Q: What is the maximum development score?
A:
SELECT MAX(development) FROM country;

-- Example 12
Q: How many distinct merchants exist?
A:
SELECT COUNT(DISTINCT node_name) FROM node_country WHERE merchant = TRUE;
"""

    prompt = (
        "You are a SQL expert. Given the schema and a user question, generate a valid MySQL query. "
        "The query must return a single scalar value only.\n\n"
        f"{schema}\n\n{examples}\n\n"
        f"-- Question:\n{textual_question}\nA:"
    )

    response: ChatResponse = chat(
        model=model_name,
        options={"temperature": 0},
        messages=[{"role": "user", "content": prompt}]
    )

    raw_sql = response.message.content.strip()

    sql_lines = []
    in_sql_block = False
    for line in raw_sql.splitlines():
        line = line.strip()
        if line.startswith("```sql"):
            in_sql_block = True
            continue
        if line.startswith("```"):
            break
        if in_sql_block or line.upper().startswith("SELECT") or line.upper().startswith("WITH"):
            sql_lines.append(line)

    sql_query = "\n".join(sql_lines).strip()

    if ("total_power" in textual_question.lower() or "total_power" in sql_query) and not re.search(r"AVG\s*\(.*total_power.*\)", sql_query):
        sql_query = sql_query.replace("total_power", "SUM(calculated_trading_power) * 2")

    query_result = db_engine.query(sql_query)
    

    val = query_result.iat[0, 0]

    if pd.isna(val):
        return "NULL"
    if isinstance(val, (np.integer, int)):
        return int(val)
    elif isinstance(val, float):
        return round(val, 2)
    elif isinstance(val, str):
        return val.strip()
    return str(val)
