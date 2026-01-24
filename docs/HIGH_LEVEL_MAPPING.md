# High-Level Structural Mapping

This document maps the **Main Elements** of the Requirements Document to the **Architectural Components** of the OpenAPI (YAML) file.

## 1. Conceptual Hierarchy

| Requirements Layer | YAML Layer | Concept |
| :--- | :--- | :--- |
| **User Stories** | **Paths / Endpoints** | *Behaviors & Actions* |
| **Logical Data Model** | **Components / Schemas** | *Data Structures* |
| **Business Rules** | **Response Codes & Descriptions** | *Logic & Constraints* |
| **NFRs (Security)** | **Security Schemes** | *Protection* |

## 2. Element-to-Element Mapping

### A. User Stories $\rightarrow$ Paths
*Mapping functional goals to technical entry points.*

| User Story Group | YAML Path |
| :--- | :--- |
| **List Operations** (Create, Read, Update, Delete Lists) | `/lists` & `/lists/{id}` |
| **Task Operations** (Create, Read, Update, Delete Tasks) | `/lists/{list_id}/tasks` & `.../tasks/{task_id}` |
| **Auth Operations** (Register, Get Token) | `/auth/clients` & `/auth/token` |

### B. Logical Data Model $\rightarrow$ Components
*Mapping business entities to API data contracts.*

| Requirement Entity | YAML Schema (`components/schemas`) |
| :--- | :--- |
| **List** | `ToDoList` |
| **Task** | `Task` |
| **Client** | `Client` |
| **Auth Token** | `TokenResponse` |