# Requirements Document: To-Do List API

This document outlines the business goals, user stories, data model, and business rules for the To-Do List API.

## 1. Business Goals

The primary goal of this project is to provide a simple, reliable, and programmatic interface (an API) for managing to-do lists and their tasks.

- **Problem Solved:** It solves the user problem of needing a centralized, accessible way to track their to-dos from any application.
- **Core Functionality:** The API will serve as the backend foundation for any client application (e.g., a web app, mobile app, or command-line tool) that needs to offer task management functionality.
- **Target Audience:** Business Users / Stakeholders

## 2. Data Model

This is the single source of truth for all data entities in the system.

### 2.1. List Entity

| Field         | Type    | Constraints                               |
|---------------|---------|-------------------------------------------|
| `id`          | String  | UUID, Read-only                           |
| `title`       | String  | Required, Writable on create/update       |
| `description` | String  | Optional, Writable on create/update       |
| `status`      | String  | Read-only, Derived from task statuses     |
| `created_at`  | String  | Timestamp, Read-only                      |

### 2.2. Task Entity

| Field         | Type    | Constraints                               |
|---------------|---------|-------------------------------------------|
| `id`          | String  | UUID, Read-only                           |
| `list_id`     | String  | UUID, Foreign Key to List                 |
| `title`       | String  | Required, Writable on create/update       |
| `description` | String  | Optional, Writable on create/update       |
| `status`      | String  | Enum ('New', 'In-Progress', 'Completed', 'Deferred', 'Deleted') |
| `priority`    | String  | Enum ('Low', 'Medium', 'High')            |
| `due_date`    | Date    | Optional                                  |
| `created_at`  | String  | Timestamp, Read-only                      |
| `updated_at`  | String  | Timestamp, Read-only                      |

## 3. Key Business Rules Summary

This section provides a consolidated overview of critical business rules. For detailed context and specific application, refer to the Acceptance Criteria of the referenced User Story.

### 3.1. Status Transitions & Constraints

*   **List Status Derivation:** A List's `status` is derived from the `status` of its constituent Tasks. (See: Story 1, AC 2; Story 4, AC 2)
*   **Task Status Immutability (New):** A Task's `status` cannot be reverted to 'New' after creation. (See: Story 9, AC 2)
*   **Task Status Immutability (Deleted/Deferred):** Tasks in 'Deleted' or 'Deferred' status cannot be updated. (See: Story 9, AC 3)
*   **List Immutability (Deleted/Deferred):** Tasks within a 'Deleted' or 'Deferred' List cannot be modified. (See: Story 9, AC 4; Story 10, AC 4; Story 11, AC 4; Story 12, AC 4)

### 3.2. Data Validation

*   **Required Fields:** `title` is required for both List and Task creation. (See: Story 1, AC 1; Story 5, AC 1)
*   **ID Uniqueness:** All `id` fields must be unique. (Implicit in all operations)

### 3.3. Deletion & Deferral Logic

*   **Soft Delete:** Both Lists and Tasks are soft-deleted by changing their `status` to 'Deleted'. (See: Story 4, AC 1; Story 12, AC 1)
*   **List Deletion Pre-conditions:** A List cannot be deleted if it contains any active (non-Completed, non-Deferred) Tasks. (See: Story 4, AC 3)
*   **Idempotency:** Deleting or deferring an already deleted/deferred entity is a successful no-op. (See: Story 4, AC 5; Story 11, AC 2; Story 12, AC 2)

## 4. User Stories (Functional Requirements)

### 4.1. List Management

#### Story 1: Create a To-Do List
- **As a user, I want to create a new To-Do list, so that I can group and manage my tasks.**
- **Acceptance Criteria:**
    - The API call must include a `title`.
    - A new list will have a `status` of 'New'.
    - Upon successful creation, the API should return a `201 Created` status with the newly created list data.
    - If a required field (e.g., `title`) is missing, the API should return a `400 Bad Request` error.

#### Story 2: Get All To-Do Lists
- **As a user, I want to retrieve all my To-Do lists, so that I can see an overview of my tasks.**
- **Acceptance Criteria:**
    - The API should return a list of all To-Do lists, including their `id`, `title`, `description`, and `status`.
    - The API should return a `200 OK` status.
    - If no lists exist, an empty array should be returned with a `200 OK` status.

#### Story 3: Get a Specific To-Do List
- **As a user, I want to retrieve a specific To-Do list by its ID, so that I can view its details.**
- **Acceptance Criteria:**
    - The API call must specify the unique `ID` of the To-Do list.
    - Upon success, the API should return a `200 OK` status with the list's data.
    - If no To-Do list exists with the given ID, the API should return a `404 Not Found` error.

#### Story 4: Delete a To-Do List
- **As a user, I want to delete a To-Do list, so that it is removed from my view.**
- **Acceptance Criteria:**
    - The API call must specify the unique `ID` of the To-Do list to be deleted.
    - Upon a successful deletion, the list's `status` is changed to 'Deleted'. The API should return a `204 No Content` success status. This includes cases where the list was already in a 'Deleted' state.
    - If the list contains any tasks with a `status` other than 'Completed' or 'Deferred', the API should return a `409 Conflict` error.
    - If no To-Do list exists with the given ID, the API should return a `404 Not Found` error.

### 4.2. Task Management

#### Story 5: Create a Task
- **As a user, I want to create a new task within a To-Do list, so that I can add work items.**
- **Acceptance Criteria:**
    - The API call must specify the unique `ID` of the parent To-Do list.
    - The API call must include a `title` for the task.
    - A new task will have a `status` of 'New'.
    - Upon successful creation, the API should return a `201 Created` status with the newly created task data.
    - If the parent list `ID` does not exist, or if the parent list is in a 'Deleted' or 'Deferred' status, the API should return a `404 Not Found` error.
    - If a required field (e.g., `title`) is missing, the API should return a `400 Bad Request` error.

#### Story 6: Get All Tasks in a List
- **As a user, I want to retrieve all tasks for a specific To-Do list, so that I can see all items I need to do.**
- **Acceptance Criteria:**
    - The API call must specify the unique `ID` of the parent To-Do list.
    - The API should return a list of all tasks associated with the given To-Do list, including their `id`, `title`, `description`, `status`, `priority`, and `due_date`.
    - The API should return a `200 OK` status.
    - If the parent list `ID` does not exist, the API should return a `404 Not Found` error.
    - If no tasks exist for the given list, an empty array should be returned with a `200 OK` status.

#### Story 7: Get a Specific Task
- **As a user, I want to retrieve a specific task by its ID, so that I can view its details.**
- **Acceptance Criteria:**
    - The API call must specify the unique `ID` of the parent To-Do list and the unique `ID` of the task.
    - Upon success, the API should return a `200 OK` status with the task's data.
    - If the specified parent list `ID` or task `ID` does not exist, the API should return a `404 Not Found` error.

#### Story 8: Mark a Task as Completed
- **As a user, I want to mark a task as completed, so that I know it's done.**
- **Acceptance Criteria:**
    - The API call must specify the unique `ID` of the parent To-Do list and the unique `ID` of the task to be marked as completed.
    - Upon a successful completion, the task's `status` is changed to 'Completed'. The API should return a `204 No Content` success status. This includes cases where the task was already in a 'Completed' state.
    - If the specified parent list `ID` or task `ID` does not exist, or if the task is in a 'Deleted' status, the API should return a `404 Not Found` error.
    - If the parent list is in a 'Deleted' or 'Deferred' status, the API should return a `409 Conflict` error, as its tasks cannot be modified.

#### Story 9: Update a Task
- **As a user, I want to update the details of a task, so that I can keep its information current.**
- **Acceptance Criteria:**
    - The API call must specify the unique `ID` of the parent To-Do list and the unique `ID` of the task to be updated.
    - The API should allow updating the `title`, `description`, `priority`, and `due_date`.
    - The API must reject any attempt to change the `status` back to 'New' if it's not already 'New'.
    - If the specified parent list `ID` or task `ID` does not exist, or if the task is in a 'Deleted' or 'Deferred' status, the API should return a `404 Not Found` error.
    - If the parent list is in a 'Deleted' or 'Deferred' status, the API should return a `409 Conflict` error, as its tasks cannot be modified.
    - Upon a successful update, the API should return a `200 OK` status with the updated task data.

#### Story 10: Defer a Task
- **As a user, I want to defer a task, so that it is marked as obsolete but not deleted.**
- **Acceptance Criteria:**
    - The API call must specify the unique `ID` of the parent To-Do list and the unique `ID` of the task to be deferred.
    - Upon a successful deferral, the task's `status` is changed to 'Deferred'. The API should return a `204 No Content` success status. This includes cases where the task was already in a 'Deferred' state.
    - If the specified parent list `ID` or task `ID` does not exist, or if the task is in a 'Deleted' status, the API should return a `404 Not Found` error.
    - If the parent list is in a 'Deleted' or 'Deferred' status, the API should return a `409 Conflict` error, as its tasks cannot be modified.

#### Story 11: Delete a Task
- **As a user, I want to delete a task, so that it can be removed from my To-Do list.**
- **Acceptance Criteria:**
    - The API call must specify the unique `ID` of the parent To-Do list and the unique `ID` of the task to be deleted.
    - Upon a successful deletion, the task's `status` is changed to 'Deleted'. The API should return a `204 No Content` success status. This includes cases where the task was already in a 'Deleted' state.
    - If the specified parent list `ID` or task `ID` does not exist, the API should return a `404 Not Found` error.
