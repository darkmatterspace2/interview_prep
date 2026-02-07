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



Feature

Processing Layers

Data Flow

Complexity

Maintenance

Real-time Processing

Batch Processing

Lambda

Batch, Speed, Serving

Separate batch and stream
paths

Higher

More difficult

Good

Good

Kappa

Single Stream Processing

Single data stream

Use Cases

Big data analytics, historical
analysis

Lower

Easier

Excellent

Can be achieved by
replaying the stream

Real-time analytics, loT,
event-driven applications