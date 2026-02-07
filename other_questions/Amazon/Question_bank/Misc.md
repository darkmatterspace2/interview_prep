# Business & Transportation Domain Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Logistics KPIs and Domain Knowledge

---

## 1️⃣ Core Questions (Q101-Q105)

### Q101: Key KPIs for logistics systems

| KPI | Definition | Target | Why It Matters |
|-----|------------|--------|----------------|
| **OTIF (On-Time In-Full)** | % shipments delivered on time AND complete | > 98% | Customer satisfaction |
| **Delivery Accuracy** | % packages to correct address | > 99.5% | Cost of redelivery |
| **Fill Rate** | % of ordered items shipped | > 99% | Inventory management |
| **Order Cycle Time** | Order placed → delivered | < 2-3 days | Competitive advantage |
| **Cost Per Package** | Total logistics cost / packages | Varies by volume | Profitability |
| **First Attempt Delivery Rate** | % delivered on first try | > 95% | Efficiency |
| **Returns Rate** | % packages returned | < 5% | Customer satisfaction, cost |
| **Vehicle Utilization** | % of capacity used | > 80% | Cost efficiency |
| **Dock-to-Stock Time** | Receipt → available for sale | < 24 hours | Inventory velocity |

```sql
-- Calculate OTIF
SELECT 
    DATE_TRUNC('month', delivery_date) AS month,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN delivered_on_time AND items_complete THEN 1 ELSE 0 END) AS otif_orders,
    ROUND(100.0 * SUM(CASE WHEN delivered_on_time AND items_complete THEN 1 ELSE 0 END) / COUNT(*), 2) AS otif_pct
FROM orders
WHERE delivery_date IS NOT NULL
GROUP BY DATE_TRUNC('month', delivery_date);
```

---

### Q102: How data improves delivery efficiency

**Data-Driven Improvements:**

| Area | Data Used | Improvement |
|------|-----------|-------------|
| **Route Optimization** | Historical traffic, weather, time-of-day | 10-15% fuel savings |
| **Demand Forecasting** | Sales trends, seasonality, events | Pre-position inventory |
| **Capacity Planning** | Volume trends, peak patterns | Right-size fleet |
| **Carrier Selection** | Performance history, cost, SLA | Choose optimal carrier per shipment |
| **Delivery Window** | Customer availability patterns | Reduce failed deliveries |
| **Exception Prediction** | Delay patterns, external factors | Proactive customer communication |

```python
# Example: Carrier Selection Algorithm
def select_carrier(shipment):
    """
    Score carriers based on historical performance and cost
    """
    route = (shipment['origin'], shipment['destination'])
    priority = shipment['priority']
    
    scores = []
    for carrier in available_carriers:
        # Get historical metrics for this route
        metrics = get_carrier_metrics(carrier, route)
        
        score = (
            metrics['on_time_rate'] * 0.4 +        # 40% weight: reliability
            (1 - metrics['damage_rate']) * 0.2 +   # 20% weight: quality
            (1 - normalize_cost(metrics['avg_cost'])) * 0.3 +  # 30% weight: cost
            metrics['capacity_available'] * 0.1    # 10% weight: availability
        )
        
        # Priority adjustments
        if priority == 'EXPRESS' and metrics['express_capable']:
            score *= 1.2
        
        scores.append((carrier, score))
    
    return max(scores, key=lambda x: x[1])[0]
```

---

### Q103: Cost drivers in transportation

**Major Cost Components:**

| Component | % of Total | Drivers |
|-----------|------------|---------|
| **Fuel** | 30-35% | Distance, vehicle type, fuel prices |
| **Labor** | 25-30% | Driver wages, overtime, benefits |
| **Vehicle** | 15-20% | Depreciation, maintenance, insurance |
| **Overhead** | 10-15% | Facilities, management, IT |
| **Last Mile** | 50%+ of total | Dense urban, failed deliveries, returns |

**Last Mile Cost Breakdown:**
```
Total Delivery Cost: $10.00 (average)
├── First/Middle Mile: $3.00 (30%)
│   ├── Warehouse to Hub
│   └── Hub to Distribution Center
└── Last Mile: $7.00 (70%)  ← Most expensive!
    ├── Sorting: $1.00
    ├── Loading: $0.50
    ├── Transit: $3.00
    ├── Delivery Attempt: $2.00
    └── Customer Contact: $0.50
```

**Data to Track:**

```sql
-- Cost per delivery by zone type
SELECT 
    zone_type,  -- Urban, Suburban, Rural
    AVG(total_cost) AS avg_cost,
    AVG(attempts) AS avg_attempts,
    AVG(miles) AS avg_miles,
    AVG(total_cost / NULLIF(miles, 0)) AS cost_per_mile
FROM deliveries
GROUP BY zone_type;
```

---

### Q104: Metrics to track delivery delays

**Delay Categories:**

| Metric | Definition | Alert Threshold |
|--------|------------|-----------------|
| **Delay Rate** | % shipments late | > 5% |
| **Average Delay Hours** | Mean hours past SLA | > 4 hours |
| **Delay Reason Distribution** | % by cause | New category > 10% |
| **Delay Cost** | Financial impact | > $10K/day |
| **Customer Impact Score** | Priority customers affected | Any VIP |

**Root Cause Tracking:**

```sql
-- Delay reason analysis
SELECT 
    delay_reason,
    COUNT(*) AS delay_count,
    AVG(delay_hours) AS avg_delay_hours,
    SUM(estimated_cost_impact) AS total_cost
FROM shipments
WHERE is_delayed = TRUE
  AND delivery_date >= CURRENT_DATE - 30
GROUP BY delay_reason
ORDER BY delay_count DESC;
```

**Common Delay Reasons:**

| Reason | % of Delays | Mitigation |
|--------|------------|------------|
| **Weather** | 25% | Dynamic routing, proactive alerts |
| **Traffic** | 20% | Real-time routing, time-of-day optimization |
| **Capacity** | 15% | Better demand forecasting |
| **Customs** | 10% | Pre-clearance, documentation automation |
| **Address Issues** | 10% | Address validation at order time |
| **Carrier Issues** | 10% | Performance monitoring, backup carriers |
| **Other** | 10% | Varies |

---

### Q105: Trade-offs between speed and cost

**Trade-off Matrix:**

| Speed Option | Cost Multiplier | Use Case |
|--------------|-----------------|----------|
| **Same Day** | 5-10x | Urgent medical, perishables |
| **Next Day (Air)** | 2-3x | Prime, high-value customers |
| **2-Day (Ground Express)** | 1.5x | Standard e-commerce |
| **Standard (Ground)** | 1x (baseline) | Non-urgent |
| **Economy (Consolidated)** | 0.7x | Bulk, B2B, low priority |

**Decision Framework:**

```python
def choose_shipping_speed(order):
    """
    Balance customer expectation, cost, and margin
    """
    margin = order['sale_price'] - order['cost']
    customer_tier = order['customer_tier']
    promised_sla = order['promised_delivery_days']
    
    # High-value customers: Prioritize speed
    if customer_tier == 'PRIME' or margin > 100:
        return 'NEXT_DAY'
    
    # Standard promise: Use cheapest that meets SLA
    current_date = datetime.now().date()
    required_delivery = current_date + timedelta(days=promised_sla)
    
    options = get_shipping_options(order['origin'], order['destination'])
    
    # Filter options that meet SLA
    valid_options = [o for o in options if o['estimated_delivery'] <= required_delivery]
    
    if not valid_options:
        return 'EXPRESS'  # No cheap option meets SLA, upgrade
    
    # Choose cheapest valid option
    return min(valid_options, key=lambda x: x['cost'])['service_level']
```

**Cost vs Speed Visualization:**

```
Cost ▲
     │                               ★ Same Day
     │                          ★ Next Day
     │                    ★ 2-Day
     │              ★ Standard
     │        ★ Economy
     │
     └────────────────────────────────────────▶ Speed (hours to deliver)
     
Sweet Spot: 2-Day for most e-commerce
- 80% customer satisfaction
- 60% of fastest option cost
```

---

## 2️⃣ Additional Domain Knowledge

### Supply Chain Visibility

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    END-TO-END VISIBILITY                                     │
└─────────────────────────────────────────────────────────────────────────────┘

[Order Placed]    [Warehouse]     [In Transit]    [Last Mile]     [Delivered]
     │                │                │               │               │
     ▼                ▼                ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Order   │───▶│  Pick &  │───▶│  Carrier │───▶│  Local   │───▶│  Customer│
│  System  │    │  Pack    │    │  Network │    │  Courier │    │  Receipt │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │                │                │               │               │
   [Event]         [Event]         [Events]        [Events]        [Event]
     │                │                │               │               │
     └────────────────┴────────────────┴───────────────┴───────────────┘
                                       │
                              ┌────────▼────────┐
                              │  Event Stream   │
                              │    (Kafka)      │
                              └────────┬────────┘
                                       │
                              ┌────────▼────────┐
                              │   Real-time     │
                              │   Tracking DB   │
                              └─────────────────┘
```

### Inventory Velocity Metrics

| Metric | Formula | Good Target |
|--------|---------|-------------|
| **Inventory Turnover** | COGS / Avg Inventory | > 8x/year |
| **Days Sales of Inventory** | 365 / Turnover | < 45 days |
| **Fill Rate** | Units Shipped / Units Ordered | > 99% |
| **Backorder Rate** | Backordered / Total Orders | < 2% |
| **Stockout Rate** | Stockout Days / Total Days | < 1% |

### Network Optimization

```sql
-- Identify underutilized facilities
SELECT 
    facility_id,
    facility_type,
    capacity_max,
    SUM(units_processed) AS actual_volume,
    ROUND(100.0 * SUM(units_processed) / capacity_max, 2) AS utilization_pct
FROM facility_operations
WHERE operation_date >= CURRENT_DATE - 30
GROUP BY facility_id, facility_type, capacity_max
HAVING utilization_pct < 50  -- Underutilized
ORDER BY utilization_pct;

-- Identify best location for new facility
WITH regional_demand AS (
    SELECT 
        destination_region,
        SUM(package_count) AS total_demand,
        AVG(transit_days) AS avg_transit
    FROM shipments
    GROUP BY destination_region
)
SELECT 
    r.destination_region,
    r.total_demand,
    r.avg_transit,
    f.nearest_facility,
    f.distance_miles
FROM regional_demand r
JOIN closest_facility f ON r.destination_region = f.region
WHERE r.avg_transit > 3  -- Areas with slow delivery
ORDER BY r.total_demand DESC;
```

---

## 3️⃣ Interview Tips for Domain Questions

```
1. SHOW BUSINESS UNDERSTANDING
   ❌ "I'd track delivery time"
   ✅ "I'd track OTIF because it combines timeliness AND completeness, 
       which both impact customer satisfaction"

2. CONNECT DATA TO OUTCOMES
   ❌ "We built a dashboard"
   ✅ "Dashboard enabled operations to identify delay patterns by carrier,
       leading to 15% improvement in on-time delivery"

3. UNDERSTAND TRADE-OFFS
   ❌ "Faster is better"
   ✅ "Same-day costs 5x more. We analyze margin to determine which 
       orders justify the premium speed"

4. MENTION SCALE
   ❌ "We processed orders"
   ✅ "We processed 50M packages/day across 100K routes"

5. AMAZON-SPECIFIC TERMS
   • FC (Fulfillment Center)
   • DS (Delivery Station)
   • Prime Promise
   • Ship Option
   • Inbound/Outbound
   • Last Mile vs Middle Mile
```
