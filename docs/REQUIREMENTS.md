# Requirements Document: To-Do List API

This document outlines the business goals, user stories, data model, and business rules for the To-Do List API.

## 1. Business Goals

The primary goal of this project is to provide a simple, reliable, and programmatic interface (an API) for managing to-do lists and their tasks.

- **Problem Solved:** It solves the user problem of needing a centralized, accessible way to track their to-dos from any application.
- **Core Functionality:** The API will serve as the backend foundation for any client application (e.g., a web app, mobile app, or command-line tool) that needs to offer task management functionality.
- **Target Audience:** Business Users / Stakeholders

2. Data Model
This is the single source of truth for all data entities in the system.

2.1. List Entity
Field	Type	Constraints
id	String	UUID, Read-only, System-generated
title	String	Required, Writable on create/update
description	String	Optional, Writable on create/update
status	String	Enum ('New', 'Deferred', 'Deleted'), Writable via specific actions
created_at	Timestamp	Read-only, System-generated
updated_at	Timestamp	Read-only, System-generated
2.2. Task Entity
Field	Type	Constraints
id	String	UUID, Read-only, System-generated
list_id	String	UUID, Foreign Key to List, Required on create
title	String	Required, Writable on create/update
description	String	Optional, Writable on create/update
status	String	Enum ('New', 'In-Progress', 'Completed', 'Deferred', 'Deleted')
priority	String	Enum ('Low', 'Medium', 'High'), Optional
due_date	Date	Optional, Writable on create/update
created_at	Timestamp	Read-only, System-generated
updated_at	Timestamp	Read-only, System-generated
3. Key Business Rules Summary
This section provides a consolidated overview of critical business rules. For detailed context, refer to the Acceptance Criteria of the referenced User Story.

3.1. Status & Lifecycle
List Immutability: Lists in 'Deleted' or 'Deferred' status cannot be modified, and new tasks cannot be created in them. (See: Story 4, 5, 6, 7)
Task Immutability: Tasks in 'Deleted' or 'Deferred' status cannot be updated. (See: Story 10)
Task Status - 'New' Constraint: A Task's status cannot be set to 'New' via an update action; this status is reserved for creation. (See: Story 10)
3.2. Deletion & Deferral Logic
Soft Delete: Both Lists and Tasks are "soft-deleted" by changing their status to 'Deleted'. (See: Story 6, 12)
List Deferral Pre-condition: A List cannot be deferred if it contains any 'In-Progress' tasks. (See: Story 5)
List Deletion Pre-condition: A List cannot be deleted if it contains any tasks that are not 'Completed' or 'Deferred'. (See: Story 6)
Idempotency: Deleting or deferring an entity that is already in the target state is a successful no-op. (See: Story 5, 6, 11, 12)
3.3. Data Validation & Integrity
Required Fields: title is required for both List and Task creation. (See: Story 1, 7)
Parent Existence: A Task can only be created or modified within an existing, active (not 'Deleted' or 'Deferred') List. (See: Story 7, 10, 11)
4. User Stories (Functional Requirements)
4.1. To-Do List Management
Story 1: Create a To-Do List
As a user, I want to create a new To-Do list, so that I can group and manage my list tasks.
Acceptance Criteria:
The request body must contain a title.
The request body may optionally contain a description.
A new list will have its status set to 'New' by default.
Upon successful creation, the API should return a 201 Created status with the complete data for the new list.
Story 2: View All To-Do lists
As a user, I want to retrieve a list of all my To-Do lists, so that I can see and review them.
Acceptance Criteria:
The API should return a list (array) of all lists that are not in 'Deleted' status.
If no lists exist, the API should return an empty list with a 200 OK status.
Each item in the returned list should contain the To-Do list's full details.
Story 3: View a Specific To-Do list
As a user, I want to retrieve a To-Do list, so that I can review it.
Acceptance Criteria:
The API call must specify the unique ID of the To-Do list.
If a list with the given ID exists and is not in a 'Deleted' status, the API should return its full details with a 200 OK status.
If no list exists with the given ID, or if the list is in a 'Deleted' status, the API should return a 404 Not Found error.
Story 4: Update a To-Do list
As a user, I want to update a To-Do list, so that it can be up to date.
Acceptance Criteria:
The API call must specify the unique ID of the To-Do list.
The updatable fields are title and description.
If a list with the given ID exists and is not in a 'Deleted' status, the API should update it.
Upon a successful update, the API should return the complete, updated list details with a 200 OK status.
If no list exists with the given ID, or if the list is in a 'Deleted' status, the API should return a 404 Not Found error.
Story 5: Defer a To-Do list
As a user, I want to defer a To-Do list, so that it is set as obsolete.
Acceptance Criteria:
The API call must specify the unique ID of the To-Do list.
Upon success, the list's status is changed to 'Deferred'.
If the list contains any tasks with a status of 'In-Progress', the API should return a 409 Conflict error.
If no list exists with the given ID, or if the list is in a 'Deleted' status, the API should return a 404 Not Found error.
Upon a successful deferral (including when the list was already 'Deferred'), the API should return a 204 No Content status.
Story 6: Delete a To-Do list
As a user, I want to delete a To-Do list, so that it can be removed.
Acceptance Criteria:
The API call must specify the unique ID of the To-Do list.
Upon success, the list's status is changed to 'Deleted'.
If the list contains any tasks with a status other than 'Completed' or 'Deferred', the API should return a 409 Conflict error.
If no list exists with the given ID, the API should return a 404 Not Found error.
Upon a successful deletion (including when the list was already 'Deleted'), the API should return a 204 No Content status.
4.2. Task Management
(This section remains unchanged)

Story 7: Create a Task
As a user, I want to create a new To-Do list Task, so that I can plan and trace my work.
Acceptance Criteria:
The API call must specify the parent list_id.
The request body must contain a title.
The request body may optionally contain a description, priority, and due_date.
A new task will have its status set to 'New' by default.
Upon successful creation, the API should return a 201 Created status with the complete data for the new task.
If the title is missing, the API should return a 400 Bad Request error.
If the parent list_id does not exist, the API should return a 404 Not Found error.
If the parent list is in a 'Deleted' or 'Deferred' status, the API should return a 409 Conflict error.
Story 8: View a Single Task
As a user, I want to view the details of a single, specific task, so that I can focus on one item.
Acceptance Criteria:
The API call must specify the parent list_id and the task id.
If the task exists and is not in a 'Deleted' status, the API should return its full details with a 200 OK status.
If the parent list or task ID does not exist, or if the task is in a 'Deleted' status, the API should return a 404 Not Found error.
Story 9: View All Tasks in a List
As a user, I want to retrieve a list of all my To-Do list tasks, so that I can see everything I need to do.
Acceptance Criteria:
The API call must specify the parent list_id.
The API should return a list of all tasks in that list that are not in 'Deleted' status.
If no tasks exist, the API should return an empty list with a 200 OK status.
If the parent list_id does not exist, or if the list is in a 'Deleted' status, the API should return a 404 Not Found error.
Story 10: Update a Task
As a user, I want to update a Task, so that it can be up to date.
Acceptance Criteria:
The API call must specify the parent list_id and the task id.
The updatable fields are title, description, status, priority, and due_date.
If the task exists and is not in a 'Deleted' or 'Deferred' status, the API should update it.
Upon a successful update, the API should return the complete, updated task details with a 200 OK status.
If the request attempts to set the status to 'New', the API should return a 400 Bad Request error.
If the parent list is in a 'Deleted' or 'Deferred' status, the API should return a 409 Conflict error.
If the parent list or task ID does not exist, or if the task is in a 'Deleted' or 'Deferred' status, the API should return a 404 Not Found error.
Story 11: Defer a Task
As a user, I want to defer a Task, so that it is set as obsolete.
Acceptance Criteria:
The API call must specify the parent list_id and the task id.
Upon success, the task's status is changed to 'Deferred'.
If the parent list or task ID does not exist, or if the task is in a 'Deleted' status, the API should return a 404 Not Found error.
If the parent list is in a 'Deleted' or 'Deferred' status, the API should return a 409 Conflict error.
Upon a successful deferral (including when the task was already 'Deferred'), the API should return a 204 No Content status.
Story 12: Delete a Task
As a user, I want to delete a Task, so that it can be removed from the To-Do list.
Acceptance Criteria:
The API call must specify the parent list_id and the task id.
Upon success, the task's status is changed to 'Deleted'.
If the parent list or task ID does not exist, the API should return a 404 Not Found error.
Upon a successful deletion (including when the task was already 'Deleted'), the API should return a 204 No Content status.
