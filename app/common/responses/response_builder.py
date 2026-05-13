from app.common.responses.standard_response import StandardResponse


def success_response(data=None, message="Success"):
    return StandardResponse(
        success=True,
        message=message,
        data=data,
    )
