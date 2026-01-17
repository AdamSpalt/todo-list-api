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
    git clone https://github.com/<YOUR_USERNAME>/todo-list-api.git
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

## 📖 API Documentation

Once the server is running, access the interactive API docs at:
*   **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
