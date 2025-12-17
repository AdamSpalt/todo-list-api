# Requirements Document: TO-DO List API

This document outlines the business goals and user stories for the TO-DO List API.

## 1. Business Goals

The primary goal of this project is to provide a simple, reliable, and programmatic interface (an API) for managing to-do lists and their tasks.

- **Problem Solved:** It solves the user problem of needing a centralized, accessible way to track their to-dos from any application.
- **Core Functionality:** The API will serve as the backend foundation for any client application (e.g., a web app, mobile app, or command-line tool) that needs to offer task management functionality.
- **Target Audience:** Business Users / Stakeholders

## 2. User Stories

These user stories define the specific actions a consumer of our API should be able to perform. Each story will directly translate into an API endpoint.

---
### To-Do list

### Story 1: Create a To-Do List

- **As a user, I want to create a new To-Do list with a title, so that I can group and manage my list tasks.**
- **Acceptance Criteria:**
    - A To-Do list must have a `title`.
    - A To-Do list should by default have "New" status.
    - The API should return the newly created To-Do list, showing its `ID`, `Title`, `Description`, `Status`, `Due Date`, and `Creation Date`.
    - The API should return the To-Do list showing ID, Title, Creation Date, and Status.

### Story 2: View All To-Do lists

- **As a user, I want to retrieve a list of all my To-Do lists, so that I can see and review them.**
- **Acceptance Criteria:**
    - The API should return a list (array) of lists that are not in 'Deleted' status.
    - Each item in the returned list should contain the To-Do list's ID, Title, Description, Status, Due Date, and Creation Date.
    - If there are no lists, the API should return an empty list.

### Story 3: View To-Do list

- **As a user, I want to retrieve a To-Do list, so that I can review it.**
- **Acceptance Criteria:**
    - The API call must specify the unique ID of the To-Do list to be retrieved.
    - If a To-Do list with the given ID exists and is not in a 'Deleted' status, the API should return its full details.
    - The returned data must include the list's `ID`, `Title`, `Description`, `Status`, `Due Date`, and `Creation Date`.
    - If no list exists with the given ID, or if the list is in a 'Deleted' status, the API should return a 404 Not Found error.

### Story 4: Update To-Do list

- **As a user, I want to update a To-Do list, so that it can be up to date.**
- **Acceptance Criteria:**
    - The API call must specify the unique ID of the To-Do list to be updated.
    - The API call must include a request body containing the fields to be updated. The updatable fields are `title`, `description`, and `due_date`.
    - If a To-Do list with the given ID exists and is not in a 'Deleted' status, the API should update it with the provided data.
    - Upon a successful update, the API should return the complete and updated To-Do list details.
    - If no list exists with the given ID, or if the list is in a 'Deleted' status, the API should return a 404 Not Found error.

### Story 5: Defer To-Do list

- **As a user, I want to defer a To-Do list, so that it is set as obsolete**
- **Acceptance Criteria:**
    - The API call must specify the unique ID of the To-Do list to be deferred.
    - A success will change the list's status to 'Deferred'.
    - If a list with the given ID contains any tasks with a status In-Progress, the API should return a 409 Conflict error.
    - If no list exists with the given ID, or if the list is in a 'Deleted' status, the API should return a 404 Not Found error.
    - Upon a successful deferral (including when the list was already in a 'Deferred' state), the API should return a 204 No Content success status.

### Story 6: Delete To-Do list

- **As a user, I want to delete a To-Do list, so that it can be removed.**
- **Acceptance Criteria:**
    - The API call must specify the unique ID of the To-Do list to be deleted.
    - A successful "deletion" will change the list's status to 'Deleted'.
    - If a list with the given ID contains any tasks with a status other than Completed or Deferred, the API should return a 409 Conflict error.
    - If no list exists with the given ID, the API should return a 404 Not Found error.
    - Upon a successful deletion (including when the list was already in a 'Deleted' state), the API should return a 204 No Content success status.


### Task

### Story X: Create a Task

- **As a user, I want to create a new task with a title, so that I can add new items to my to-do list.**
- **Acceptance Criteria:**
    - A task must have a `title`.
    - A new task should default to being "not completed".
    - The API should return the newly created task data upon success.

---

### Story X: View All Tasks

- **As a user, I want to retrieve a list of all my tasks, so that I can see everything I need to do.**
- **Acceptance Criteria:**
    - The API should return a list (array) of all existing tasks.
    - If there are no tasks, the API should return an empty list.

---

### Story X: View a Single Task

- **As a user, I want to view the details of a single, specific task, so that I can focus on one item.**
- **Acceptance Criteria:**
    - The user must provide a unique identifier for the task they want to see.
    - If the task is found, the API should return its complete data.
    - If no task with that ID exists, the API should return an appropriate "Not Found" error.

---

### Story X: Update a Task

- **As a user, I want to update an existing task (e.g., change its title or mark it as complete), so that I can keep my task list current.**
- **Acceptance Criteria:**
    - The user must provide the unique ID of the task to update.
    - The user can update the task's `title` and/or its `is_completed` status.
    - If the task is found and updated, the API should return the updated task data.
    - If no task with that ID exists, the API should return a "Not Found" error.

---

### Story X: Delete a Task

- **As a user, I want to delete a task, so that I can remove completed or unnecessary items from my list.**
- **Acceptance Criteria:**
    - The user must provide the unique ID of the task to delete.
    - If the task is successfully deleted, the API should return a success confirmation.
    - If no task with that ID exists, the API should return a "Not Found" error.
