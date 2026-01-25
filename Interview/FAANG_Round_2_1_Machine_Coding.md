# FAANG Machine Coding Guide (Round 2.1 Focus)

This guide covers all key topics for the Machine Coding round, specifically tailored for companies like Flipkart, Uber, Swiggy, and others with similar interview styles.

## 1. Object-Oriented Programming (OOP) Essentials

The foundation of machine coding is a valid object-oriented model.

### Core Concepts

*   **Classes & Objects**:
    *   **Class**: Blueprint/Template (e.g., `Vehicle`).
    *   **Object**: Instance (e.g., `Car`, `Bike`).
    *   *Tip*: Always start by identifying the "Nouns" in the problem statement; these are likely your classes.

*   **Interfaces / Abstract Classes**:
    *   Use **Interfaces** to define abilities (e.g., `Drivable`, `PaymentMethod`).
    *   Use **Abstract Classes** for shared base behavior + contracts (e.g., `BaseUser` handles `id` and `name`, concrete users handle roles).
    *   *Flipkart Tip*: Always code against interfaces involved in services (e.g., `INotificationService` instead of `EmailService`).

*   **Inheritance vs Composition**:
    *   **Inheritance** (`IS-A`): `Car` is a `Vehicle`. Rigid structure.
    *   **Composition** (`HAS-A`): `Car` has an `Engine`. Flexible.
    *   *Rule of Thumb*: Prefer **Composition over Inheritance**. It allows you to swap behaviors at runtime (Strategy Pattern).

*   **Encapsulation**:
    *   Keep fields `private`.
    *   Expose data only via public methods/getters.
    *   Protect internal state from invalid updates (e.g., `setAge(-1)` should throw error).

*   **Polymorphism**:
    *   Runtime polymorphism (Overriding): `paymentService.pay()` triggers different logic for `UPIPayment` vs `CreditCardPayment`.

---

## 2. SOLID Principles (The Evaluator's Checklist)

Your code is scored heavily on this.

### S - Single Responsibility Principle (SRP)
*   **Concept**: A class should have only one reason to change.
*   **Example**: `Order` class should typically handle data. `OrderService` handles business logic. `InvoicePrinter` handles printing. Don't mix them.

### O - Open/Closed Principle (OCP)
*   **Concept**: Open for extension, closed for modification.
*   **Example**: Adding a new Discount type shouldn't modify the existing `DiscountService`. Instead, add a new `TenPercentDiscount` class implementing `IDiscount`.

### L - Liskov Substitution Principle (LSP)
*   **Concept**: Subtypes must be substitutable for their base types.
*   **Anti-Pattern**: A `Penguin` class inheriting `Bird` but throwing exception on `fly()`.

### I - Interface Segregation Principle (ISP)
*   **Concept**: Clients shouldn't depend on methods they don't use.
*   **Example**: Split `Worker` interface into `Workable` and `Eatable` if robots don't eat.

### D - Dependency Inversion Principle (DIP)
*   **Concept**: Depend on abstractions, not concretions.
*   **Example**: Inject `IPaymentProcessor` into `BookingService`, not `PayPalProcessor` directly.

---

## 3. Design Patterns (The "Power Moves")

Use these to solve specific extensibility problems.

### Factory Pattern
*   **Use When**: Creating complex objects or when creation logic varies based on type.
*   **Example**: `NotificationFactory.getService("EMAIL")` returns `EmailService`.

### Strategy Pattern (CRITICAL)
*   **Use When**: You have interchangeable algorithms.
*   **Example**: Pricing strategies (`FlatRate`, `SurgePricing`), Parking assignment strategies (`LowestFloorFirst`, `NearestToEntry`).

### Singleton Pattern
*   **Use When**: Exactly one instance is needed (e.g., `ConfigurationManager`, `DatabaseConnection`).
*   **Warning**: Don't overuse. It makes testing hard. In machine coding, it's safer to create a Service class and inject it once.

### Observer Pattern
*   **Use When**: One change needs to notify many others.
*   **Example**: When `Order` status becomes `SHIPPED`, notify `SMSModule`, `EmailModule`, and `InventorySystem`.

### Builder Pattern
*   **Use When**: Constructing complex objects with many optional parameters.
*   **Example**: `Order.builder().setId(1).setItems(items).setCoupon("SAVE10").build()`.

---

## 4. Code Quality Checklist

*   **Separation of Concerns**:
    *   **Models**: POJOs (Plain Old Java Objects) - `User`, `Ride`, `Ticket`.
    *   **Services**: Logic - `UserService`, `BookingService`.
    *   **Repositories (DAO)**: In-memory storage - `UserMap`, `RideList`.
    *   **Driver/Main**: Entry point interacting with services.
*   **Readable Naming**:
    *   Variable: `isAvailable` (boolean), `userMap` (collection).
    *   Methods: `calculateTotal()`, `assignDriver()`.
*   **Extensible Structure**:
    *   Can you add a new generic vehicle type without rewriting `ParkingLot` class?
*   **Exception Handling**:
    *   Don't return string "Error". Throw `InvalidOperationException`.
*   **Input Validation**:
    *   Check nulls and bounds at the start of public methods.

---

## 5. Data Structures for Machine Coding

You won't implementing complex trees/graphs usually. You need fast lookup and order.

*   **HashMap / Dictionary**: Primary storage. O(1) retrieval by ID. `Map<String, User>`.
*   **List / Array**: Storing collections where index matters less or simple iteration needed.
*   **Set**: Uniqueness (e.g., `activeUserIds`).
*   **Priority Queue**: "Get nearest driver", "Get cheapest ride" (if optimization is needed).

---

## 6. Common Problem Types (Practice Scenarios)

1.  **Parking Lot**:
    *   Concepts: Multilevel, different vehicle sizes, pricing strategies, filling strategies.
2.  **Library Management**:
    *   Concepts: Books, Copies, Users, Borrow limits, Fines, Search by Title/Author.
3.  **Splitwise (Equation Simplifier)**:
    *   Concepts: Users, Groups, Expenses, Exact/Percent splits, `Simplify Debt` graph algorithm.
4.  **Elevator System**:
    *   Concepts: Scheduling requests (SCAN/LOOK algorithm), multiple elevators, states (MOVING_UP, IDLE).
5.  **Rate Limiter**:
    *   Concepts: User, API-Key, sliding window/token bucket logic.
6.  **Inventory / Order System (E-commerce)**:
    *   Concepts: Cart, Inventory locking (concurrency simulation), Payment state machine.

---

## 7. Testing Mindset (The Final 15 Mins)

The interviewer wants to see your code work.

1.  **Driver Class**: Create a `Main` class that acts as a simulation.
2.  **Hardcoded Data**: Pre-populate some users/items to save demo time.
3.  **Happy Path**: Show the standard flow working perfectly.
4.  **Edge Cases**:
    *   Booking when inventory is 0.
    *   Parking a Truck in a Bike slot.
    *   Invalid user ID.
5.  **Bonus**: Use a simple JUnit/Test framework if comfortable, otherwise strictly structured Print statements are accepted.

---

## Sample Project Structure (Java/Python style conceptual)

```text
/src
  /model
    User.java
    Vehicle.java
    Ticket.java
  /service
    ParkingService.java (Interface)
    ParkingServiceImpl.java (Implementation)
    PricingStrategy.java (Interface)
  /repository
    InMemoryParkingRepository.java
  /exception
    ParkingFullException.java
  Main.java
```
