from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta

from app.agents.models import (
    Run, RunStatus, RunStep, RunStepType, RunStepStatus,
    Assistant, Thread, Message, MessageRole
)
from app.agents.services.assistant_service import AssistantService
from app.agents.services.thread_service import ThreadService
from app.agents.services.message_service import MessageService


class RunService:
    def __init__(self, db: Session):
        self.db = db
        self.assistant_service = AssistantService(db)
        self.thread_service = ThreadService(db)
        self.message_service = MessageService(db)
    
    def create_run(
        self,
        thread_id: uuid.UUID,
        assistant_id: uuid.UUID,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        metadata: Dict[str, Any] = None,
        temperature: Optional[float] = None,
        max_prompt_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None
    ) -> Optional[Run]:
        """Create a new run."""
        # Verify thread and assistant exist
        thread = self.thread_service.get_thread(thread_id)
        assistant = self.assistant_service.get_assistant(assistant_id)
        
        if not thread or not assistant:
            return None
        
        # Use assistant's model if not specified
        if not model:
            model = assistant.model
        
        # Use assistant's instructions if not overridden
        if not instructions:
            instructions = assistant.instructions
        
        # Use assistant's tools if not overridden
        if tools is None:
            tools = assistant.tools
        
        run = Run(
            thread_id=thread_id,
            assistant_id=assistant_id,
            model=model,
            instructions=instructions,
            tools=tools,
            metadata=metadata or {},
            temperature=temperature,
            max_prompt_tokens=max_prompt_tokens,
            max_completion_tokens=max_completion_tokens,
            expires_at=datetime.utcnow() + timedelta(minutes=10),  # Default 10 minute expiry
            provider_id=assistant.provider_id
        )
        
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        
        return run
    
    def get_run(
        self,
        run_id: uuid.UUID,
        thread_id: uuid.UUID
    ) -> Optional[Run]:
        """Get a run by ID and thread ID."""
        return self.db.query(Run).filter(
            and_(
                Run.id == run_id,
                Run.thread_id == thread_id
            )
        ).first()
    
    def list_runs(
        self,
        thread_id: uuid.UUID,
        limit: int = 20,
        order: str = "desc",
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> List[Run]:
        """List runs in a thread with pagination."""
        query = self.db.query(Run).filter(Run.thread_id == thread_id)
        
        # Apply cursor-based pagination
        if after:
            try:
                after_uuid = uuid.UUID(after.replace("run_", "").replace("-", ""))
                after_run = self.db.query(Run).filter(
                    Run.id == after_uuid
                ).first()
                if after_run:
                    if order == "desc":
                        query = query.filter(Run.created_at < after_run.created_at)
                    else:
                        query = query.filter(Run.created_at > after_run.created_at)
            except ValueError:
                pass
        
        if before:
            try:
                before_uuid = uuid.UUID(before.replace("run_", "").replace("-", ""))
                before_run = self.db.query(Run).filter(
                    Run.id == before_uuid
                ).first()
                if before_run:
                    if order == "desc":
                        query = query.filter(Run.created_at > before_run.created_at)
                    else:
                        query = query.filter(Run.created_at < before_run.created_at)
            except ValueError:
                pass
        
        # Apply ordering
        if order == "desc":
            query = query.order_by(desc(Run.created_at))
        else:
            query = query.order_by(asc(Run.created_at))
        
        # Apply limit
        return query.limit(limit).all()
    
    def update_run(
        self,
        run_id: uuid.UUID,
        thread_id: uuid.UUID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Run]:
        """Update a run's metadata."""
        run = self.get_run(run_id, thread_id)
        if not run:
            return None
        
        if metadata is not None:
            run.metadata = metadata
        
        self.db.commit()
        self.db.refresh(run)
        
        return run
    
    def cancel_run(
        self,
        run_id: uuid.UUID,
        thread_id: uuid.UUID
    ) -> Optional[Run]:
        """Cancel a run that is in progress."""
        run = self.get_run(run_id, thread_id)
        if not run:
            return None
        
        # Can only cancel runs that are in progress
        if run.status not in [RunStatus.QUEUED, RunStatus.IN_PROGRESS, RunStatus.REQUIRES_ACTION]:
            return None
        
        run.status = RunStatus.CANCELLING
        run.cancelled_at = datetime.utcnow()
        
        self.db.commit()
        
        # TODO: Implement actual cancellation logic
        # For now, immediately mark as cancelled
        run.status = RunStatus.CANCELLED
        
        self.db.commit()
        self.db.refresh(run)
        
        return run
    
    def get_run_step(
        self,
        step_id: uuid.UUID,
        run_id: uuid.UUID,
        thread_id: uuid.UUID
    ) -> Optional[RunStep]:
        """Get a run step by ID."""
        return self.db.query(RunStep).filter(
            and_(
                RunStep.id == step_id,
                RunStep.run_id == run_id,
                RunStep.thread_id == thread_id
            )
        ).first()
    
    def list_run_steps(
        self,
        run_id: uuid.UUID,
        thread_id: uuid.UUID,
        limit: int = 20,
        order: str = "desc",
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> List[RunStep]:
        """List steps in a run with pagination."""
        query = self.db.query(RunStep).filter(
            and_(
                RunStep.run_id == run_id,
                RunStep.thread_id == thread_id
            )
        )
        
        # Apply cursor-based pagination
        if after:
            try:
                after_uuid = uuid.UUID(after.replace("step_", "").replace("-", ""))
                after_step = self.db.query(RunStep).filter(
                    RunStep.id == after_uuid
                ).first()
                if after_step:
                    if order == "desc":
                        query = query.filter(RunStep.created_at < after_step.created_at)
                    else:
                        query = query.filter(RunStep.created_at > after_step.created_at)
            except ValueError:
                pass
        
        if before:
            try:
                before_uuid = uuid.UUID(before.replace("step_", "").replace("-", ""))
                before_step = self.db.query(RunStep).filter(
                    RunStep.id == before_uuid
                ).first()
                if before_step:
                    if order == "desc":
                        query = query.filter(RunStep.created_at > before_step.created_at)
                    else:
                        query = query.filter(RunStep.created_at < before_step.created_at)
            except ValueError:
                pass
        
        # Apply ordering
        if order == "desc":
            query = query.order_by(desc(RunStep.created_at))
        else:
            query = query.order_by(asc(RunStep.created_at))
        
        # Apply limit
        return query.limit(limit).all()
    
    async def process_run(self, run_id: uuid.UUID):
        """
        Process a run asynchronously.
        This is a placeholder for the actual run processing logic.
        """
        # TODO: Implement actual run processing
        # This would involve:
        # 1. Retrieving thread messages
        # 2. Calling the appropriate AI model
        # 3. Creating response messages
        # 4. Creating run steps
        # 5. Updating run status
        pass