# todo-list-api

A robust RESTful API for managing personal task lists and tasks, built with **FastAPI**.

## 🚀 Tech Stack

*   **Language:** Python 3.10+
*   **Framework:** FastAPI
*   **Server:** Uvicorn
*   **Validation:** Pydantic
*   **Database:** PostgreSQL (Supabase)

## ✨ Features

*   **Lists Management:** Create, Read, Update, Soft-Delete lists.
*   **Task Management:** Add tasks to lists, track status, set priorities.
*   **Business Logic:**
    *   Cannot delete lists with active tasks.
    *   Cannot defer lists with "In-Progress" tasks.
*   **Security & Performance:**
    *   **Rate Limiting:** Protects against spam.
    *   **Pagination:** Efficiently handles large datasets.
    *   **Authentication:** JWT (Supabase) + Client Credentials Flow.
*   **Documentation:** Fully documented with OpenAPI (Swagger UI).

## 🛠️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AdamSpalt/todo-list-api.git
    cd todo-list-api
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Server:**
    ```bash
    uvicorn main:app --reload
    ```

## 🔐 Authentication Guide

This API uses the **Client Credentials Flow** for machine-to-machine authentication.

### 1. Setup (Admin Only)
First, you must generate a "Master Token" to register new clients.
1.  Run the local script: `python generate_token.py`
2.  Copy the generated JWT.

### 2. Register a Client
Use your Master Token to create credentials for a partner.
*   **Endpoint:** `POST /v1/auth/clients`
*   **Header:** `Authorization: Bearer <YOUR_MASTER_TOKEN>`
*   **Body:**
    ```json
    {
      "client_id": "my-app",
      "client_secret": "strong-password",
      "name": "My Frontend App"
    }
    ```

### 3. Get an Access Token
Now, the partner can log in to get a temporary access token.
*   **Endpoint:** `POST /v1/auth/token`
*   **Body:**
    ```json
    {
      "client_id": "my-app",
      "client_secret": "strong-password"
    }
    ```
*   **Response:** Returns an `access_token` (valid for 24 hours).

### 4. Access Protected Data
Use the Access Token to call API endpoints.
*   **Header:** `Authorization: Bearer <ACCESS_TOKEN>`

## 📖 API Documentation

### ☁️ Live Deployment
*   **Swagger UI (Interactive):** https://todo-list-api.vercel.app/docs
*   **ReDoc (Static):** https://todo-list-api.vercel.app/redoc

### 🧪 Postman Collection

[![Run in Postman](https://run.pstmn.io/button.svg)](https://raw.githubusercontent.com/AdamSpalt/todo-list-api/refs/heads/main/postman/collections/ToDo%20API%20-%20Public.json)

### 📄 Design & Specifications
*   **API Contract (YAML):** `index.yaml` - The strict architectural blueprint.
*   **Requirements:** `docs/REQUIREMENTS.md` - The business logic and user stories.