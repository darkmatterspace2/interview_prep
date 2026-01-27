# Design Pattern Interview Questions

## Beginner Level (Concepts & SOLID Principles)

1.  **What is a Design Pattern in software engineering?**
    *   **Answer:** A design pattern is a general, reusable solution to a commonly occurring problem within a given context in software design. It is not a finished design that can be transformed directly into source code, but rather a description or template for how to solve a problem.

2.  **Explain the Single Responsibility Principle (SRP) from SOLID.**
    *   **Answer:** A class should have only one reason to change. This means that a class should have only one job or responsibility. If a class has more than one responsibility, it becomes coupled, and changes to one responsibility might impair or inhibit the other.

3.  **Explain the Open/Closed Principle (OCP) from SOLID.**
    *   **Answer:** Software entities (classes, modules, functions, etc.) should be open for extension, but closed for modification. This allows adding new functionality without changing existing code, typically achieved using interfaces and inheritance.

4.  **Explain the Liskov Substitution Principle (LSP) from SOLID.**
    *   **Answer:** Objects of a superclass should be replaceable with objects of its subclasses without breaking the application. In simpler terms, if class B is a subtype of class A, we should be able to pass an object of class B to any method that expects an object of class A and have it function correctly.

5.  **Explain the Interface Segregation Principle (ISP) from SOLID.**
    *   **Answer:** Clients should not be forced to depend on interfaces they do not use. It is better to have many specific interfaces than one general-purpose interface. This prevents "fat" interfaces where implementing classes are forced to dummy-implement methods they don't need.

6.  **Explain the Dependency Inversion Principle (DIP) from SOLID.**
    *   **Answer:** High-level modules should not depend on low-level modules. Both should depend on abstractions (interfaces). Abstractions should not depend on details. Details (concrete implementations) should depend on abstractions.

7.  **What is the Singleton Pattern?**
    *   **Answer:** A creational pattern that ensures a class has only one instance and provides a global point of access to it. Used for logging, driver objects, caching, and thread pools.

8.  **What is the Factory Pattern?**
    *   **Answer:** A creational pattern that defines an interface for creating an object, but lets subclasses alter the type of objects that will be created. It promotes loose coupling by eliminating the need to bind application-specific classes into the code.

9.  **What is the difference between an Interface and an Abstract Class in the context of design patterns?**
    *   **Answer:** An interface defines a contract (Behavior) that a class must implement (Can-Do relationship), while an Abstract Class defines a common base (Is-A relationship) that can provide default behavior. Design patterns like **Strategy** use interfaces heavily, while **Template Method** relies on abstract classes.

10. **What are the three main categories of Design Patterns?**
    *   **Answer:**
        *   **Creational:** Deal with object creation mechanisms (e.g., Singleton, Factory).
        *   **Structural:** Deal with object composition (e.g., Adapter, Decorator).
        *   **Behavioral:** Deal with communication between objects (e.g., Observer, Strategy).

## Medium Level (Structural & Behavioral)

11. **What is the Builder Pattern and when should you use it?**
    *   **Answer:** The Builder pattern allows constructing complex objects step by step. It separates the construction of a complex object from its representation. Use it when an object requires many constructor arguments (avoiding the "telescoping constructor" anti-pattern) or when specific configurations are needed (e.g., building a SQL query or a Car object).

12. **Explain the Prototype Pattern.**
    *   **Answer:** It specifies the kinds of objects to create using a prototypical instance, and creates new objects by copying this prototype. It is useful when object creation is expensive (e.g., database calls) compared to cloning.

13. **What is the Adapter Pattern?**
    *   **Answer:** A structural pattern that allows objects with incompatible interfaces to collaborate. It acts as a wrapper (like a physical power adapter) converting the interface of one class into an interface expected by the clients.

14. **What is the Decorator Pattern?**
    *   **Answer:** A structural pattern that allows adding new behavior to an existing object dynamically without altering its structure. It provides a flexible alternative to subclassing for extending functionality (e.g., Step Streams in Java IO).

15. **Explain the Facade Pattern.**
    *   **Answer:** It provides a simplified interface to a library, a framework, or any other complex set of classes. It hides the complexity of the subsystem from the client (e.g., a "CarStarter" class that internally handles fuel injection, battery checks, and ignition).

16. **What is the Proxy Pattern?**
    *   **Answer:** A placeholder for another object to control access to it. Types include:
        *   **Remote Proxy:** Represents an object in a different address space.
        *   **Virtual Proxy:** Creates expensive objects on demand (lazy loading).
        *   **Protection Proxy:** Controls access rights.

17. **What is the Observer Pattern?**
    *   **Answer:** A behavioral pattern where an object (Subject) maintains a list of its dependents (Observers) and notifies them automatically of any state changes. Commonly used in implementing event handling systems (e.g., GUI listeners).

18. **What is the Strategy Pattern?**
    *   **Answer:** It defines a family of algorithms, encapsulates each one, and makes them interchangeable. Strategy lets the algorithm vary independently from clients that use it (e.g., different Sorting strategies or Payment methods).

19. **Explain the Command Pattern.**
    *   **Answer:** It turns a request into a stand-alone object that contains all information about the request. This transformation lets you parameterize methods with different requests, delay or queue a request's execution, and support undoable operations.

20. **What is the Iterator Pattern?**
    *   **Answer:** A behavioral pattern that lets you traverse elements of a collection without exposing its underlying representation (list, stack, tree, etc.).

## Advanced Level (Architecture & Anti-Patterns)

21. **What is the difference between Dependency Injection (DI) and Inversion of Control (IoC)?**
    *   **Answer:** IoC is the principle (the "what") where the control flow of a program is inverted: instead of the programmer calling the framework, the framework calls the programmer's code. DI is a specific design pattern (the "how") to implement IoC, where dependencies are "injected" into a component (via constructor, setter, or interface) rather than the component creating them itself.

22. **Compare the Chain of Responsibility pattern with the Decorator pattern.**
    *   **Answer:**
        *   **Decorator:** Adds responsibilities/behavior to an object dynamically.
        *   **Chain of Responsibility:** Passes a request along a chain of handlers. A handler decides either to process the request or to pass it to the next handler. It isn't essentially adding behavior to the object, but finding the right handler for an action.

23. **What is the Bridge Pattern and how does it differ from Adapter?**
    *   **Answer:**
        *   **Bridge:** Split a large class or a set of closely related classes into two separate hierarchies—abstraction and implementation—which can be developed independently. It is designed up-front.
        *   **Adapter:** Used to make unrelated classes work together. It is usually applied *after* the components are designed (retrofitting).

24. **Mediator vs. Observer: When to use which?**
    *   **Answer:**
        *   **Observer:** Establishes a dynamic one-to-many connection. Good for decentralized communication where the subject doesn't care who is listening.
        *   **Mediator:** Centralizes communication between components. Components don't talk to each other directly; they talk to the mediator. Use this when dependencies between components become too chaotic (like a spaghetti graph).

25. **What is the Memento Pattern?**
    *   **Answer:** A behavioral pattern that lets you save and restore the previous state of an object without revealing the details of its implementation. Used heavily in building "Undo" mechanisms in editors (Ctrl+Z).

26. **Explain the Template Method Pattern.**
    *   **Answer:** Defines the skeleton of an algorithm in the superclass but lets subclasses override specific steps of the algorithm without changing its structure. (e.g., a DataMiner class having `openFile()`, `extractData()`, `parseData()`, `closeFile()` where `parseData()` is abstract).

27. **What is the Flyweight Pattern?**
    *   **Answer:** A structural pattern that lets you fit more objects into the available amount of RAM by sharing common parts of state (intrinsic state) between multiple objects instead of keeping all of the data in each object. Used in text editors to render characters.

28. **What is the "God Object" Anti-Pattern?**
    *   **Answer:** A class that knows too much or does too much. It violates the Single Responsibility Principle. It usually imports 50+ packages/modules and has thousands of lines of code, making it a nightmare to test and maintain.

29. **What is the difference between Abstract Factory and Factory Method?**
    *   **Answer:**
        *   **Factory Method:** Uses inheritance. A method in a base class is overridden by a subclass to create a specific object. (Creates one product).
        *   **Abstract Factory:** Uses object composition. An object is created that has multiple factory methods to create a *family* of related products (e.g., createButton, createCheckbox for Windows vs. MacOS).

30. **What is the Visitor Pattern?**
    *   **Answer:** A behavioral pattern that lets you separate algorithms from the objects on which they operate. It relies on a technique called **Double Dispatch**. It allows adding new operations to existing object structures without modifying the structures.
