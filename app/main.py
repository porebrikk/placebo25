from fastapi import FastAPI
from uvicorn import run

from common.database import Base, engine
from departments.departments_rst import router as department_router
from departments.employees_rst import router as employee_router
from departments.roles_rst import router as role_router
from departments.permissions_rst import router as permission_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(department_router)
app.include_router(employee_router)
app.include_router(role_router)
app.include_router(permission_router)


if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=8000, reload=True)
