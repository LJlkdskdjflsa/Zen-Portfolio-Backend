from contextlib import contextmanager

from app.utils.database_util import SessionLocal


# For FastAPI dependency injection
def get_db():
    """Get a database session for FastAPI dependency injection.
    
    This function is used as a dependency in FastAPI routes.
    FastAPI will automatically handle the yielding and cleanup.
    
    Yields:
        Session: A SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit() 
    except Exception:
        db.rollback()  
        raise
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database sessions.
    
    Use this function with the 'with' statement when you need
    a database session outside of FastAPI routes.
    
    Example:
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
    
    Yields:
        Session: A SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit() 
    except Exception:
        db.rollback()  
        raise
    finally:
        db.close()


@contextmanager
def get_db_no_rollback():
    """Context manager that does not rollback on exception."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        # intentionally do not perform rollback
        raise e
    finally:
        db.close()
