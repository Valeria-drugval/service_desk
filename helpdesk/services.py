from .models import Request, RequestStatusLog

class RequestService:
    # Разрешенные переходы (Конечный автомат)
    ALLOWED_TRANSITIONS = {
        Request.Status.NEW: [Request.Status.ACCEPTED],
        Request.Status.ACCEPTED: [Request.Status.IN_PROGRESS],
        Request.Status.IN_PROGRESS: [Request.Status.COMPLETED],
        Request.Status.COMPLETED: [Request.Status.CLOSED],
        Request.Status.CLOSED: [], 
    }

    @staticmethod
    def change_status(request: Request, new_status: str, user, comment: str = "") -> bool:
        old_status = request.status
        
        if new_status not in RequestService.ALLOWED_TRANSITIONS.get(old_status, []):
            return False

        request.status = new_status
        
        if new_status == Request.Status.IN_PROGRESS and not request.assignee:
            request.assignee = user
            
        request.save(update_fields=["status", "assignee", "updated_at"])
        
        RequestStatusLog.objects.create(
            request=request,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
            comment=comment
        )
        return True