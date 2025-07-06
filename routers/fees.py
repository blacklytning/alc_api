from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from models import PaymentCreate
from database.fees_repository import FeesRepository

router = APIRouter(prefix="/api", tags=["fees"])


@router.post("/fees/payment")
def create_payment(payment: PaymentCreate) -> Dict[str, Any]:
    """Create a new payment record"""
    try:
        payment_data = {
            "student_id": payment.student_id,
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "payment_method": payment.payment_method,
            "transaction_id": payment.transaction_id or "",
            "notes": payment.notes or "",
            "late_fee": payment.late_fee or 0,
            "handled_by": payment.handled_by or "System User",
        }

        payment_id = FeesRepository.create_payment(payment_data)

        return {
            "message": "Payment recorded successfully",
            "payment_id": payment_id,
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording payment: {str(e)}")


@router.get("/fees")
def get_fee_summary() -> Dict[str, Any]:
    """Get fee summary for all students"""
    try:
        fee_summary = FeesRepository.get_fee_summary()
        return {
            "fees": fee_summary,
            "total": len(fee_summary),
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fee summary: {str(e)}")


@router.get("/fees/payments")
def get_all_payments() -> Dict[str, Any]:
    """Get all payment records"""
    try:
        payments = FeesRepository.get_all_payments()
        return {
            "payments": payments,
            "total": len(payments),
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching payments: {str(e)}")


@router.get("/fees/student/{student_id}")
def get_student_fee_details(student_id: int) -> Dict[str, Any]:
    """Get detailed fee information for a specific student"""
    try:
        fee_details = FeesRepository.get_student_fee_details(student_id)
        if not fee_details:
            raise HTTPException(status_code=404, detail="Student not found")

        return {
            "data": fee_details,
            "status": "success",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching student fee details: {str(e)}")


@router.get("/fees/payments/student/{student_id}")
def get_student_payments(student_id: int) -> Dict[str, Any]:
    """Get all payments for a specific student"""
    try:
        payments = FeesRepository.get_payments_by_student(student_id)
        return {
            "payments": payments,
            "total": len(payments),
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching student payments: {str(e)}") 