from typing import Literal, Optional
from pydantic import BaseModel, Field


class EmailExtraction(BaseModel):

    sender_name: str = Field(
        description="Name of the person who sent the email",
    )

    sender_email: str = Field(
        description="Email of the person who sent the email, e.g. ryan@example.com",
    )

    category: Literal["meeting", "invoice", "support", "newsletter", "personal", "other"] = Field(
                description="Primary purpose of the email",
            )

    urgency: Literal["low", "medium", "high"] = Field(
        description="How urgently the email needs a response",
    )

    meeting_requested: bool = Field(
        description="True if the sender is asking to schedule or attend a meeting",
    )

    deadline: Optional[str] = Field(
        default=None,
        description="Any deadline mentioned, in YYYY-MM-DD format. Null if no deadline is mentioned.",
    )

    action_items: list[str] = Field(
        default_factory=list,
        description="Concrete tasks the recipient is asked to do. Empty list if none."
    )