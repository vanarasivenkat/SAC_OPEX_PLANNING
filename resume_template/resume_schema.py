"""
Resume data schema for CoolSnail Technologies standardized resume template.

Defines the JSON schema that candidate resume data must conform to,
and provides validation utilities.
"""

RESUME_SCHEMA = {
    "type": "object",
    "required": ["candidate_name", "email", "phone", "summary", "experience", "education"],
    "properties": {
        "candidate_name": {
            "type": "string",
            "description": "Full name of the candidate"
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "Contact email address"
        },
        "phone": {
            "type": "string",
            "description": "Contact phone number"
        },
        "location": {
            "type": "string",
            "description": "City, State or Country"
        },
        "linkedin": {
            "type": "string",
            "description": "LinkedIn profile URL"
        },
        "portfolio": {
            "type": "string",
            "description": "Portfolio or personal website URL"
        },
        "summary": {
            "type": "string",
            "description": "Professional summary (2-4 sentences)"
        },
        "skills": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of key skills"
        },
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "company", "start_date"],
                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "location": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string", "default": "Present"},
                    "responsibilities": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "description": "Work experience entries, most recent first"
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["degree", "institution"],
                "properties": {
                    "degree": {"type": "string"},
                    "institution": {"type": "string"},
                    "location": {"type": "string"},
                    "graduation_date": {"type": "string"},
                    "gpa": {"type": "string"}
                }
            },
            "description": "Education entries, most recent first"
        },
        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "issuer": {"type": "string"},
                    "date": {"type": "string"}
                }
            },
            "description": "Professional certifications"
        },
        "languages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "language": {"type": "string"},
                    "proficiency": {"type": "string"}
                }
            },
            "description": "Language proficiencies"
        },
        "applied_position": {
            "type": "string",
            "description": "Position the candidate is applying for"
        }
    }
}


def validate_resume_data(data):
    """Validate candidate data against the resume schema.

    Args:
        data: Dictionary of candidate resume data.

    Returns:
        Tuple of (is_valid: bool, errors: list[str]).
    """
    from jsonschema import validate, ValidationError

    errors = []
    try:
        validate(instance=data, schema=RESUME_SCHEMA)
    except ValidationError as e:
        errors.append(str(e.message))

    return (len(errors) == 0, errors)
