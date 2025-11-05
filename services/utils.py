from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

def get_response(
    status_code=HTTP_200_OK,
    message="Request has been processed successfully.",
    is_success=False,
    data=None,
    errors=None,
):
    return Response(
        {
            "status": is_success,
            "message": message,
            "data": data,
            "errors": errors,
        },
        status=status_code,
    )
