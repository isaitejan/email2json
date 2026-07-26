import re
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


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
        description=(
            "Classify how urgent the email is. Apply these rules in order and stop at the first match:\n"
            "1. high — the email uses explicit urgency language such as: urgent, ASAP, immediately, "
            "critical, emergency, blocker, EOD, or out of SLA.\n"
            "2. medium — no urgency words, BUT the recipient is asked to do something, or a deadline is mentioned.\n"
            "3. low — nothing is asked of the recipient and there is no deadline."
        ),
    )

    meeting_requested: bool = Field(
        description="True if the sender is asking to schedule or attend a meeting",
    )

    deadline: Optional[str] = Field(
        description="Any deadline mentioned, in YYYY-MM-DD format. Null if no deadline is mentioned.",
    )

    action_items: list[str] = Field(
        description="Concrete tasks the recipient is asked to do. Each list item must be exactly one task - split "
                    "compound requests like 'send X and sign Y' into two separate items. Empty list if none."
    )

    @field_validator("sender_email")
    @classmethod
    def check_email_format(cls, value):
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError(f"'{value}' is not a valid email address")
        return value

    @field_validator("deadline")
    @classmethod
    def check_date_format(cls, value):
        if value is None:
            return value

        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError(f"deadline '{value}' must be in YYYY-MM-DD format")
        return value

    @field_validator("action_items")
    @classmethod
    def check_action_items(cls, value):
        for item in value:
            if len(item.split()) < 2:
                raise ValueError(f"action item '{item}' is too short - each item must be a full task description, not a name or single word")
        return value
