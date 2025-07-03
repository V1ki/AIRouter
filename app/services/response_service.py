import time
import uuid
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from app.models.response import Response as DBResponse, MessageItem as DBMessageItem
from app.services.model_service import ModelService


class ResponseService:

    @staticmethod
    def delete_response(
        db: Session,
        response_id: str,
    ):
        db.query(DBResponse).filter(DBResponse.id == response_id).delete()
        db.commit()

    @staticmethod
    def get_response(db: Session, response_id: str, include: list[str] = []):
        return db.query(DBResponse).filter(DBResponse.id == response_id).first()

    @staticmethod
    def get_response_input_items(
        db: Session,
        response_id: str,
        after: str = None,
        before: str = None,
        include: list[str] = [],
        limit: int = 10,
        order: str = "asc",
    ):
        resp = db.query(DBResponse).filter(DBResponse.id == response_id).first()
        if not resp:
            return []

        return resp.message_items

    @staticmethod
    def build_conversation_state(db: Session, previous_response: DBResponse):
        pass

    @staticmethod
    # https://platform.openai.com/docs/api-reference/responses/create
    async def handle_not_implements(db: Session, client: AsyncOpenAI, args: dict):

        input_value = args.get("input")
        if input_value is None:
            raise ValueError("input is required")

        # build conversation state
        previous_response_id = None
        if "previous_response_id" in args:
            previous_response_id = previous_response.previous_response_id

        msgs = []
        if "instructions" in args:
            msgs.append({"role": "system", "content": args["instructions"]})

        previous_msgs = []
        while previous_response_id is not None:
            previous_response = (
                db.query(DBResponse)
                .filter(DBResponse.id == previous_response_id)
                .first()
            )
            mesg_items = previous_response.message_items
            for item in mesg_items:
                previous_msgs.append({"role": item.role, "content": item.content})
            previous_response_id = previous_response.previous_response_id

        # reverse previous_msgs
        previous_msgs.reverse()

        # merge previous_msgs and msgs
        msgs.extend(previous_msgs)

        response_id = f"router_response_{uuid.uuid4()}"
        
        
        db_response = DBResponse(
            id=response_id,
            created_at=int(time.time()),
            instructions=args.get("instructions", None),
            max_output_tokens=args.get("max_tokens", None),
            parallel_tool_calls=args.get("parallel_tool_calls", True),
            previous_response_id=previous_response_id,
            reasoning=args.get("reasoning", None),  # 暂时没有用
            status="in_progress",
            temperature=args.get("temperature", 0.7),
            text=args.get("text", None),
            tool_choice=args.get("tool_choice", None),
            tools=args.get("tools", None),
            top_p=args.get("top_p", 1),
            truncation=args.get("truncation", None),
            user=args.get("user", None),
            model=args["model"],
            metadata=args.get("metadata", None)
        )
        db.add(db_response)
        db.commit()

        
        
        # if input is array
        if isinstance(input_value, list):
            for item in input_value:
                msgs.append({"role": item["role"], "content": item["content"]})
                # save to db
                db.add(
                    DBMessageItem(
                        role=item["role"],
                        content=item["content"],
                        response_id=response_id,
                    )
                )
            db.commit()
        elif isinstance(input_value, str):
            msgs.append({"role": "user", "content": input_value})
            db.add(
                DBMessageItem(
                    role="user",
                    content=input_value,
                    response_id=response_id,
                )
            )
            db.commit()
        else:
            raise ValueError("input must be an array or a string")

        print(msgs)
        tools = args.get("tools", None)
        if tools:
            tools = [{"type": "function", "function": tool} for tool in tools]

        completion_args = {
            "model": args["model"],
            "messages": msgs,
            "stream": False,
            "temperature": args.get("temperature", 0.7),
            "top_p": args.get("top_p", 1),
            "max_tokens": args.get("max_tokens", 1000),
            "parallel_tool_calls": args.get("parallel_tool_calls", True),
            "response_format": args.get("text", None),
            "tools": tools,
            "tool_choice": args.get("tool_choice", None),
            "metadata": args.get("metadata", None),
        }
        try:
            print(completion_args)
            completion = await client.chat.completions.create(**completion_args)
            print(completion)
            completion_data = completion.model_dump()
            choices = completion_data.get("choices", [])

            db_response.status = "completed"
            db_response.usage = completion_data.get("usage", None)

            output_msgs = []
            for choice in choices:
                message = choice.get("message", {})
                msg_item = DBMessageItem(
                    role=message.get("role", "assistant"),
                    content=message.get("content", ""),
                    response_id=response_id,
                )
                db.add(msg_item)
                db.commit()
                
                output_msgs.append(
                    {
                        "id": msg_item.id,
                        "type": "message",
                        "status": "completed",
                        "role": msg_item.role,
                        "content": [
                            {
                                "type": "text",
                                "text": {
                                    "value": msg_item.content, # 目前只支持text
                                },
                            },
                        ],
                    }
                )
            db_response.output = output_msgs


        except Exception as e:
            print(e)
            raise e
            db_response.status = "failed"
            db_response.error = str(e)
            db_response.incomplete_details = {
                "reason": str(e),
            }

        db.commit()
        db.refresh(db_response)

        # Convert SQLAlchemy model to Pydantic model and then to dict
        resp = {
            "id": db_response.id,
            "created_at": db_response.created_at,
            "error": db_response.error,
            "incomplete_details": db_response.incomplete_details,
            "instructions": db_response.instructions,
            "max_output_tokens": db_response.max_output_tokens,
            "metadata": db_response.meta_data,
            "model": db_response.model,
            "output": db_response.output,
            "parallel_tool_calls": db_response.parallel_tool_calls,
            "previous_response_id": db_response.previous_response_id,
            "reasoning": db_response.reasoning,
            "status": db_response.status,
            "temperature": db_response.temperature,
            "text": db_response.text,
            "tool_choice": db_response.tool_choice,
            "tools": db_response.tools,
            "top_p": db_response.top_p,
            "truncation": db_response.truncation,
            "usage": db_response.usage,
            "user": db_response.user
        }
        return resp
