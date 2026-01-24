# Requirements to API Traceability Matrix

This document maps the Business Requirements defined in `REQUIREMENTS.md` to the API Specification in `index.yaml`.

## 1. Data Model Mapping

Mapping Entities in `REQUIREMENTS.md` (Section 2) to Schemas in `index.yaml`.

| Requirement Entity | Field | Req Rule (Body) | YAML Schema Property | Status |
| :--- | :--- | :--- | :--- | :--- |
| **2.1 List** | `id` | Read-only | `ToDoList.id` (readOnly: true) | ✅ Match |
| | `user_id` | **No (System)** | **Implicit / Handled via Auth** | ✅ Match |
| | `title` | Required | `ToDoList.title` (required: true) | ✅ Match |
| | `description` | Optional | `ToDoList.description` | ✅ Match |
| | `status` | Enum, Default 'Active' | `ToDoList.status` (enum, default: Active) | ✅ Match |
| | `created_at` | Read-only | `ToDoList.created_at` (readOnly: true) | ✅ Match |
| **2.2 Task** | `list_id` | Required (FK) | `Task.list_id` | ✅ Match |
| | `title` | Required | `Task.title` | ✅ Match |
| | `status` | Enum, Default 'New' | `Task.status` (enum, default: New) | ✅ Match |
| | `priority` | Enum | `Task.priority` (enum) | ✅ Match |
| | `due_date` | Date | `Task.due_date` (format: date) | ✅ Match |
| **2.3 Client** | `client_id` | Required | `Client.client_id` | ✅ Match |
| | `client_secret` | Required | `Client.client_secret` | ✅ Match |

## 2. Functional Mapping

Mapping User Stories in `REQUIREMENTS.md` (Section 4) to Endpoints in `index.yaml`.

| Story ID | User Story | YAML Path | Method | Key Logic Mapped in YAML |
| :--- | :--- | :--- | :--- | :--- |
| **Story 1** | Create List | `/lists` | `POST` | `required: [title]`, Default status 'Active'. |
| **Story 2** | View All Lists | `/lists` | `GET` | Pagination params (`page`, `limit`) included. |
| **Story 3** | View Specific List | `/lists/{id}` | `GET` | 404 Response defined for missing/deleted lists. |
| **Story 4** | Update List | `/lists/{id}` | `PATCH` | Schema allows updating Title/Description. |
| **Story 5** | Defer List | `/lists/{id}` | `PATCH` | **409 Conflict** response defined for lists with In-Progress tasks. |
| **Story 6** | Delete List | `/lists/{id}` | `DELETE` | **409 Conflict** response defined for lists with active tasks. |
| **Story 7** | Create Task | `/lists/{list_id}/tasks` | `POST` | **409 Conflict** if Parent List is Deleted/Deferred. |
| **Story 8** | View Task | `/lists/{list_id}/tasks/{task_id}` | `GET` | 404 defined for deleted tasks. |
| **Story 9** | View Tasks in List | `/lists/{list_id}/tasks` | `GET` | Pagination params included. |
| **Story 10** | Update Task | `/lists/{list_id}/tasks/{task_id}` | `PATCH` | **400 Bad Request** for 'New' status transition; **409** for locked list. |
| **Story 11** | Defer Task | `/lists/{list_id}/tasks/{task_id}` | `PATCH` | Covered by Update Task endpoint. |
| **Story 12** | Delete Task | `/lists/{list_id}/tasks/{task_id}` | `DELETE` | Returns 204 on success. |
| **Story 13** | Register Client | `/auth/clients` | `POST` | Matches Client schema. |
| **Story 14** | Obtain Token | `/auth/token` | `POST` | Matches TokenRequest/Response schemas. |

## 3. Business Rules Mapping

Mapping Business Rules in `REQUIREMENTS.md` (Section 3) to Logic/Validation in `index.yaml`.

| Rule Section | Business Rule | YAML Implementation (Location & Logic) | Status |
| :--- | :--- | :--- | :--- |
| **3.1 Lifecycle** | **List Immutability**<br>*(Cannot modify or add tasks to Deleted/Deferred lists)* | **`POST /lists/{list_id}/tasks`**: Returns `409 Conflict` if Parent List is Deleted or Deferred.<br>**`PATCH /lists/{id}`**: Returns `404` if list is Deleted. | ✅ Match |
| | **Task Immutability**<br>*(Cannot update Deleted/Deferred tasks)* | **`PATCH .../tasks/{task_id}`**: Description states "Cannot update if Task is 'Deferred' -> Returns 404". Returns `404` if Deleted. | ✅ Match |
| | **'New' Status Constraint**<br>*(Cannot manually update status back to 'New')* | **`PATCH .../tasks/{task_id}`**: Description explicitly states "Cannot set status to 'New' -> Returns 400". | ✅ Match |
| **3.2 Deletion** | **Soft Delete**<br>*(Change status to 'Deleted', don't remove data)* | **`DELETE /lists/{id}`** & **`DELETE .../tasks/{id}`**: Descriptions confirm behavior is "Changes status to 'Deleted'". | ✅ Match |
| | **List Deferral Pre-condition**<br>*(Cannot defer if tasks are In-Progress)* | **`PATCH /lists/{id}`**: Explicitly documents: "If 'In-Progress' tasks exist, returns **409 Conflict**". | ✅ Match |
| | **List Deletion Pre-condition**<br>*(Cannot delete if active tasks exist)* | **`DELETE /lists/{id}`**: Explicitly documents: "Returns **409 Conflict** if active tasks exist." | ✅ Match |
| | **Idempotency**<br>*(Deleting an already deleted item is a success)* | **`DELETE /lists/{id}`**: Description notes "Returns 204 if successful (Idempotent)". | ✅ Match |
| **3.3 Integrity** | **Required Fields**<br>*(Title is mandatory)* | **Schemas**: `ToDoList` and `Task` both have `required: [title]`.<br>**`POST` Endpoints**: Define `400 Bad Request` for missing title. | ✅ Match |
| | **Parent Existence**<br>*(Tasks require an Active Parent List)* | **`POST .../tasks`** & **`PATCH .../tasks/{id}`**: Both define `409 Conflict` responses if the Parent List is locked (Deleted/Deferred). | ✅ Match |

## 4. Non-Functional Requirements (NFR) Mapping

| NFR Section | Requirement | YAML Implementation | Status |
| :--- | :--- | :--- | :--- |
| **5.1 Security** | Bearer Token Auth | `security: - bearerAuth: []` | ✅ Match |
| **5.2 Pagination** | `limit`, `offset` (or page) | Parameters `page`, `limit` in GET operations. | ✅ Match |
| **5.3 Errors** | Standard Error Format | `components/schemas/Error` | ✅ Match |
| **5.4 Versioning** | URI Versioning | `servers.url`: `.../v1` | ✅ Match |