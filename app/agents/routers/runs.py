from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid

from app.db.database import get_db
from app.agents.models import Run, RunStatus
from app.agents.services.run_service import RunService

router = APIRouter(tags=["runs"])


@router.post("/threads/{thread_id}/runs")
async def create_run(
    thread_id: str,
    assistant_id: str,
    model: Optional[str] = None,
    instructions: Optional[str] = None,
    additional_instructions: Optional[str] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    temperature: Optional[float] = None,
    stream: Optional[bool] = False,
    max_prompt_tokens: Optional[int] = None,
    max_completion_tokens: Optional[int] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Create a run.
    
    Args:
        thread_id: The ID of the thread to run
        assistant_id: The ID of the assistant to use to execute this run
        model: The ID of the model to be used to execute this run
        instructions: Overrides the instructions of the assistant
        additional_instructions: Appends additional instructions at the end of the instructions for the run
        tools: Override the tools the assistant can use for this run
        metadata: Set of 16 key-value pairs for storing additional information
        temperature: What sampling temperature to use
        stream: If true, returns a stream of events that happen during the run
        max_prompt_tokens: The maximum number of prompt tokens
        max_completion_tokens: The maximum number of completion tokens
    
    Returns:
        A run object
    """
    service = RunService(db)
    
    # Convert OpenAI style IDs to UUIDs
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
        assistant_uuid = uuid.UUID(assistant_id.replace("asst_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid thread or assistant ID")
    
    # Combine instructions if additional_instructions is provided
    final_instructions = instructions
    if additional_instructions and instructions:
        final_instructions = f"{instructions}\n\n{additional_instructions}"
    elif additional_instructions:
        final_instructions = additional_instructions
    
    run = service.create_run(
        thread_id=thread_uuid,
        assistant_id=assistant_uuid,
        model=model,
        instructions=final_instructions,
        tools=tools,
        metadata=metadata or {},
        temperature=temperature,
        max_prompt_tokens=max_prompt_tokens,
        max_completion_tokens=max_completion_tokens
    )
    
    if not run:
        raise HTTPException(status_code=404, detail="Thread or assistant not found")
    
    # Queue the run for processing in the background
    background_tasks.add_task(service.process_run, run.id)
    
    # Return appropriate response based on stream parameter
    if stream:
        # TODO: Implement streaming response
        raise HTTPException(status_code=501, detail="Streaming not yet implemented")
    
    return run.to_dict()


@router.get("/threads/{thread_id}/runs")
async def list_runs(
    thread_id: str,
    limit: int = Query(20, ge=1, le=100),
    order: str = Query("desc", regex="^(asc|desc)$"),
    after: Optional[str] = None,
    before: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns a list of runs belonging to a thread.
    
    Args:
        thread_id: The ID of the thread the run belongs to
        limit: Maximum number of runs to return
        order: Sort order by created_at timestamp
        after: Cursor for pagination (run ID)
        before: Cursor for pagination (run ID)
    
    Returns:
        A list of run objects
    """
    service = RunService(db)
    
    # Convert OpenAI style thread ID to UUID
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    runs = service.list_runs(
        thread_id=thread_uuid,
        limit=limit,
        order=order,
        after=after,
        before=before
    )
    
    # Format response according to OpenAI API
    return {
        "object": "list",
        "data": [run.to_dict() for run in runs],
        "first_id": runs[0].id if runs else None,
        "last_id": runs[-1].id if runs else None,
        "has_more": len(runs) == limit
    }


@router.get("/threads/{thread_id}/runs/{run_id}")
async def retrieve_run(
    thread_id: str,
    run_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves a run.
    
    Args:
        thread_id: The ID of the thread that was run
        run_id: The ID of the run to retrieve
    
    Returns:
        The run object matching the specified ID
    """
    service = RunService(db)
    
    # Convert OpenAI style IDs to UUIDs
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
        run_uuid = uuid.UUID(run_id.replace("run_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run = service.get_run(run_uuid, thread_uuid)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return run.to_dict()


@router.post("/threads/{thread_id}/runs/{run_id}")
async def modify_run(
    thread_id: str,
    run_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Modifies a run.
    
    Args:
        thread_id: The ID of the thread that was run
        run_id: The ID of the run to modify
        metadata: Set of 16 key-value pairs for storing additional information
    
    Returns:
        The modified run object
    """
    service = RunService(db)
    
    # Convert OpenAI style IDs to UUIDs
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
        run_uuid = uuid.UUID(run_id.replace("run_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run = service.update_run(
        run_id=run_uuid,
        thread_id=thread_uuid,
        metadata=metadata
    )
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return run.to_dict()


@router.post("/threads/{thread_id}/runs/{run_id}/cancel")
async def cancel_run(
    thread_id: str,
    run_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancels a run that is in_progress.
    
    Args:
        thread_id: The ID of the thread to which this run belongs
        run_id: The ID of the run to cancel
    
    Returns:
        The modified run object matching the specified ID
    """
    service = RunService(db)
    
    # Convert OpenAI style IDs to UUIDs
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
        run_uuid = uuid.UUID(run_id.replace("run_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run = service.cancel_run(run_uuid, thread_uuid)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found or cannot be cancelled")
    
    return run.to_dict()


@router.get("/threads/{thread_id}/runs/{run_id}/steps")
async def list_run_steps(
    thread_id: str,
    run_id: str,
    limit: int = Query(20, ge=1, le=100),
    order: str = Query("desc", regex="^(asc|desc)$"),
    after: Optional[str] = None,
    before: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns a list of run steps belonging to a run.
    
    Args:
        thread_id: The ID of the thread the run and run steps belong to
        run_id: The ID of the run the run steps belong to
        limit: Maximum number of run steps to return
        order: Sort order by created_at timestamp
        after: Cursor for pagination (run step ID)
        before: Cursor for pagination (run step ID)
    
    Returns:
        A list of run step objects
    """
    service = RunService(db)
    
    # Convert OpenAI style IDs to UUIDs
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
        run_uuid = uuid.UUID(run_id.replace("run_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found")
    
    steps = service.list_run_steps(
        run_id=run_uuid,
        thread_id=thread_uuid,
        limit=limit,
        order=order,
        after=after,
        before=before
    )
    
    # Format response according to OpenAI API
    return {
        "object": "list",
        "data": [step.to_dict() for step in steps],
        "first_id": steps[0].id if steps else None,
        "last_id": steps[-1].id if steps else None,
        "has_more": len(steps) == limit
    }


@router.get("/threads/{thread_id}/runs/{run_id}/steps/{step_id}")
async def retrieve_run_step(
    thread_id: str,
    run_id: str,
    step_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves a run step.
    
    Args:
        thread_id: The ID of the thread to which the run and run step belongs
        run_id: The ID of the run to which the run step belongs
        step_id: The ID of the run step to retrieve
    
    Returns:
        The run step object matching the specified ID
    """
    service = RunService(db)
    
    # Convert OpenAI style IDs to UUIDs
    try:
        thread_uuid = uuid.UUID(thread_id.replace("thread_", "").replace("-", ""))
        run_uuid = uuid.UUID(run_id.replace("run_", "").replace("-", ""))
        step_uuid = uuid.UUID(step_id.replace("step_", "").replace("-", ""))
    except ValueError:
        raise HTTPException(status_code=404, detail="Run step not found")
    
    step = service.get_run_step(step_uuid, run_uuid, thread_uuid)
    if not step:
        raise HTTPException(status_code=404, detail="Run step not found")
    
    return step.to_dict()