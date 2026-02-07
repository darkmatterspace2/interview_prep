# Types of Architecture Patterns

## Data Management Architectures

- Data Mesh
- Data LakeHouse

## Data Processing Architectures

- Lambda
- Kappa
- Serverless
- Microservices
- CQRS and Event Sourcing


## Lambda Architecture: 
Splits data processing into two layers: batch for historic data and real-time for immediate data. Netflix uses this for recommendations (2:14).

## Kappa Architecture: 
Uses a single real-time layer, replaying events for batch processing. Uber uses this for its core infrastructure, enabling quick reactions to changing conditions (3:07).

## Event-Driven Microservices Architecture: 
Breaks down applications into small, independent services that communicate via events. Amazon uses this for order processing (5:14).

## Serverless Pipelines: 
Utilizes serverless services like AWS Lambda, where you pay only for computation time. Coca-Cola uses this for vending machine logic (7:06).

## Command Query Responsibility Segregation (CQRS) and Event Sourcing: 
Separates read (queries) and write (commands) operations, logging all state changes as events. This is common in banking applications (7:58).

## Data Mesh Architecture: 
A decentralized approach where different business domains own and manage their data. Zalando uses this for its data lake (9:44).

## Lakehouse Architecture: 
Combines the flexibility and cost-effectiveness of data lakes with the structured, performant querying capabilities of data warehouses.


