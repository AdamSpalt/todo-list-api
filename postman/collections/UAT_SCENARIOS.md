# User Acceptance Testing (UAT) Scenarios

This document outlines the testing scenarios for the To-Do List API, covering standard workflows ("Happy Path") and specific business rule enforcement ("Edge Cases").

**Prerequisites:**
*   **Base URL:** Ensure your API client is pointing to the correct server (e.g., `http://localhost:8000/v1`).
*   **Authentication:** Most endpoints require a Bearer Token obtained in `AUTH-01`.

---

## Test Suite 1: Authentication & Setup
*Goal: Ensure we can authenticate to perform the rest of the tests.*

| ID | Scenario | Steps | Expected Result |
| :--- | :--- | :--- | :--- |
| **AUTH-01** | **Obtain Access Token** | 1. Send `POST /auth/token` with valid `client_id` and `client_secret`. | **200 OK**<br>Response contains `access_token`.<br>*(Save this token for subsequent requests)* |
| **AUTH-02** | **Unauthorized Access** | 1. Send `GET /lists` **without** the Authorization header. | **401 Unauthorized** |

---

## Test Suite 2: List Lifecycle (CRUD)
*Goal: Verify basic list management defined in User Stories 1, 2, 3, 4, & 6.*

| ID | Scenario | Steps | Expected Result |
| :--- | :--- | :--- | :--- |
| **LIST-01** | **Create Active List** | 1. Send `POST /lists`<br>Body: `{"title": "UAT List"}` | **201 Created**<br>`status` is "Active".<br>`id` is returned. *(Save as `{{list_id}}`)* |
| **LIST-02** | **Create List Validation** | 1. Send `POST /lists`<br>Body: `{}` (Empty body) | **400 Bad Request**<br>Message indicates missing title. |
| **LIST-03** | **View All Lists** | 1. Send `GET /lists` | **200 OK**<br>Response is an array containing "UAT List". |
| **LIST-04** | **View Specific List** | 1. Send `GET /lists/{{list_id}}` | **200 OK**<br>Returns details for "UAT List". |
| **LIST-05** | **Update List** | 1. Send `PATCH /lists/{{list_id}}`<br>Body: `{"description": "Updated Description"}` | **200 OK**<br>`description` is updated. |
| **LIST-06** | **Delete Empty List** | 1. Send `DELETE /lists/{{list_id}}` | **204 No Content**<br>List is soft-deleted. |
| **LIST-07** | **Verify Deletion** | 1. Send `GET /lists/{{list_id}}` | **404 Not Found**<br>Deleted lists should not be retrievable. |

---

## Test Suite 3: Task Lifecycle
*Goal: Verify task management defined in User Stories 7, 8, 9, 10, & 12.*

*Pre-condition: Create a new list named "Task Suite List" and save ID as `{{task_list_id}}`.*

| ID | Scenario | Steps | Expected Result |
| :--- | :--- | :--- | :--- |
| **TASK-01** | **Create Task** | 1. Send `POST /lists/{{task_list_id}}/tasks`<br>Body: `{"title": "Test Task"}` | **201 Created**<br>`status` is "New".<br>`id` is returned. *(Save as `{{task_id}}`)* |
| **TASK-02** | **View List Tasks** | 1. Send `GET /lists/{{task_list_id}}/tasks` | **200 OK**<br>Array contains "Test Task". |
| **TASK-03** | **Update Task Status** | 1. Send `PATCH .../tasks/{{task_id}}`<br>Body: `{"status": "In-Progress"}` | **200 OK**<br>`status` is now "In-Progress". |
| **TASK-04** | **Invalid Status Move** | 1. Send `PATCH .../tasks/{{task_id}}`<br>Body: `{"status": "New"}` | **400 Bad Request**<br>Cannot transition back to "New" (Story 10). |
| **TASK-05** | **Delete Task** | 1. Send `DELETE .../tasks/{{task_id}}` | **204 No Content** |
| **TASK-06** | **Verify Task Delete** | 1. Send `GET .../tasks/{{task_id}}` | **404 Not Found** |

---

## Test Suite 4: Business Rules (Complex Logic)
*Goal: Verify specific constraints regarding Deferral and Deletion logic (Stories 5, 6, 7, 11).*

### Scenario A: List Deferral Logic (Story 5)
*Rule: Cannot defer a list if it has "In-Progress" tasks.*

| ID | Scenario | Steps | Expected Result |
| :--- | :--- | :--- | :--- |
| **RULE-01** | **Setup Conflict** | 1. Create List "Defer Test".<br>2. Create Task "Blocking Task".<br>3. Update Task status to "In-Progress". | **200 OK** (for the update) |
| **RULE-02** | **Attempt Deferral** | 1. Send `PATCH /lists/{id}`<br>Body: `{"status": "Deferred"}` | **409 Conflict**<br>System prevents deferral due to In-Progress task. |
| **RULE-03** | **Resolve Conflict** | 1. Update Task status to "Completed".<br>2. Send `PATCH /lists/{id}`<br>Body: `{"status": "Deferred"}` | **200 OK**<br>List status is now "Deferred". |

### Scenario B: Parent List Locking (Story 7 & 10)
*Rule: Cannot add/edit tasks if the List is Deferred.*

| ID | Scenario | Steps | Expected Result |
| :--- | :--- | :--- | :--- |
| **RULE-04** | **Add Task to Deferred** | 1. Use the "Defer Test" list ID from RULE-03.<br>2. Send `POST /lists/{id}/tasks`<br>Body: `{"title": "Impossible Task"}` | **409 Conflict**<br>Cannot create task in Deferred list. |
| **RULE-05** | **Edit Task in Deferred** | 1. Attempt to update the "Blocking Task" inside "Defer Test" list. | **409 Conflict**<br>Cannot update task in Deferred list. |

### Scenario C: List Deletion Logic (Story 6)
*Rule: Cannot delete a list if it has Active (New/In-Progress) tasks.*

| ID | Scenario | Steps | Expected Result |
| :--- | :--- | :--- | :--- |
| **RULE-06** | **Setup Delete Block** | 1. Create List "Delete Test".<br>2. Create Task "Active Task" (Status: New). | **201 Created** |
| **RULE-07** | **Attempt Delete** | 1. Send `DELETE /lists/{id}` | **409 Conflict**<br>System prevents deletion due to active task. |
| **RULE-08** | **Resolve & Delete** | 1. Update Task status to "Completed" (or Delete the task).<br>2. Send `DELETE /lists/{id}` | **204 No Content**<br>List is successfully deleted. |