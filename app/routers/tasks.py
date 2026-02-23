from db.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models.audit_log import AuditLog
from models.task import Task, TaskStatus
from models.user import User
from routers.auth import get_admin_user, get_current_user
from schemas.task import TaskCreate, TaskResponse, TaskUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_task = Task(
        title=task.title, description=task.description, owner_id=current_user.id
    )

    db.add(new_task)
    db.flush()

    log = AuditLog(
        action="create",
        entity_type="task",
        entity_id=new_task.id,
        user_id=current_user.id,
    )

    db.add(log)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 10,
    status: TaskStatus | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    if current_user.is_admin:
        query = db.query(Task).filter(Task.is_deleted.is_(False))
    else:
        query = db.query(Task).filter(
            Task.owner_id == current_user.id, Task.is_deleted.is_(False)
        )

    if status:
        query = query.filter(Task.status == status)

    return query.offset(skip).limit(limit).all()


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted.is_(False)).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not current_user.is_admin and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if task_update.title is not None:
        task.title = task_update.title

    if task_update.description is not None:
        task.description = task_update.description

    if task_update.status is not None:
        task.status = task_update.status

    log = AuditLog(
        action="update", entity_type="task", entity_id=task.id, user_id=current_user.id
    )

    db.add(log)
    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not current_user.is_admin and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task.is_deleted = True

    log = AuditLog(
        action="delete", entity_type="task", entity_id=task.id, user_id=current_user.id
    )

    db.add(log)
    db.commit()

    return {"message": "Task soft deleted"}


@router.get("/admin/users", tags=["Admin"])
def list_all_users(
    admin: User = Depends(get_admin_user), db: Session = Depends(get_db)
):
    return db.query(User).all()


@router.put("/admin/restore/{task_id}", tags=["Admin"])
def restore_task(
    task_id: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted.is_(True)).first()

    if not task:
        raise HTTPException(status_code=404, detail="Deleted task not found")

    task.is_deleted = False

    log = AuditLog(
        action="restore", entity_type="task", entity_id=task.id, user_id=admin.id
    )

    db.add(log)
    db.commit()
    db.refresh(task)

    return {"message": "Task restored"}


@router.get("/admin/audit-logs", tags=["Admin"])
def get_audit_logs(
    admin: User = Depends(get_admin_user), db: Session = Depends(get_db)
):
    return db.query(AuditLog).all()
