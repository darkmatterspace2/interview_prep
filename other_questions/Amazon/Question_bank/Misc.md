# Business & Transportation Domain Questions & Answers (Question Bank 1)

> **Amazon Data Engineer Style** - Logistics KPIs and Domain Knowledge

---

<a id="index"></a>
## 📑 Table of Contents

| Section | Topics |
|---------|--------|
| [1️⃣ Core Questions (Q101-Q105)](#1️⃣-core-questions-q101-q105) | KPIs, Efficiency, Costs, Delays |
| &nbsp;&nbsp;&nbsp;└ [Q101: Logistics KPIs](#q101-key-kpis-for-logistics-systems) | OTIF, Fill Rate, Cycle Time |
| &nbsp;&nbsp;&nbsp;└ [Q102: Data-driven efficiency](#q102-how-data-improves-delivery-efficiency) | Route optimization, carrier selection |
| &nbsp;&nbsp;&nbsp;└ [Q103: Cost drivers](#q103-cost-drivers-in-transportation) | Fuel, labor, last mile |
| &nbsp;&nbsp;&nbsp;└ [Q104: Delay metrics](#q104-metrics-to-track-delivery-delays) | Root cause tracking |
| &nbsp;&nbsp;&nbsp;└ [Q105: Speed vs cost trade-offs](#q105-trade-offs-between-speed-and-cost) | Decision framework |
| [2️⃣ Additional Domain Knowledge](#2️⃣-additional-domain-knowledge) | Visibility, Inventory, Network |
| &nbsp;&nbsp;&nbsp;└ [Supply Chain Visibility](#supply-chain-visibility) | End-to-end tracking |
| &nbsp;&nbsp;&nbsp;└ [Inventory Velocity Metrics](#inventory-velocity-metrics) | Turnover, fill rate |
| &nbsp;&nbsp;&nbsp;└ [Network Optimization](#network-optimization) | Facility utilization |
| [3️⃣ Interview Tips](#3️⃣-interview-tips-for-domain-questions) | Amazon-specific terms |

---

<a id="1️⃣-core-questions-q101-q105"></a>
## 1️⃣ Core Questions (Q101-Q105) [↩️](#index)

<a id="q101-key-kpis-for-logistics-systems"></a>
### Q101: Key KPIs for logistics systems [↩️](#index)

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

<a id="q102-how-data-improves-delivery-efficiency"></a>
### Q102: How data improves delivery efficiency [↩️](#index)

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
    route = (shipment['origin'], shipment['destination'])
    priority = shipment['priority']
    
    scores = []
    for carrier in available_carriers:
        metrics = get_carrier_metrics(carrier, route)
        
        score = (
            metrics['on_time_rate'] * 0.4 +        # 40% weight: reliability
            (1 - metrics['damage_rate']) * 0.2 +   # 20% weight: quality
            (1 - normalize_cost(metrics['avg_cost'])) * 0.3 +  # 30% weight: cost
            metrics['capacity_available'] * 0.1    # 10% weight: availability
        )
        
        if priority == 'EXPRESS' and metrics['express_capable']:
            score *= 1.2
        
        scores.append((carrier, score))
    
    return max(scores, key=lambda x: x[1])[0]
```

---

<a id="q103-cost-drivers-in-transportation"></a>
### Q103: Cost drivers in transportation [↩️](#index)

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

---

<a id="q104-metrics-to-track-delivery-delays"></a>
### Q104: Metrics to track delivery delays [↩️](#index)

**Delay Categories:**

| Metric | Definition | Alert Threshold |
|--------|------------|-----------------|
| **Delay Rate** | % shipments late | > 5% |
| **Average Delay Hours** | Mean hours past SLA | > 4 hours |
| **Delay Reason Distribution** | % by cause | New category > 10% |
| **Delay Cost** | Financial impact | > $10K/day |
| **Customer Impact Score** | Priority customers affected | Any VIP |

**Common Delay Reasons:**

| Reason | % of Delays | Mitigation |
|--------|------------|------------|
| **Weather** | 25% | Dynamic routing, proactive alerts |
| **Traffic** | 20% | Real-time routing, time-of-day optimization |
| **Capacity** | 15% | Better demand forecasting |
| **Customs** | 10% | Pre-clearance, documentation automation |
| **Address Issues** | 10% | Address validation at order time |
| **Carrier Issues** | 10% | Performance monitoring, backup carriers |

---

<a id="q105-trade-offs-between-speed-and-cost"></a>
### Q105: Trade-offs between speed and cost [↩️](#index)

**Trade-off Matrix:**

| Speed Option | Cost Multiplier | Use Case |
|--------------|-----------------|----------|
| **Same Day** | 5-10x | Urgent medical, perishables |
| **Next Day (Air)** | 2-3x | Prime, high-value customers |
| **2-Day (Ground Express)** | 1.5x | Standard e-commerce |
| **Standard (Ground)** | 1x (baseline) | Non-urgent |
| **Economy (Consolidated)** | 0.7x | Bulk, B2B, low priority |

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

<a id="2️⃣-additional-domain-knowledge"></a>
## 2️⃣ Additional Domain Knowledge [↩️](#index)

<a id="supply-chain-visibility"></a>
### Supply Chain Visibility [↩️](#index)

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
                              │   Real-time     │
                              │   Tracking DB   │
                              └─────────────────┘
```

<a id="inventory-velocity-metrics"></a>
### Inventory Velocity Metrics [↩️](#index)

| Metric | Formula | Good Target |
|--------|---------|-------------|
| **Inventory Turnover** | COGS / Avg Inventory | > 8x/year |
| **Days Sales of Inventory** | 365 / Turnover | < 45 days |
| **Fill Rate** | Units Shipped / Units Ordered | > 99% |
| **Backorder Rate** | Backordered / Total Orders | < 2% |
| **Stockout Rate** | Stockout Days / Total Days | < 1% |

<a id="network-optimization"></a>
### Network Optimization [↩️](#index)

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
```

---

<a id="3️⃣-interview-tips-for-domain-questions"></a>
## 3️⃣ Interview Tips for Domain Questions [↩️](#index)

```
1. SHOW BUSINESS UNDERSTANDING
   ❌ "I'd track delivery time"
   ✅ "I'd track OTIF because it combines timeliness AND completeness"

2. CONNECT DATA TO OUTCOMES
   ❌ "We built a dashboard"
   ✅ "Dashboard enabled 15% improvement in on-time delivery"

3. UNDERSTAND TRADE-OFFS
   ❌ "Faster is better"
   ✅ "Same-day costs 5x more. We analyze margin to determine which orders justify premium speed"

4. MENTION SCALE
   ❌ "We processed orders"
   ✅ "We processed 50M packages/day across 100K routes"

5. AMAZON-SPECIFIC TERMS
   • FC (Fulfillment Center)
   • DS (Delivery Station)
   • Prime Promise
   • Last Mile vs Middle Mile
```
